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
        sta1 = self.addStation('sta1', mac='48:E5:60:8D:A4:9C')
        # sta2 = self.addStation('sta2', mac='00:00:00:00:00:02')
        # sta3 = self.addStation('sta3', mac='00:00:00:00:00:03')
        # sta4 = self.addStation('sta4', mac='00:00:00:00:00:04')

        ap_arg = {'client_isolation': True}
        ap1 = self.addAccessPoint('ap1', ssid='new-ssid', mode='ac', channel='36', position='50,50,0', **ap_arg)
    
        info("*** Associating Stations\n")
        self.addLink(sta1, ap1, bw=150)
        # self.addLink(sta2, ap1, bw=150)
        # self.addLink(sta3, ap1, bw=150)
        # self.addLink(sta4, ap1, bw=150)

# Change the commands of each sta to solicitation of DNS
def run():
    net = Mininet_wifi(topo=Wifi_band_limit_Topo(), host=CPULimitedHost, controller=RemoteController('c', '127.0.0.1', 6653, protocols="OpenFlow13"), accessPoint=OVSKernelAP)
    net.start()
    # sta1, sta2, sta3, sta4 = net.stations[0], net.stations[1], net.stations[2], net.stations[3]
    net.pingAll()
    # sta3.cmd('''xterm -geometry 80x24+625+380 -hold -T "sta3" -e " " &''')
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
