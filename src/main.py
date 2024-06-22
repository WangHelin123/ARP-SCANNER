import sys
import threading
from scapy.all import ARP, Ether, srp
import ipaddress
from PyQt5.QtCore import pyqtSignal, QObject, QThread, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QLineEdit
from parser import parse_args  

# 定义局域网扫描器类
class ARPScanner(QObject):
    scan_complete = pyqtSignal(list)

    def __init__(self, network):
        super().__init__()
        self.network = network
        self.active_hosts = []

    @pyqtSlot()
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
        
        self.scan_complete.emit(self.active_hosts)

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

# 创建GUI应用程序
class App(QWidget):
    def __init__(self, network=None):
        super().__init__()
        self.title = 'ARP Scanner'
        self.network = network
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 800, 600)

        # 创建布局
        layout = QVBoxLayout()
        
        # 创建控件
        self.label = QLabel('ARP Scanner', self)
        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)
        self.inputField = QLineEdit(self)
        self.inputField.setPlaceholderText("Enter a subnet or a network device (e.g., 192.168.1.0/24 or 192.168.1.0)")
        self.button = QPushButton('Start Scan', self)
        
        # 将控件添加到布局
        layout.addWidget(self.label)
        layout.addWidget(self.inputField)
        layout.addWidget(self.textEdit)
        layout.addWidget(self.button)
        
        # 设置主窗口布局
        self.setLayout(layout)

        # 连接按钮点击事件到函数
        self.button.clicked.connect(self.start_scan)
        
        self.show()

        # 如果通过命令行参数指定了网络，直接开始扫描
        if self.network:
            self.inputField.setText(self.network)
            self.start_scan()

    def start_scan(self):
        # 禁用按钮
        self.button.setEnabled(False)
        self.textEdit.clear()
        self.textEdit.append('Scanning...')
        
        # 获取输入的网段
        network = self.inputField.text()
        if not network:
            self.textEdit.append('Please enter a valid network.')
            self.button.setEnabled(True)
            return
        
        # 创建扫描器对象
        self.scanner = ARPScanner(network)
        self.scanner.scan_complete.connect(self.update_result)
        
        # 启动扫描线程
        self.scan_thread = QThread()
        self.scanner.moveToThread(self.scan_thread)
        self.scan_thread.started.connect(self.scanner.scan)
        self.scan_thread.finished.connect(self.scan_thread.deleteLater)
        self.scan_thread.start()

    @pyqtSlot(list)
    def update_result(self, active_hosts):
        # 更新UI
        self.textEdit.clear()
        self.textEdit.append('Scan complete. Found hosts:\n')
        for host in active_hosts:
            self.textEdit.append(f"IP: {host['ip']}, MAC: {host['mac']}")
        
        # 重新启用按钮
        self.button.setEnabled(True)

    def closeEvent(self, event):
        if hasattr(self, 'scan_thread') and self.scan_thread.isRunning():
            self.scan_thread.quit()
            self.scan_thread.wait()
        event.accept()

def main():
    args = parse_args()

    app = QApplication(sys.argv)
    ex = App(network=args.network)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
