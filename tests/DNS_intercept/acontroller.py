from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types, ipv4, udp
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
        # add a meter entry with a rate limit of 100 Mbs
        meter_mod = parser.OFPMeterMod(datapath=datapath,
                                        command=ofproto.OFPMC_ADD,
                                        flags=ofproto.OFPMF_KBPS, meter_id=1,
                                        bands=[parser.OFPMeterBandDrop(rate=100_000,
                                                                        burst_size=0)])
        datapath.send_msg(meter_mod)
        # add a second meter entry with a rate limit of 100 Mbs
        meter_mod = parser.OFPMeterMod(datapath=datapath,
                                        command=ofproto.OFPMC_ADD,
                                        flags=ofproto.OFPMF_KBPS, meter_id=2,
                                        bands=[parser.OFPMeterBandDrop(rate=100_000,
                                                                        burst_size=0)])
        datapath.send_msg(meter_mod)
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        # allow all communication from port 1
        match = parser.OFPMatch(in_port=1)
        actions = [parser.OFPActionOutput(ofproto.OFPP_IN_PORT), parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
        self.add_flow(datapath, 1, match, actions)

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

        if eth.ethertype == ether_types.ETH_TYPE_IP:
            ipv4_pkt = pkt.get_protocol(ipv4.ipv4)
            self.logger.info("IP Packet: %s", ipv4_pkt)
            if ipv4_pkt.proto == 17:  # Check if the protocol is UDP 
                udp_pkt = pkt.get_protocol(udp.udp)
                self.logger.info("UDP Packet: %s", udp_pkt)
                if udp_pkt.dst_port == 53:  # Check if the destination port is 53 (DNS)
                    dns_data = dpkt.dns.DNS(udp_pkt.data)
                    self.logger.info("DNS Packet: %s", dns_data)
                    if dns_data.qr == dpkt.dns.DNS_Q:   # Check if it is a DNS query 
                        self.logger.info("DNS Query: %s", dns_data)

