from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib import dpid as dpid_lib
from ryu.lib import stplib
from ryu.app import simple_switch_13

class SimpleSwitch13(simple_switch_13.SimpleSwitch13):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'stplib': stplib.Stp}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.stp = kwargs['stplib']
        self.stp.set_config({
            dpid_lib.str_to_dpid('0000000000000001'): {'bridge': {'priority': 0x8000}},
            dpid_lib.str_to_dpid('0000000000000002'): {'bridge': {'priority': 0x9000}},
            dpid_lib.str_to_dpid('0000000000000003'): {'bridge': {'priority': 0xa000}},
            dpid_lib.str_to_dpid('0000000000000004'): {'bridge': {'priority': 0xb000}}
        })
        self.h2_communicating = True

    def delete_flow(self, datapath):
        ofproto, parser = datapath.ofproto, datapath.ofproto_parser
        for dst in self.mac_to_port[datapath.id].keys():
            match = parser.OFPMatch(eth_dst=dst)
            mod = parser.OFPFlowMod(datapath=datapath, command=ofproto.OFPFC_DELETE,
                                    out_port=ofproto.OFPP_ANY, out_group=ofproto.OFPG_ANY,
                                    priority=1, match=match)
            datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Install a rule to forward packets from h2 and h3 normally
        match = parser.OFPMatch(in_port=2)
        
        actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
        self.add_flow(datapath, 10, match, actions)

        match = parser.OFPMatch(in_port=3)
        actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
        self.add_flow(datapath, 10, match, actions)

        # Install a rule to drop packets from h1
        match = parser.OFPMatch(in_port=1)
        actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
        self.add_flow(datapath, 1, match, actions)

    @set_ev_cls(stplib.EventPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg, datapath = ev.msg, ev.msg.datapath
        ofproto, parser = datapath.ofproto, datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        dst, src = eth.dst, eth.src

        self.mac_to_port.setdefault(datapath.id, {})
        self.logger.info(f"packet in {datapath.id} {src} {dst} {in_port}")

        self.mac_to_port[datapath.id][src] = in_port
        out_port = self.mac_to_port[datapath.id].get(dst, ofproto.OFPP_FLOOD)
        actions = [parser.OFPActionOutput(out_port)]
        self.switch_features_handler(ev=ev)
        # if out_port != ofproto.OFPP_FLOOD:
        #     match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
        #     self.add_flow(datapath=datapath, priority=1, match=match, actions=actions)

        data = None if msg.buffer_id == ofproto.OFP_NO_BUFFER else msg.data 
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
