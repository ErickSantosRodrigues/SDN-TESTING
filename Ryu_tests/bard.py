import ryu.app.simple_switch_13 as simple_switch


class MySwitch(simple_switch.SimpleSwitch):
    def __init__(self, **kwargs):
        super(MySwitch, self).__init__(**kwargs)
        ofproto = self.dp.ofproto
        parser = self.dp.ofproto_parser
        ofp_match = parser.OFPMatch
        ofp_action = parser.OFPAction
        # Create two queues
        self.queue1 = self.dp.queue_create('queue1')
        self.queue2 = self.dp.queue_create('queue2')

        # Set the default queue for packets
        self.dp.set_default_queue(self.queue1)

        # Add flow entries to forward packets to the appropriate queue
        self.add_flow(
            priority=1,
            match=ofp_match.OFPMatch(src_port=1),
            actions=[ofp_action.OFPQueueAction(queue_id=self.queue1)]
        )
        self.add_flow(
            priority=1,
            match=ofp_match.OFPMatch(src_port=2),
            actions=[ofp_action.OFPQueueAction(queue_id=self.queue2)]
        )


