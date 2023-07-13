from ryu.base import app_manager
from ryu.controller import ofp_event, handler
from ryu.controller.handler import set_ev_cls, CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types
from ryu.lib import dpid as dpid_lib


class Controller_drop_h2(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Controller_drop_h2, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        # add a meter entry with a rate limit of 100 Mbs
        meter_mod = parser.OFPMeterMod(datapath=datapath,
                                        command=ofproto.OFPMC_ADD,
                                        flags=ofproto.OFPMF_KBPS, meter_id=1,
                                        bands=[parser.OFPMeterBandDrop(rate=100_000,
                                                                        burst_size=0)])
        datapath.send_msg(meter_mod)
        # add a second meter entry with a rate limit of 100 Mbs
        meter_mod = parser.OFPMeterMod(datapath=datapath,
                                        command=ofproto.OFPMC_ADD,
                                        flags=ofproto.OFPMF_KBPS, meter_id=2,
                                        bands=[parser.OFPMeterBandDrop(rate=100_000,
                                                                        burst_size=0)])
        datapath.send_msg(meter_mod)
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

        match = parser.OFPMatch(in_port=1)
        actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
        self.add_flow(datapath, 1, match, actions, meter_id=1)

        match = parser.OFPMatch(in_port=2)
        actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
        self.add_flow(datapath, 1, match, actions, meter_id=2)

        match = parser.OFPMatch(in_port=3)
        actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL),
                   parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
        self.add_flow(datapath, 1, match, actions, meter_id=1)

        self.logger.info(f"Switch {dpid_lib.dpid_to_str(datapath.id)} ready")

    def add_flow(self, datapath, priority, match, actions, buffer_id=None, meter_id=None, command=None, idle_timeout=0):
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
                                    instructions=inst, command=command, idle_timeout=idle_timeout)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst, command=command, idle_timeout=idle_timeout)
        datapath.send_msg(mod)
        # if command == ofproto.OFPFC_ADD:
        #     self.logger.info(f"Flow added: {match} -> {actions}")
        # elif command == ofproto.OFPFC_REMOVE:
        #     self.logger.info(f"Flow removed: {match} -> {actions}")
        # elif command == ofproto.OFPFC_MODIFY:
        #     self.logger.info(f"Flow modified: {match} -> {actions}")

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if msg.match['in_port'] == 3:
            parser = datapath.ofproto_parser
            match = parser.OFPMatch(in_port=2)
            # Drop the packets from h2
            actions = []
            self.add_flow(datapath, 2, match, actions, idle_timeout=1)

    @handler.set_ev_cls(ofp_event.EventOFPFlowRemoved, MAIN_DISPATCHER)
    def flow_removed_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath 
        ofproto = datapath.ofproto
        match = msg.match
        self.logger.info(f"Flow Removed: {match}")
