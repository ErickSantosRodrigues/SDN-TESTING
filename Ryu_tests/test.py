from ryu.ofproto import ofproto_v1_3
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from ryu.base import app_manager


class QueueController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(QueueController, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER])
    def state_change_handler(self, ev):
        dp = ev.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser

        # create a queue with id=1, max_rate=1000 kbps
        prop = parser.OFPQueuePropMaxRate(ofp.OFPQT_MIN_RATE, 100_000)
        properties = [prop]
        req = parser.OFPQueueSetConfigRequest(dp, 1, properties)
        dp.send_msg(req)

        # create a flow entry with queue action
        match = parser.OFPMatch(in_port=1)
        actions = [parser.OFPActionQueue(1)]
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=dp, priority=0, match=match, instructions=inst)
        dp.send_msg(mod)
