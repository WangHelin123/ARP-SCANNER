import sys
import threading
from scapy.all import ARP, Ether, srp
import ipaddress
from parser import parse_args  

# 定义局域网扫描器类
class ARPScanner:
    def __init__(self, network):
        self.network = network
        self.active_hosts = []

    def scan(self):
        # 获取所有的IP地址
        ip_list = [str(ip) for ip in ipaddress.IPv4Network(self.network)]
        
        # 创建线程
        threads = []
        for ip in ip_list:
            thread = threading.Thread(target=self.arp_request, args=(ip,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        return self.active_hosts

    def arp_request(self, ip):
        # 构造ARP请求包
        arp_request = ARP(pdst=ip)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp_request
        
        # 发送ARP请求并接收应答
        result = srp(packet, timeout=1, verbose=False)[0]
        
        # 解析ARP应答包
        for sent, received in result:
            self.active_hosts.append({'ip': received.psrc, 'mac': received.hwsrc})

def main():
     
    args = parse_args()

    # 指定扫描的网段
    network = args.network

    # 创建扫描器对象
    scanner = ARPScanner(network)

    # 执行扫描
    active_hosts = scanner.scan()

    # 输出结果
    for host in active_hosts:
        print(f"IP: {host['ip']}, MAC: {host['mac']}")

if __name__ == '__main__':
    main()
