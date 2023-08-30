from mininet.node import RemoteController, CPULimitedHost
from mininet.log import setLogLevel, info
from mn_wifi.node import OVSKernelAP
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.topo import Topo
from time import sleep


class Wifi_video_traffic(Topo):
    def __init__(self, **opts):
        super(Wifi_video_traffic, self).__init__(**opts)
    # Add hosts and switches
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
        self.addLink(sta4, ap1, bw=150)
    

def run():
    net = Mininet_wifi(topo=Wifi_video_traffic(), host=CPULimitedHost, controller=RemoteController('c', '127.0.0.1', 6653, protocols="OpenFlow13"), accessPoint=OVSKernelAP)
    net.start()
    sta1, sta2, sta3, sta4 = net.stations
    net.waitConnected()
    sta1.cmd("chmod 777 d*")
    net.pingAll()
    sta1.cmd('''xterm -geometry 80x24+0+0 -hold -T "sta1_stream_A" -e "cvlc -vvv ../videos/test.mp4 --sout '#standard{access=http, mux=ts,dst=:8080}' --no-sout-rtp-sap --no-sout-standard-sap --ttl=1 --sout-keep --loop" &''')
    sta4.cmd('''xterm -geometry 80x24+650+0 -hold -T "sta4_stream_B" -e "cvlc -vvv ../videos/test2.mp4 --sout '#standard{access=http, mux=ts,dst=:8081}' --no-sout-rtp-sap --no-sout-standard-sap --ttl=1 --sout-keep --loop" &''')

    sleep(6)
    sta2.cmd("xterm -geometry 80x24+0+380 -hold -T 'sta2' -e 'vlc http://10.0.0.1:8080' &")

    sleep(10)
    sta3.cmd("xterm -geometry 80x24+650+380 -hold -T 'sta3' -e 'vlc http://10.0.0.4:8081' &")
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
