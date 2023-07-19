from ryu.ofproto import ofproto_v1_3, ofproto_v1_3_parser
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.base import app_manager


class QueueController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(QueueController, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures , CONFIG_DISPATCHER)
    def switch_features_handler(self , ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto 
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS , actions)]
        mod = datapath.ofproto_parser.OFPFlowMod(
                datapath=datapath, match=match, cookie=0,
                command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                priority=0, instructions=inst)
        datapath.send_msg(mod)
        port_1 = 3
        queue_1 = parser.OFPActionSetQueue(0)
        actions_1 = [queue_1, parser.OFPActionOutput(port_1)]

        watch_port = ofproto_v1_3.OFPP_ANY
        watch_group = ofproto_v1_3.OFPQ_ALL
        weight_1 = 1
        buckets = [parser.OFPBucket(weight_1, watch_port, watch_group, actions_1)]
        group_id = 50
        req = parser.OFPGroupMod(
            datapath, datapath.ofproto.OFPFC_ADD,
            datapath.ofproto.OFPGT_SELECT, group_id, buckets)
        datapath.send_msg(req)
        
        match = parser.OFPMatch(in_port=1)
        actions = [datapath.ofproto_parser.OFPActionGroup(50)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=3, instructions=inst)
        datapath.send_msg(mod)
        
