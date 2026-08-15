# Laboratorio: HSRP Hijacking (Secuestro del Router Activo)

![Estudiante](https://img.shields.io/badge/Estudiante-Miguel%20Ramirez%20Meli-0d6efd?style=flat-square) ![Matr%C3%ADcula](https://img.shields.io/badge/Matr%C3%ADcula-2025--1367-0d6efd?style=flat-square) ![Materia](https://img.shields.io/badge/Materia-Seguridad%20de%20Redes-fd5b45?style=flat-square) ![Profesor](https://img.shields.io/badge/Profesor-Jonathan%20Rond%C3%B3n-fd5b45?style=flat-square) ![Instituci%C3%B3n](https://img.shields.io/badge/Instituci%C3%B3n-ITLA-6c757d?style=flat-square)

![Estado](https://img.shields.io/badge/Estado-Resuelto-28a745?style=flat-square) ![Ataque](https://img.shields.io/badge/Ataque-HSRP%20Hijacking-fd5b45?style=flat-square)

---

## Topología de red

![Topología del laboratorio](topologia.png)

| Dispositivo | Rol | IP | Detalle |
|---|---|---|---|
| Kali | Atacante | 10.13.67.10/24 | Conectado a Switch1 (e0/0), salida a Internet vía Cloud1 (e1) |
| Windows10-1 | Víctima | 10.13.67.20/24 | Gateway configurado: 10.13.67.1 (IP virtual HSRP) |
| Router1 | Gateway (Active) | 10.13.67.2/24 | Grupo HSRP 1, prioridad 110, preempt habilitado |
| Router2 | Gateway (Standby) | 10.13.67.3/24 | Grupo HSRP 1, prioridad 100 |
| Switch1 | Switch de acceso | — | VLAN 10, sin protecciones L2 (sin Port Security / DHCP Snooping / DAI) |

Red: **10.13.67.0/24** — Kali, Windows10-1, Router1 y Router2 comparten el mismo dominio de broadcast (VLAN 10) a través de Switch1, condición necesaria para el ataque HSRP.

---

## Configuración vulnerable inicial

### Router1 (Active)

```
hostname Router1

interface Ethernet0/0
 description LAN - HSRP Group
 ip address 10.13.67.2 255.255.255.0
 no shutdown
 standby 1 ip 10.13.67.1
 standby 1 priority 110
 standby 1 preempt
```

### Router2 (Standby)

```
hostname Router2

interface Ethernet0/0
 description LAN - HSRP Group
 ip address 10.13.67.3 255.255.255.0
 no shutdown
 standby 1 ip 10.13.67.1
 standby 1 priority 100
```

### Switch1

```
hostname Switch1

vlan 10
 name LAN_VICTIMAS

interface range e0/0 - 3
 switchport mode access
 switchport access vlan 10
 no shutdown
```

**Vulnerabilidad:** el grupo HSRP 1 (IP virtual `10.13.67.1`) no tiene `standby 1 authentication` configurado en ningún router. Cualquier dispositivo dentro de la VLAN 10 puede inyectar paquetes Hello HSRP falsificados con una prioridad más alta y forzar su elección como router Active, sin que los routers legítimos puedan detectar ni rechazar el paquete.

---

## Ejecución del ataque

Desde Kali, se ejecutó un script en Python que escucha el tráfico HSRP existente, detecta las prioridades reales de los routers e inyecta paquetes Hello forjados anunciando `state=active` con prioridad `200` (superior a los 110 de Router1) hacia el grupo multicast `224.0.0.2`, cada 3 segundos.

![Ejecución del ataque desde Kali](capturas/12-ataque-kali-ejecucion-script.png)

---

## Tabla comparativa: Antes / Durante / Después

| Verificación | Antes del ataque | Durante el ataque | Después de mitigación |
|---|---|---|---|
| Estado Router1 | Active (local, pri. 110) | **Standby** (Active=10.13.67.10) | Active (local, pri. 110) |
| Estado Router2 | Standby (pri. 100) | **Listen** | Standby (pri. 100) |
| Tabla MAC Switch1 (MAC virtual `0000.0c07.ac01`) | Puerto Et0/2 (Router1) | Sin cambios (Et0/2) | Sin cambios (Et0/2) |
| ARP en víctima (10.13.67.1) | Resuelto a MAC virtual | Sin cambios | Sin cambios |
| Ping víctima → gateway | — | **100% perdido** | 0% perdido |
| Tráfico HSRP (tcpdump) | Hellos limpios (20 bytes), Router1 active / Router2 standby | Hello forjado de Kali `state=active` pri. 200 aceptado por la red | Hellos legítimos de 50 bytes (con MD5); paquetes de Kali (20 bytes, sin auth) descartados |

---

## Capturas — Antes del ataque (línea base)

| Captura | Descripción |
|---|---|
| ![](capturas/04-antes-router1-standby-brief-ok.png) | Router1 — `show standby brief`: Active |
| ![](capturas/05-antes-router1-standby-detalle.png) | Router1 — `show standby`: detalle sin autenticación |
| ![](capturas/02-antes-router2-standby-brief.png) | Router2 — `show standby brief`: Standby |
| ![](capturas/03-antes-router2-standby-detalle.png) | Router2 — `show standby`: detalle sin autenticación |
| ![](capturas/06-antes-switch1-mac-address-table.png) | Switch1 — tabla MAC: MAC virtual en Et0/2 |
| ![](capturas/08-antes-windows10-ip-config.png) | Windows10-1 — configuración IP y gateway |
| ![](capturas/07-antes-windows10-arp-a.png) | Windows10-1 — caché ARP inicial |
| ![](capturas/09-antes-kali-ip-addr-eth0.png) | Kali — configuración de interfaz eth0 |
| ![](capturas/10-antes-kali-arp-a.png) | Kali — caché ARP inicial |
| ![](capturas/11-antes-kali-tcpdump-hsrp.png) | Kali — tráfico HSRP legítimo (tcpdump) |

## Capturas — Durante el ataque

| Captura | Descripción |
|---|---|
| ![](capturas/13-durante-router1-standby-brief.png) | Router1 pasa a Standby |
| ![](capturas/14-durante-router2-standby-brief.png) | Router2 pasa a Listen |
| ![](capturas/15-durante-switch1-mac-address-table.png) | Switch1 — tabla MAC sin cambios |
| ![](capturas/16-durante-windows10-arp-a.png) | Windows10-1 — ARP sin cambios |
| ![](capturas/17-durante-windows10-ping-gateway-fallido.png) | Windows10-1 — ping al gateway falla (DoS) |
| ![](capturas/18-durante-kali-tcpdump-hsrp.png) | Kali — tcpdump confirmando Hello forjado aceptado |

## Capturas — Mitigación y reintento

| Captura | Descripción |
|---|---|
| ![](capturas/19-mitigacion-router1-standby-md5.png) | Router1 — autenticación MD5 aplicada |
| ![](capturas/20-mitigacion-router2-standby-md5.png) | Router2 — autenticación MD5 aplicada |
| ![](capturas/21-reintento-kali-ejecucion-script.png) | Kali — reintento del ataque tras mitigación |
| ![](capturas/22-reintento-router1-standby-sin-efecto.png) | Router1 — permanece Active a pesar del ataque |

## Capturas — Verificación final post-mitigación

| Captura | Descripción |
|---|---|
| ![](capturas/23-despues-router2-standby-brief.png) | Router2 — vuelve a Standby normal |
| ![](capturas/24-despues-windows10-ping-gateway-ok.png) | Windows10-1 — ping al gateway exitoso (0% perdido) |
| ![](capturas/25-despues-kali-tcpdump-hsrp-auth.png) | Kali — Hellos legítimos con MD5 (50 bytes) vs. paquetes forjados descartados |

---

## Mitigación aplicada

En **Router1** y **Router2**:

```
enable
configure terminal
interface Ethernet0/0
 standby 1 authentication md5 key-string HSRP_S3cr3t_2026
exit
end
write memory
```

- `standby 1 authentication md5 key-string ...`: habilita autenticación MD5 en el grupo HSRP 1. Cada Hello debe incluir un hash calculado con la clave compartida configurada en ambos routers; cualquier paquete que no traiga el hash correcto (como los inyectados por un atacante que desconoce la clave) es descartado sin afectar la elección del router Active.

---

## Conclusión

El grupo HSRP 1 (`10.13.67.1`) fue configurado inicialmente sin autenticación, lo que permitió desde Kali —ubicado en el mismo dominio de broadcast que Router1 y Router2— inyectar paquetes Hello HSRP falsificados con una prioridad artificialmente alta (200) y forzar el rol Active en el protocolo de control HSRP. Router1 pasó a Standby y Router2 a Listen, evidenciando el hijacking a nivel de protocolo.

Sin embargo, la verificación de la tabla MAC del switch mostró que la dirección MAC virtual (`0000.0c07.ac01`) nunca cambió de puerto, ya que Kali no realizó envenenamiento ARP (Gratuitous ARP) ni activó IP forwarding. Como consecuencia, el tráfico de la víctima siguió siendo conmutado hacia el puerto físico de Router1, que ya no respondía como Active, resultando en una **denegación de servicio (DoS) del gateway** en lugar de una intercepción efectiva de tráfico (MITM completo). Esta distinción es relevante: el ataque comprometió la disponibilidad del enrutamiento aunque no logró interceptar el tráfico de datos, lo cual habría requerido combinar el HSRP hijacking con ARP spoofing.

La mitigación mediante **autenticación MD5** en el grupo HSRP resolvió el problema de raíz: al reintentar el ataque exactamente igual que antes, los paquetes forjados fueron descartados por ambos routers al no incluir el hash MD5 válido, y el grupo se mantuvo estable (Router1 Active, Router2 Standby) durante todo el reintento, confirmado por la recuperación de la conectividad de la víctima hacia su gateway (0% de pérdida en el ping final).

**Recomendaciones adicionales:**
- Habilitar `standby 1 authentication md5` (o su equivalente en VRRP) en todo despliegue de redundancia de primer salto, nunca dejarlo sin autenticar.
- Complementar con **DHCP Snooping**, **Dynamic ARP Inspection (DAI)** y **Port Security** en Switch1 para prevenir ataques relacionados como ARP Spoofing, que sí lograrían interceptar el tráfico de datos.
- Monitorear cambios de estado HSRP (`%STANDBY-6-STATECHANGE`) mediante syslog/SNMP para detectar intentos de hijacking en tiempo real.
