from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import RemoteController, OVSSwitch
from mininet.log import setLogLevel

class MyTopology(Topo):
    def __init__(self):
        Topo.__init__(self)

        # Add hosts
        host1 = self.addHost('h1')
        host2 = self.addHost('h2')
        host3 = self.addHost('h3')

        # Add switch
        switch = self.addSwitch('s1', cls=OVSSwitch)

        # Add links
        self.addLink(host1, switch)
        self.addLink(host2, switch)
        self.addLink(host3, switch)


def create_topology():
    topo = MyTopology()
    controller_ip = '0.0.0.0'
    controller_port = 6633
    net = Mininet(topo=topo, controller=lambda name: RemoteController(name, ip=controller_ip, port=controller_port), switch=OVSSwitch, autoSetMacs=True)
    
    net.start()
    net.waitConnected()
    net.pingAll()

    net.interact()

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_topology()

