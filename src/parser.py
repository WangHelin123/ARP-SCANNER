import argparse
import os


def parse_args():
    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description='ARP Scanner')
    # 添加参数
    parser.add_argument('--network', type=str, help='Network to scan (e.g., 192.168.1.0/24)')

    args, _ = parser.parse_known_args()

    return args
