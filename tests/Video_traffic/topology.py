from mininet.node import CPULimitedHost
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from time import sleep


class Video_traffic(Topo):
    def __init__(self, **opts):
        super(Video_traffic, self).__init__(**opts)
    # Add hosts and switches
        h1 = self.addHost('h1', mac='00:00:00:00:00:01', ip='10.0.0.1')
        h2 = self.addHost('h2', mac='00:00:00:00:00:02', ip='10.0.0.2')
        h3 = self.addHost('h3', mac='00:00:00:00:00:03', ip='10.0.0.3')
        h4 = self.addHost('h4', mac='00:00:00:00:00:04', ip='10.0.0.4')

        s1 = self.addSwitch('s1', cls=OVSSwitch, protocols="OpenFlow13")

        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s1)


def run():
    net = Mininet(topo=Video_traffic(), host=CPULimitedHost, controller=RemoteController('c', '127.0.0.1', 6653, protocols="OpenFlow13"))
    net.start()
    h1, h2, h3, h4 = net.hosts[0], net.hosts[1], net.hosts[2], net.hosts[3]

    h1.cmd("chmod 777 d*")
    net.pingAll()
    h1.cmd('''xterm -geometry 80x24+0+0 -hold -T "h1_stream_A" -e "cvlc -vvv ../videos/test.mp4 --sout '#standard{access=http, mux=ts,dst=:8080}' --no-sout-rtp-sap --no-sout-standard-sap --ttl=1 --sout-keep --loop" &''')
    h4.cmd('''xterm -geometry 80x24+650+0 -hold -T "h4_stream_B" -e "cvlc -vvv ../videos/test2.mp4 --sout '#standard{access=http, mux=ts,dst=:8081}' --no-sout-rtp-sap --no-sout-standard-sap --ttl=1 --sout-keep --loop" &''')

    h2.cmd("xterm -geometry 80x24+0+380 -hold -T 'h2' -e 'vlc http://10.0.0.1:8080' &")

    sleep(6)
    h3.cmd("xterm -geometry 80x24+650+380 -hold -T 'h3' -e 'vlc http://10.0.0.4:8081' &")
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
