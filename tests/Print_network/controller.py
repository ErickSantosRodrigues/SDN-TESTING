from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
import networkx as nx

class NetworkGraph(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(NetworkGraph, self).__init__(*args, **kwargs)
        self.network_graph = nx.Graph()

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
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        # allow all communication from port 1
        match = parser.OFPMatch(in_port=1)
        actions = [parser.OFPActionOutput(ofproto.OFPP_IN_PORT), parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
        self.add_flow(datapath, 1, match, actions)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto

        src = msg.match['eth_src']
        dst = msg.match['eth_dst']

        # Update the network graph
        self.network_graph.add_edge(src, dst)

        # Print the network graph
        self.print_network_graph()

    def print_network_graph(self):
        for edge in self.network_graph.edges():
            self.logger.info("Edge: %s %s", edge[0], edge[1])

