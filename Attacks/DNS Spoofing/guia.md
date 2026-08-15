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
https://github.com/miguel34d/RED-TEAM/blob/main/Attacks/DNS%20Spoofing/DNS-Spoofing.py

**Ejecución:**

```bash
sudo python3 DNS-Spoofing.py
```

**Repositorio GitHub del script:**

https://github.com/miguel34d/RED-TEAM/blob/main/Attacks/DNS%20Spoofing/DNS-Spoofing.py

---

## 7. Página Web Legítima (WEB-1)

`index.html`

https://github.com/miguel34d/RED-TEAM/blob/main/Attacks/DNS%20Spoofing/legitimo_login.html

---

## 8. Página Web Falsa (Atacante)

`index.html`

https://github.com/miguel34d/RED-TEAM/blob/main/Attacks/DNS%20Spoofing/atacante_login.html

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
