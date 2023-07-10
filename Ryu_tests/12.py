   from ryu.base import app_manager
   from ryu.controller import ofp_event
   from ryu.controller.handler import MAIN_DISPATCHER
   from ryu.controller.handler import set_ev_cls
   from ryu.lib.packet import ethernet
   from ryu.lib.packet import packet
   from ryu.ofproto import ofproto_v1_3

   class MyController(app_manager.RyuApp):
       OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

       def __init__(self, *args, **kwargs):
           super(MyController, self).__init__(*args, **kwargs)
           self.mac_to_port = {}

       @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
       def packet_in_handler(self, ev):
           msg = ev.msg
           datapath = msg.datapath
           ofproto = datapath.ofproto
           parser = datapath.ofproto_parser

           pkt = packet.Packet(msg.data)
           eth = pkt.get_protocol(ethernet.ethernet)

           # Learn MAC address to port mapping
           self.mac_to_port[eth.src] = msg.in_port

           # Forward the packet to the appropriate port
           if eth.dst in self.mac_to_port:
               out_port = self.mac_to_port[eth.dst]
           else:
               out_port = ofproto.OFPP_FLOOD

           actions = [parser.OFPActionOutput(out_port)]

           # Install a flow entry for future packets
           if out_port != ofproto.OFPP_FLOOD:
               match = parser.OFPMatch(eth_dst=eth.dst)
               instructions = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
               flow_mod = parser.OFPFlowMod(datapath=datapath, match=match, instructions=instructions)
               datapath.send_msg(flow_mod)

           # Send the packet out
           data = None
           if msg.buffer_id == ofproto.OFP_NO_BUFFER:
               data = msg.data

           out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=msg.in_port,
                                     actions=actions, data=data)
           datapath.send_msg(out)


        #add the other functions
