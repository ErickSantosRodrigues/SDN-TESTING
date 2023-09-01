from mininet.node import RemoteController
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
        sta1 = self.addStation('sta1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        sta2 = self.addStation('sta2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
        sta3 = self.addStation('sta3', ip='10.0.0.3/24', mac='00:00:00:00:00:03')
        sta4 = self.addStation('sta4', ip='10.0.0.4/24', mac='00:00:00:00:00:04')
        ap_arg = {'client_isolation': True}
        ap1 = self.addAccessPoint('ap1', ssid='new-ssid', mode='ac', channel='36', position='50,50,0', **ap_arg)
    
        info("*** Associating Stations\n")
        self.addLink(sta1, ap1, bw=150)
        self.addLink(sta2, ap1, bw=150)
        self.addLink(sta3, ap1, bw=150)
    

def run():
    net = Mininet_wifi(topo=Wifi_band_limit_Topo(), controller=RemoteController('c', '127.0.0.1', 6653, protocols="OpenFlow13"), accessPoint=OVSKernelAP)
    net.start()
    sta1, sta2, sta3, sta4 = net.stations
    net.pingAll()
    sta4.cmd('''xterm -geometry 80x24+0+0 -hold -T "sta1_5002" -e "iperf3 -s --port 5001 " &''')
    sta4.cmd('''xterm -geometry 80x24+625+0 -hold -T "sta1_5003" -e "iperf3 -s --port 5002 " &''')
    sta4.cmd('''xterm -geometry 80x24+1350+0 -hold -T "sta1_5003" -e "iperf3 -s --port 5003 " &''')
    sleep(5)
    sta1.cmd('''xterm -geometry 80x24+0+380 -hold -T "sta1" -e "iperf3 -c 10.0.0.4 --port 5001 -t 60 -i 60"&''')
    sta2.cmd('''xterm -geometry 80x24+625+380 -hold -T "sta2" -e "iperf3 -c 10.0.0.4 --port 5002 -t 60 -i 60" &''')
    sta3.cmd('''xterm -geometry 80x24+625+720 -hold -T "sta2" -e "iperf3 -c 10.0.0.4 --port 5003 -t 60 -i 60" &''')
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
