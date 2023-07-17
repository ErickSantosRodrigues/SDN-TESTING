from ryu.ofproto import ofproto_v1_3, ofproto_v1_3_parser
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from ryu.base import app_manager


class QueueController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(QueueController, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER])
    def state_change_handler(self, ev):
        datapath = ev.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch(in_port=1)
        actions = [parser.OFPActionOutput(2)]
        bucket = ofproto_v1_3_parser.OFPBucket(weight=0, watch_port=ofproto_v1_3.OFPP_ANY,
                                                watch_group=ofproto_v1_3.OFPG_ANY, actions=actions)
        req = ofproto_v1_3_parser.OFPQueueGetConfigRequest(ev.datapath, 1)

        datapath.send_msg(req)

        ofproto_v1_3_parser.OFPQueueModify(ev.datapath, 1, 1, min_rate=1000)

        # create a queue with id=1, max_rate=1000 kbps
        prop = parser.OFPQueuePropMaxRate(ofproto.OFPQT_MIN_RATE, 100_000)

        # construct a flow_mod message and send it to the switch
        instructions = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        flow_mod = parser.OFPFlowMod(
            datapath=datapath,
            match=match,
            cookie=0,
            command=ofproto.OFPFC_ADD,
            idle_timeout=0,
            hard_timeout=0,
            priority=100,
            flags=ofproto.OFPFF_SEND_FLOW_REM,
            actions=actions
        )

        datapath.send_msg(flow_mod)

