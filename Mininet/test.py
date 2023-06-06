from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.node import RemoteController, CPULimitedHost
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
    c0 = RemoteController('c', '127.0.0.1', 6633)
    net = Mininet(topo=SimplePktSwitch(), host=CPULimitedHost, controller=c0)
    # net.addController(c0)
    net.start()
    h1, h2, h3 = net.hosts[0], net.hosts[1], net.hosts[2]

    h1.cmd("mkdir d1 d2 d3")
    h1.cmd("chmod 777 d*")
    path = h1.cmd("pwd") 
    # path.removesuffix("\n")
    # remove \n
    path = path[:-2]
    h1.cmd("echo 'test file' > ./d1/test.txt")
    # print(h1.cmd("whoami"))
    h1.cmd("/usr/sbin/sshd -D &")
    h2.cmd("/usr/sbin/sshd -D &")
    h3.cmd("/usr/sbin/sshd -D &")
    print(h1.cmd("scp /home/sdn/mininet/custom/d1/test.txt sdn@10.0.0.2:/home/sdn/mininet/custom/d2 | echo 'sdn'"))
    # print(f"scp {h1.IP()}:{path}/d1/test.txt {path}/d2")
    # h2error = h2.cmd(f"scp {h1.IP()}:{path}/d1/test.txt {path}/d2")
    # info("*** h2 starting download...\n")
    # print(h2error)
    h1.cmd(" scp /home/sdn/mininet/custom/d1/test.txt sdn@10.0.0.3:/home/sdn/mininet/custom/d3 | echo 'sdn'") 
    # h3.cmd("/usr/sbin/sshd")
    # print(f"scp {h1.IP()}:{path}/d1/test.txt {path}/d3")
    # h3error = h3.cmd(f"scp {h1.IP()}:{path}/d1/test.txt {path}/d3")
    # info("*** h3 starting download...\n")
    # print(h3error)

    #ping
    net.pingAll()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
