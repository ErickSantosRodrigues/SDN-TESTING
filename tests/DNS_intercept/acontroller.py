from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
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
        dp = msg.datapath
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        self.logger.info(f"Packet in: {eth.src} -> {eth.dst}")
        pkt = packet.Packet(array.array('B', ev.msg.data))
        raw_pkt = bytes(pkt.data)

        eth_pkt = dpkt.ethernet.Ethernet(raw_pkt)
        ip_pkt = eth_pkt.data
    
        src_ip = ip_pkt.src
        dst_ip = ip_pkt.dst
        pkt = packet.Packet(array.array('B', ev.msg.data))
        eth = pkt.get_protocol(ethernet.ethernet)
        
        if not eth:
            return
        
        if eth.ethertype == ether.ETH_TYPE_IP:
            ip = pkt.get_protocol(ipv4.ipv4)
            
            if ip.proto == inet.IPPROTO_UDP:
                udp_packet = pkt.get_protocol(udp.udp)
                
                if udp_packet.dport == 53:
                    self.parse_dns_data(udp_packet.data)
    
    def parse_dns_data(self, data):
        dns = dpkt.dns.DNS(data)
        for question in dns.qd:
            print(question.name)

        # self.logger.info(f"Packet: pkt {pkt.get_protocol(ethernet.ethernet)}, IP {pkt.get_protocol(ipv4.ipv4)}, UDP {pkt.get_protocol(udp.udp)}")
        # if eth.ethertype == ether_types.ETH_TYPE_IP:
        #     ipv4_pkt = pkt.get_protocol(ipv4.ipv4)
        #     self.logger.info(f"IP Packet: {ipv4_pkt}")
        #     if ipv4_pkt.proto == 17:  # Check if the protocol is UDP 
        #         udp_pkt = pkt.get_protocol(udp.udp)
        #         self.logger.info(f"UDP Packet: {udp_pkt}")
        #         if udp_pkt.dst_port == 53:  # Check if the destination port is 53 (DNS)
        #             dns_data = dpkt.dns.DNS(udp_pkt.data)
        #             self.logger.info(f"DNS Packet: {dns_data}")
        #             if dns_data.qr == dpkt.dns.DNS_Q:   # Check if it is a DNS query 
        #                 self.logger.info(f"DNS Query: {dns_data}")

