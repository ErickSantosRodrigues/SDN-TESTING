from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet


class BlockH1(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(BlockH1, self).__init__(*args, **kwargs)
        self.h2_communicating = False

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if in_port == 2:  # h2 is communicating
            self.h2_communicating = True

        if in_port == 1:  # h1 is communicating
            if self.h2_communicating:
                # Drop h1's packet
                return
            else:
                # Forward h1's packet normally
                actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
                out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                          in_port=in_port, actions=actions, data=msg.data)
                datapath.send_msg(out)
        elif in_port in (2, 3):  # h2 or h3 is communicating
            actions = [parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                      in_port=in_port, actions=actions, data=msg.data)
            datapath.send_msg(out)

