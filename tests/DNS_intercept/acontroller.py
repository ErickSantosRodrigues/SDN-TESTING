from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3, ether, inet
from ryu.lib.packet import packet, ethernet, ether_types, ipv4, udp
import array
import dpkt


class DNSApp(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(DNSApp, self).__init__(*args, **kwargs)
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        # allow all communication from port 1
        match = parser.OFPMatch(in_port=1)
        actions = [parser.OFPActionOutput(ofproto.OFPP_IN_PORT), parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 1, match, actions)                                        
        match = parser.OFPMatch(
            eth_type=0x0800,  # IP
            ip_proto=17,  # UDP
            udp_dst=53  # DNS
        )
        actions = [parser.OFPActionOutput(ofproto.OFPP_IN_PORT), parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                                                    ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 2, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None, meter_id=None, command=None, idle_timeout=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        if actions == []:
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_CLEAR_ACTIONS, [])]
        else:
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
        self.logger.info(f"Flow added: {match} -> {actions}")

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        # OUR CODE	
        pkt_udp = pkt.get_protocol(udp.udp)
        dns = 0 
        # fr = open('blacklist.txt', 'r') 
        fw = open('./monitor.txt', 'a')
        if pkt_udp:
            if pkt_udp.src_port == 53 or pkt_udp.dst_port == 53:
                # *** Use dpkt to parse UDP DNS data:
                try:
                    dns = dpkt.dns.DNS(pkt.protocols[-1])
                except:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    self.logger.error("DNS extraction failed "
                                      "Exception %s, %s, %s",
                                      exc_type, exc_value, exc_traceback)
        if dns:
            for qname in dns.qd:
                print(qname.name)
                src_mac = eth.src 
                timestamp = time.strftime('%d-%m-%Y %H-%M-%S ') 
                fileStr = timestamp + src_mac + ' ' + qname.name + '\n' 
                fw.write(fileStr)
                fw.close()
                # return
                # print(eth.src + " " + dns.qd)

