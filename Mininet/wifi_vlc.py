from mininet.node import Controller
from mininet.log import setLogLevel, info
from mininet_wifi.node import OVSKernelAP
from mininet_wifi.cli import CLI_wifi
from mininet_wifi.net import Mininet_wifi


def topology():
    net = Mininet_wifi(controller=Controller, accessPoint=OVSKernelAP)

    info("*** Creating nodes\n")
    sta1 = net.addStation('sta1')
    sta2 = net.addStation('sta2')
    sta3 = net.addStation('sta3')
    ap1 = net.addAccessPoint('ap1', ssid='new-ssid', mode='g', channel='1', position='50,50,0')
    c1 = net.addController('c1')

    info("*** Configuring WiFi nodes\n")
    net.configureWifiNodes()

    info("*** Associating Stations\n")
    net.addLink(sta1, ap1)
    net.addLink(sta2, ap1)
    net.addLink(sta3, ap1)

    info("*** Starting network\n")
    net.build()
    net.start()

    info("*** Running CLI\n")
    CLI_wifi(net)

    info("*** Stopping network")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()

