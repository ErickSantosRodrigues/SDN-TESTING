from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3 as odp

class MyController(app_manager.RyuApp):
    """Ryu App to manage open flow rules"""
    OFP_VERSIONS = [odp.OFP_VERSION] # We use OpenFlow ver 1.3

    def __init__(self, *args, **kwargs):
        super(MyController, self).__init__(*args, **kwargs)
        self.client1_streaming = False
        self.client1_mac = "00:00:00:00:00:01" # Substitute with actual MAC
        self.client2_mac = "00:00:00:00:00:02" # Substitute with actual MAC

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, event):
        """Handle packet-in events"""
        msg = event.msg
        pkt = packet.Packet(msg.data)

        eth = pkt.get_protocol(ethernet.ethernet)
        if eth.ethertype == ether_types.ETH_TYPE_IP:
            ip = pkt.get_protocol(ipv4.ipv4)

            if self.client1_streaming:
                # If client-1 is in streaming mode, we drop packets from client-2
                if eth.src == self.client2_mac:
                    self.add_flow(event, priority=1, actions=[])
                else:
                    actions = [parser.OFPActionOutput(ofp.OFPP_FLOOD)]
                    self.add_flow(event, actions=actions)
            else:
                # Check if client 1 is streaming
                if eth.src == self.client1_mac:
                    self.client1_streaming = True
                actions = [parser.OFPActionOutput(ofp.OFPP_FLOOD)]
                self.add_flow(event, actions=actions)

    def add_flow(self, event, priority, actions, buffer_id=None):
        """Adds a flow rule in switch"""
        ofproto = event.msg.datapath.ofproto
        parser = event.msg.datapath.ofproto_parser
        match = parser.OFPMatch()
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=event.msg.datapath,
                                    buffer_id=buffer_id,
                                    priority=priority,
                                    match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=event.msg.datapath,
                                    priority=priority,
                                    match=match,
                                    instructions=inst)
        event.msg.datapath.send_msg(mod)

