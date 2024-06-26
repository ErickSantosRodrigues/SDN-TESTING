import ryu.base.app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.lib import packet
from ryu.lib.packet import udp, packet
from ryu.ofproto import ofproto_v1_3
import scapy.all as scapy


class DNSSpy(ryu.base.app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

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

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # get the raw data from the packet arrival event
        raw_data = ev.msg.data
        # convert the raw data to a packet object
        
        packet = packet.Packet(raw_data)

        # check if the packet is DNS
        udp_packet = packet.get_protocol(udp.udp)
        if udp_packet and (udp_packet.dst_port == 53 or udp_packet.src_port == 53):
            # this is a DNS packet
            self._handle_dns(packet)

    def _handle_dns(self, packet):
        # convert packet to byte string and feed it to Scapy's Ether constructor
        raw_packet = ryu.lib.packet.packet.Packet.__bytes__(packet)
        scapy_packet = scapy.layers.l2.Ether(raw_packet)
        dns_section = scapy_packet['scapy.layers.dns.DNS']
        print(dns_section.show())

