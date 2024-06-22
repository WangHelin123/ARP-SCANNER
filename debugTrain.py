# debugProxy.py
import os, sys, runpy

## 1. cd WORKDIR
# os.chdir('WORKDIR')
os.chdir('/home/whl/桌面/ARP-LAN-scanning/src/main.py')
# ## 2A. python test.py 4 5
# args = 'python test.py 4 5'
args = 'sudo python main.py --network 192.168.1.0/24'
# ## 2B. python -m mymodule.test 4 5
# args = 'python -m mymodule.test 4 5'

args = args.split()
if args[0] == 'python':
    """pop up the first in the args""" 
    args.pop(0)
if args[0] == '-m':
    """pop up the first in the args"""
    args.pop(0)
    fun = runpy.run_module
else:
    fun = runpy.run_path
sys.argv.extend(args[1:])
fun(args[0], run_name='__main__')
