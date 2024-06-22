import subprocess
from termcolor import colored
from tqdm import tqdm
import torch
import argparse


# 定义一个函数，用于在并行中运行命令
def run_commands_in_parallel(commands):
    # 使用subprocess.Popen()函数启动命令，并设置shell为True
    processes = [subprocess.Popen(cmd, shell=True) for cmd  in commands]
    # 等待所有进程完成
    for p in processes:
        p.wait()

# 定义一个函数，用于将输入列表分割成K个一组的新列表
def split_list(input_list, K):
    # 使用range()函数遍历输入列表，并按照K个一组分割
    return [input_list[i:i+K] for i in range(0, len(input_list), K)]


if __name__ == '__main__':
    # 清除cuda缓存
    torch.cuda.empty_cache()

    # 设置命令的数量
    num_cmds = 8
    # 设置命令模板
    cmd_biao = 'python3 src/main.py'
    # 初始化命令列表
    cmds =[]
    # 设置network
    seeds = ["192.168.1.0/24","192.168.2.0/24","192.168.3.0/24"]
    # 遍历network，生成命令列表
    for seed in seeds:
        cmd = cmd_biao+"  --network {} ".format(seed)
        cmds.append(cmd)
          
    # 将命令列表分割成K个一组的新列表
    commands_batches = split_list(cmds,num_cmds)

    # 初始化计数器
    cnt = 0
    # 遍历新列表，并运行命令
    for commands in tqdm(commands_batches):
        cnt +=1
        print (colored(f"--------current progress: {cnt} out of {len(commands_batches)}---------", 'blue','on_white'))
        run_commands_in_parallel(commands)