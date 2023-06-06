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
        self.h2_is_communicating = False

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        #add a meter entry with a rate limit of 1000 kbps
        meter_mod = parser.OFPMeterMod(datapath=datapath, command=ofproto.OFPMC_ADD,
                                      flags=ofproto.OFPMF_KBPS, meter_id=1,
                                      bands=[parser.OFPMeterBandDrop(rate=1000, burst_size=0)])

        datapath.send_msg(meter_mod)
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        match = parser.OFPMatch(in_port=4)
        actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
        self.add_flow(datapath, 2, match, actions, meter_id=1)
        
        match = parser.OFPMatch(in_port=2)
        actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
        self.add_flow(datapath, 3, match, actions, meter_id=1)

        match = parser.OFPMatch(in_port=3)
        actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
        self.add_flow(datapath, 0, match, actions,meter_id=1)

        match = parser.OFPMatch(in_port=1)
        actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
        self.add_flow(datapath, 0, match, actions, meter_id=1)



   
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
 
        # # If host H2 is communicating, create a flow entry to block host H1
        # self.h2_is_communicating = True if in_port == 2 else False
        # match = parser.OFPMatch(in_port=3)
        # actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
        #                                  ofproto.OFPCML_NO_BUFFER)]
        # self.add_flow(datapath, 1, match, actions, meter_id=1, command=ofproto.OFPFC_DELETE)
        # if self.h2_is_communicating:
        #     match = parser.OFPMatch(in_port=3)
        #     actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
        #                                      ofproto.OFPCML_NO_BUFFER)]
        #     self.add_flow(datapath, 1, match, actions, meter_id=1)
        # else:
        #     # If host H2 is not communicating, remove the flow entry
        #     match = parser.OFPMatch(in_port=3)
        #     actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
        #     self.add_flow(datapath, 0, match, actions, meter_id=1)
        #
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        match = parser.OFPMatch(in_port=msg.match['in_port'])
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions),
                parser.OFPInstructionMeter(meter_id=1)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=1, match=match, instructions=inst)
        datapath.send_msg(mod)


        # dpid = format(datapath.id, "d").zfill(16)
        # self.mac_to_port.setdefault(dpid, {})
        # self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)
        #
        # # learn a mac address to avoid FLOOD next time.
        # self.mac_to_port[dpid][src] = in_port
        # if dst in self.mac_to_port[dpid]:
        #     out_port = self.mac_to_port[dpid][dst]
        # else:
        #     out_port = ofproto.OFPP_FLOOD

    # def print_flow_table(self, datapath):
    #     ofproto = datapath.ofproto_v1_3
    #     parser = datapath.ofproto_parser
    #
    #     # Prepare and send the flow stats request message
    #     req = parser.OFPFlowStatsRequest(datapath)
    #     datapath.send_msg(req)                        
    #
    # @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    # def flow_stats_reply_handler(self, ev):
    #     flows = []
    #     for stat in ev.msg.body:
    #        flows.append({
    #             'priority': stat.priority,
    #             'match': stat.match,
    #             'actions': stat.instructions[0].Actions
    #             })
    #     # Print the flow table 
    #     print("Flow Table:")
    #     for flow in flows:
    #         print("Priority: %s" % flow['priority'])
    #         print("Match: %s" % flow['match'])
    #         print("Actions: %s" % flow['actions'])
    #         print("")
    #
    # 
    # @set_ev_cls(stplib.EventTopologyChange, MAIN_DISPATCHER)
    # def _topology_change_handler(self, ev):
    #     dp = ev.dp
    #     dpid_str = dpid_lib.dpid_to_str(dp.id)
    #     msg = 'Receive topology change event. Flush MAC table.'
    #     self.logger.debug("[dpid=%s] %s", dpid_str, msg)
    #
    #     if dp.id in self.mac_to_port:
    #         self.delete_flow(dp)
    #         del self.mac_to_port[dp.id]
    #
    # @set_ev_cls(stplib.EventPortStateChange, MAIN_DISPATCHER)
    # def _port_state_change_handler(self, ev):
    #     dpid_str = dpid_lib.dpid_to_str(ev.dp.id)
    #     of_state = {stplib.PORT_STATE_DISABLE: 'DISABLE',
    #                 stplib.PORT_STATE_BLOCK: 'BLOCK',
    #                 stplib.PORT_STATE_LISTEN: 'LISTEN',
    #                 stplib.PORT_STATE_LEARN: 'LEARN',
    #                 stplib.PORT_STATE_FORWARD: 'FORWARD'}
    #     self.logger.debug("[dpid=%s][port=%d] state=%s",
    #                       dpid_str, ev.port_no, of_state[ev.port_state])
