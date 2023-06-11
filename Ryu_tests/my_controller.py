from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls, CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types
from ryu.lib import dpid as dpid_lib
# from ryu.lib import stplib

class my_controller(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    # _CONTEXTS = {'stplib': stplib.Stp}
    H1_MAC='00:00:00:00:00:01'
    H2_MAC='00:00:00:00:00:02'
    H3_MAC='00:00:00:00:00:03'
    H4_MAC='00:00:00:00:00:04'

    def __init__(self, *args, **kwargs):
        super(my_controller, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        #add a meter entry with a rate limit of 1000 kbps
        meter_mod = parser.OFPMeterMod(datapath=datapath, command=ofproto.OFPMC_ADD,
                                      flags=ofproto.OFPMF_KBPS, meter_id=1,
                                      bands=[parser.OFPMeterBandDrop(rate=300, burst_size=0)])
        datapath.send_msg(meter_mod)
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

        match = parser.OFPMatch(eth_src=self.H4_MAC)
        actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
        self.add_flow(datapath, 2, match, actions, meter_id=1)
        
        match = parser.OFPMatch(eth_src=self.H2_MAC)
        actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
        self.add_flow(datapath, 3, match, actions, meter_id=1)

        match = parser.OFPMatch(eth_src=self.H3_MAC)
        actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
        self.add_flow(datapath, 1, match, actions,meter_id=1)

        match = parser.OFPMatch(eth_src=self.H1_MAC)
        actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
        self.add_flow(datapath, 1, match, actions, meter_id=1)

        # match = parser.OFPMatch(in_port=msg.match['in_port'])
        # actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
        # inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions),
        #         parser.OFPInstructionMeter(meter_id=1)]
        # mod = parser.OFPFlowMod(datapath=datapath, priority=1, match=match, instructions=inst)
        # datapath.send_msg(mod)
 
   
    def add_flow(self, datapath, priority, match, actions, buffer_id=None, meter_id=None, command=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if meter_id is not None:
            inst.append(parser.OFPInstructionMeter(meter_id=meter_id))

        if command is None:
            command = ofproto.OFPFC_ADD
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst, command=command)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst, command=command)
        datapath.send_msg(mod)
        # Add a barrier request to ensure the flow modification is executed before continuing
        barrier_req = parser.OFPBarrierRequest(datapath)
        datapath.send_msg(barrier_req)
    

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src



