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
        s1 = self.addSwitch('s1', cls=OVSSwitch, protocols="OpenFlow13")
# Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s1)


def run():
    net = Mininet(topo=SimplePktSwitch(), host=CPULimitedHost, controller=RemoteController('c', '127.0.0.1', 6653, protocols="OpenFlow13"))
    net.start()
    h1, h2, h3, h4 = net.hosts[0], net.hosts[1], net.hosts[2], net.hosts[3]
    print(f"h1 MAC: {h1.MAC()}\nh2 MAC: {h2.MAC()}\nh3 MAC: {h3.MAC()}\nh4 MAC: {h4.MAC()}")

    # h1.cmd("ovs-vsctl -- set Port s1-eth1 qos=@newqos -- --id=@newqos create QoS type=linux-htb other-config:max-rate=10000000 queues=0=@q0,1=@q1 -- --id=@q0 create Queue other-config:min-rate=1000000 other-config:max-rate=1000000 -- --id=@q1 create Queue other-config:min-rate=9000000 other-config:max-rate=9000000")
    # h1.cmd("mkdir d1 d2 d3")
    # h1.cmd("fallocate -l 1G ./d1/dummy")
    h1.cmd("chmod 777 d*")
    h1.cmd("cd videos && chmod 777 d* ")
    # path = h1.cmd("pwd")
    # sleep(5)
    # h1.cmd("/usr/sbin/sshd")
    # h2.cmd("/usr/sbin/sshd")
    # h3.cmd("/usr/sbin/sshd")   
    #ping
    net.pingAll()
    h1.cmd('''xterm -hold -T "h1_stream_A" -e "cvlc -vvv ../videos/test.mp4 --sout '#standard{access=http, mux=ts,dst=:8080}' --no-sout-rtp-sap --no-sout-standard-sap --ttl=1 --sout-keep --loop" &''')
    h4.cmd('''xterm -hold -T "h4_stream_B" -e "cvlc -vvv ../videos/test2.mp4 --sout '#standard{access=http, mux=ts,dst=:8081}' --no-sout-rtp-sap --no-sout-standard-sap --ttl=1 --sout-keep --loop" &''')


    h2.cmd("xterm -hold -T 'h2' -e 'vlc http://10.0.0.1:8080' &")

    sleep(6)
    h3.cmd("xterm -hold -T 'h3' -e 'vlc http://10.0.0.4:8081' &")
    CLI(net)
    # h1.cmd("rm -r d1 d2 d3")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
