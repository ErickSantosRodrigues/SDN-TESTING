from mininet.node import CPULimitedHost
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.node import RemoteController, Controller, OVSSwitch
from mininet.cli import CLI
class SimplePktSwitch(Topo):
    """Simple topology example."""
    def __init__(self, **opts):
        """Create custom topo."""
# Initialize topology
# It uses the constructor for the Topo class
        super(SimplePktSwitch, self).__init__(**opts)
# Add hosts and switches
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
# Adding switches
        s1 = self.addSwitch('s1')
# Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)


def run():
    c0 = RemoteController('c', '0.0.0.0', 6633)
    net = Mininet(topo=SimplePktSwitch() ,host=CPULimitedHost, controller=None)
    net.addController(c0)
    net.start()
    h1, h2, h3 = net.hosts[0], net.hosts[1], net.hosts[2]

    h1.cmd("python -m SimpleHTTPServer 80 &")
    info("*** h1 hosting HTTP Server on port 80\n")

    h2.cmd(f"wget http://{h1.IP()}:80")
    info("*** h2 starting download...\n")
    if "index.html" in h2.cmd("ls | grep index.html"):
        print("File was successfully downloaded on host h2")
        h2.cmd("rm index.html")
    else:
        print("File was not downloaded on host h2")

    h3.cmd(f"wget http://{h1.IP()}:80")
    info("*** h3 starting download...\n")
    if "index.html" in h3.cmd("ls | grep index.html"):
        print("File was successfully downloaded on host h3")
        h3.cmd("rm index.html")
    else:
        print("File was not downloaded on host h3") 

    #ping
    net.pingAll()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
