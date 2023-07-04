from mininet.node import Controller
from mn_wifi.cli import CLI_wifi
from mn_wifi.net import Mininet_wifi
from mininet.link import TCLink

def topology():
    "Create a network."
    net = Mininet_wifi(controller=Controller)

    info("*** Creating nodes\n")
    ap1 = net.addAccessPoint('ap1', ssid='ssid-ap1', mode='g', channel='1',
                             position='50,50,0')
    host1 = net.addStation('host1', ip='192.168.0.1/24',
                           position='40,40,0')
    host2 = net.addStation('host2', ip='192.168.0.2/24',
                           position='100,100,0')
    host3 = net.addStation('host3', ip='192.168.0.3/24',
                           position='120,120,0')
    c1 = net.addController('c1')

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Creating links\n")
    net.addLink(ap1, host1, link=TCLink, bw=10)
    net.addLink(ap1, host2, link=TCLink, bw=10)
    net.addLink(ap1, host3, link=TCLink, bw=10)

    info("*** Starting network\n")
    net.build()
    c1.start()
    ap1.start([c1])

    info("*** Running CLI\n")
    CLI_wifi(net)

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    topology()

