from mininet.node import RemoteController, OVSSwitch, CPULimitedHost
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.topo import Topo
from time import sleep


class Wifi_band_limit_Topo(Topo):
    def __init__(self, **opts):
        Topo.__init__(self, **opts)
        info("*** Creating nodes\n")
        sta1 = self.addStation('sta1')
        sta2 = self.addStation('sta2')
        sta3 = self.addStation('sta3')
        ap1 = self.addAccessPoint('ap1', ssid='new-ssid', mode='g', channel='1', position='50,50,0')
    
        info("*** Associating Stations\n")
        self.addLink(sta1, ap1)
        self.addLink(sta2, ap1)
        self.addLink(sta3, ap1)
    
        self.build()


def run():
    net = Mininet_wifi(topo=Wifi_band_limit_Topo(), host=CPULimitedHost, controller=RemoteController('c', '127.0.0.1', 6653, protocols="OpenFlow13"))
    net.start()
    sta1, sta2, sta3 = net.stations[0], net.stations[1], net.stations[2]
    net.pingAll()
    sta1.cmd('''xterm -geometry 80x24+0+0 -hold -T "sta1_5002" -e "iperf3 -s --port 5002" &''')
    sta1.cmd('''xterm -geometry 80x24+625+0 -hold -T "sta1_5003" -e "iperf3 -s --port 5003" &''')
    sleep(5)
    sta2.cmd('''xterm -geometry 80x24+0+380 -hold -T "sta2" -e "iperf3 -c 10.0.0.1 --port 5002 -t 40 -i 40"&''')
    sleep(5)
    sta3.cmd('''xterm -geometry 80x24+625+380 -hold -T "sta3" -e "iperf3 -c 10.0.0.1 --port 5003 -t 10 -i 10" &''')
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
