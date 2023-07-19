from mininet.node import RemoteController
from mininet.log import setLogLevel, info
from mn_wifi.node import OVSKernelAP
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.topo import Topo
from time import sleep

class SimplePktSwitch(Topo):
    """Simple topology example."""
    def __init__(self, **opts):
        """Create custom topo."""
        super(SimplePktSwitch, self).__init__(**opts)
        info("*** Creating nodes\n")
        sta1 = self.addStation('sta1')
        sta2 = self.addStation('sta2')
        sta3 = self.addStation('sta3')
        sta4 = self.addStation('sta4')
        ap1 = self.addAccessPoint('ap1', ssid='new-ssid', mode='g', channel='1', position='50,50,0')
    
        info("*** Configuring WiFi nodes\n")
        self.configureWifiNodes()
    
        info("*** Associating Stations\n")
        self.addLink(sta1, ap1)
        self.addLink(sta2, ap1)
        self.addLink(sta3, ap1)
    
        info("*** Starting network\n")
        self.build()
        self.start()


def run():
    net = Mininet_wifi(topo=SimplePktSwitch(), controller=RemoteController('c', '127.0.0.1', 6653, protocols="OpenFlow13"))
    net.start()
    sta1, sta2, sta3, sta4 = net.hosts[0], net.hosts[1], net.hosts[2], net.hosts[3]
    # print(f"h1 MAC: {h1.MAC()}\nh2 MAC: {h2.MAC()}\nh3 MAC: {h3.MAC()}\nh4 MAC: {h4.MAC()}")

    # h1.cmd("ovs-vsctl -- set Port s1-eth1 qos=@newqos -- --id=@newqos create QoS type=linux-htb other-config:max-rate=10000000 queues=0=@q0,1=@q1 -- --id=@q0 create Queue other-config:min-rate=1000000 other-config:max-rate=1000000 -- --id=@q1 create Queue other-config:min-rate=9000000 other-config:max-rate=9000000")
    # h1.cmd("mkdir d1 d2 d3")
    # h1.cmd("fallocate -l 1G ./d1/dummy")
    sta1.cmd("chmod 777 d*")
    sta1.cmd("cd videos && chmod 777 d* ")
    # path = h1.cmd("pwd")
    # sleep(5)
    # h1.cmd("/usr/sbin/sshd")
    # h2.cmd("/usr/sbin/sshd")
    # h3.cmd("/usr/sbin/sshd")   
    # ping
    net.pingAll()
    sta1.cmd('''xterm -hold -T "h1_stream_A" -e "cvlc -vvv ../videos/test.mp4 --sout '#standard{access=http, mux=ts,dst=:8080}' --no-sout-rtp-sap --no-sout-standard-sap --ttl=1 --sout-keep --loop" &''')
    sta4.cmd('''xterm -hold -T "h4_stream_B" -e "cvlc -vvv ../videos/test2.mp4 --sout '#standard{access=http, mux=ts,dst=:8081}' --no-sout-rtp-sap --no-sout-standard-sap --ttl=1 --sout-keep --loop" &''')

    sta2.cmd("xterm -hold -T 'h2' -e 'vlc http://10.0.0.1:8080' &")

    sleep(6)
    sta3.cmd("xterm -hold -T 'h3' -e 'vlc http://10.0.0.4:8081' &")
    CLI(net)
    # h1.cmd("rm -r d1 d2 d3")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()

