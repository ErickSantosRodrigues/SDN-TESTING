from mininet.node import RemoteController, OVSSwitch, CPULimitedHost
from mininet.log import setLogLevel, info
from mn_wifi.node import OVSKernelAP
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.topo import Topo
from time import sleep


class Wifi_band_limit_Topo(Topo):
    def __init__(self, **opts):
        Topo.__init__(self, **opts)
        info("*** Creating nodes\n")
        sta1 = self.addStation('sta1', mac='00:00:00:00:00:01')
        sta2 = self.addStation('sta2', mac='00:00:00:00:00:02')
        sta3 = self.addStation('sta3', mac='00:00:00:00:00:03')

        ap_arg = {'client_isolation': True}
        ap1 = self.addAccessPoint('ap1', ssid='new-ssid', mode='ac', channel='36', position='50,50,0', **ap_arg)
    
        info("*** Associating Stations\n")
        self.addLink(sta1, ap1, bw=150)
        self.addLink(sta2, ap1, bw=150)
        self.addLink(sta3, ap1, bw=150)

# Change the commands of each sta to solicitation of DNS
def run():
    net = Mininet_wifi(topo=Wifi_band_limit_Topo(), host=CPULimitedHost, controller=RemoteController('c', '127.0.0.1', 6653, protocols="OpenFlow13"), accessPoint=OVSKernelAP)
    net.start()
    # net.addNAT(name='nat0', linkTo='ap1', ip='192.168.100.254').configDefault()
    sta1, sta2, sta3 = net.stations[0], net.stations[1], net.stations[2]
    net.pingAll()
    # sta1.cmd('''xterm -geometry 80x24+0+0 -hold -T "DNS_Solicitation_1" -e "dig +notcp www.example.com " &''')
    # sleep(20)
    # sta2.cmd('''xterm -geometry 80x24+625+0 -hold -T "DNS_Solicitation_2" -e "dig +notcp www.example.com " &''')
    # sleep(10)
    # sta3.cmd('''xterm -geometry 80x24+625+380 -hold -T "sta3" -e " " &''')
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
