from mininet.node import CPULimitedHost
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from time import sleep


class SimplePktSwitch(Topo):
    """Simple topology example."""
    def __init__(self, **opts):
        """Create custom topo."""
# Initialize topology
# It uses the constructor for the Topo class
        super(SimplePktSwitch, self).__init__(**opts)
# Add hosts and switches
        h1 = self.addHost('h1', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', mac='00:00:00:00:00:02')
        h3 = self.addHost('h3', mac='00:00:00:00:00:03')
        h4 = self.addHost('h4', mac='00:00:00:00:00:04')

# Adding switches
        s1 = self.addSwitch('s1', cls=OVSSwitch)
# Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s1)


def run():
    net = Mininet(topo=SimplePktSwitch(), host=CPULimitedHost, controller=RemoteController('c', '127.0.0.1', 6633))
    net.start()
    h1, h2, h3, h4 = net.hosts[0], net.hosts[1], net.hosts[2], net.hosts[3]
    print(f"h1 MAC: {h1.MAC()}\nh2 MAC: {h2.MAC()}\nh3 MAC: {h3.MAC()}\nh4 MAC: {h4.MAC()}")
 
    net.pingAll()

    sleep(6)
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
