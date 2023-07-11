from mininet.node import CPULimitedHost
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI


class Band_limit_Topo(Topo):
    def __init__(self, **opts):
        Topo.__init__(self, **opts)
        # Add hosts and switches
        h1 = self.addHost('h1', ip='10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.0.2')
        h3 = self.addHost('h3', ip='10.0.0.3')
        # Add switches
        s1 = self.addSwitch('s1', dpid='0000000000000001', protocols='OpenFlow13', cls=OVSSwitch)
        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)


def run():
    net = Mininet(topo=Band_limit_Topo(), host=CPULimitedHost, controller=RemoteController('c', '127.0.0.1', 6653, protocols="OpenFlow13"))
    net.start()
    h1, h2, h3 = net.hosts[0], net.hosts[1], net.hosts[2]
    net.pingAll()
    h1.cmd('''xterm -hold -T "h1_5002" -e "iperf3 -s --port 5002" -geometry 100x25+0+0 &''')
    h1.cmd('''xterm -hold -T "h1_5003" -e "iperf3 -s --port 5003" -geometry 100x25+625+0 &''')
    h2.cmd('''xterm -hold -T "h2" -e "iperf3 -c 10.0.0.1 --port 5002 -t 60 -i 60" -geometry 100x25+0+380 &''')
    h3.cmd('''xterm -hold -T "h3" -e "iperf3 -c 10.0.0.1 --port 5003 -t 60 -i 60" -geometry 100x25+625+380 &''')

if __name__ == '__main__':
    setLogLevel('info')
    run()