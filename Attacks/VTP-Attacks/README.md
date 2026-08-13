<div align="center">

# 🔴 VTP Attack — VLAN Manipulation

![Kali Linux](https://img.shields.io/badge/Kali_Linux-557C94?style=for-the-badge&logo=kali-linux&logoColor=white)
![Python](https://img.shields.io/badge/Python_3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GNS3](https://img.shields.io/badge/GNS3-FF6600?style=for-the-badge&logo=cisco&logoColor=white)
![Cisco](https://img.shields.io/badge/Cisco_IOU-1BA0D7?style=for-the-badge&logo=cisco&logoColor=white)

<br>

| 👤 Autor | 🎓 Matrícula | 📚 Asignatura | 👨‍🏫 Maestro |
|:---:|:---:|:---:|:---:|
| Miguel Ramirez Meli | 2025-1367 | Seguridad de Redes | Jonathan Rondon |

> ⚠️ **Este laboratorio fue realizado en un entorno controlado (GNS3) con fines exclusivamente educativos.**

</div>

---

## 📋 Tabla de Contenidos

- [🎯 Objetivo del Laboratorio](#-objetivo-del-laboratorio)
- [⚙️ Objetivo del Script](#️-objetivo-del-script)
- [🔬 Funcionamiento del Script](#-funcionamiento-del-script)
- [🌐 Documentación de la Red](#-documentación-de-la-red)
- [📸 Capturas de Pantalla](#-capturas-de-pantalla)
- [🛡️ Contramedidas](#️-contramedidas)
- [🎬 Video Demostración](#-video-demostración)

---

## 🎯 Objetivo del Laboratorio

Demostrar en un entorno controlado cómo un atacante puede explotar el protocolo **VTP (VLAN Trunking Protocol)** para manipular la base de datos de VLANs de switches Cisco, logrando **agregar y borrar VLANs** de forma no autorizada en toda la red. El laboratorio emplea **Yersinia** como herramienta de ataque.

### El laboratorio busca:

- 🔍 Comprender el funcionamiento del protocolo VTP y su vulnerabilidad ante mensajes maliciosos.
- ⚡ Ejecutar de forma reproducible el ataque de adición y eliminación de VLANs usando Yersinia.
- 🛡️ Documentar y aplicar las contramedidas necesarias para mitigar el ataque.

---

## ⚙️ Objetivo del Script

El script automatiza el uso de **Yersinia** para enviar paquetes VTP maliciosos con número de revisión superior al del servidor legítimo, logrando que los switches acepten la configuración del atacante. Esto permite:

| Acción | Descripción | Impacto |
|--------|-------------|---------|
| 🟢 **Agregar VLAN** | Inyecta VLANs inexistentes en el dominio VTP | Modificación no autorizada de la red |
| 🔴 **Borrar VLANs** | Vacía la base de datos VTP del dominio | Denegación de servicio (DoS) total |

### Parámetros

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `Interfaz` | Interfaz de red a usar para el ataque | `e0` |
| `Acción VTP` | Tipo de ataque | `1` = Agregar / `2` = Borrar |
| `VLAN ID` | Número de VLAN objetivo | `10`, `20` |

### 🚀 Uso

```bash
sudo python3 MiguelRamirezMeli_2025-1367_Script_P1.py

# O directamente con Yersinia:
sudo yersinia vtp -attack 1 -i e0    # ➕ Agregar VLAN
sudo yersinia vtp -attack 2 -i e0    # 🗑️  Borrar VLANs
```

### 📦 Requisitos

| Requisito | Versión / Detalle |
|-----------|-------------------|
| 🐧 Sistema Operativo | Kali Linux (recomendado) |
| 🐍 Python | 3.8 o superior |
| 🔧 Yersinia | `sudo apt install yersinia` |
| 🔑 Permisos | `sudo` (root) |
| 🖥️ Entorno de red | GNS3 (laboratorio controlado) |
| 🔀 Switch Cisco | VTP mode Server activo en IOU1 |

```bash
# Instalación rápida
sudo apt update && sudo apt install yersinia -y
```

---

## 🔬 Funcionamiento del Script

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUJO DEL ATAQUE VTP                     │
└─────────────────────────────────────────────────────────────┘

Inicio
  └── 📝 Solicitar interfaz y acción (agregar/borrar VLAN)
        └── 🔑 Verificar privilegios root
              └── 🔧 Verificar que Yersinia esté instalado
                    ├── ➕ [Agregar VLAN] attack 1
                    │     └── 📡 sudo yersinia -I
                    │           └── ✅ VLAN propagada al dominio VTP
                    └── 🗑️  [Borrar VLANs] attack 2
                          └── 📡 sudo yersinia -I
                                └── ❌ Base de datos VTP vaciada
```

### ¿Cómo funciona el ataque?

1. **🔌 Posicionamiento:** Kali Linux conectado por enlace troncal al switch IOU1 (VTP Server).
2. **📨 Inyección VTP:** Yersinia envía `VTP Summary Advertisement` con *revision number* mayor al legítimo.
3. **✅ Aceptación:** El switch acepta la nueva configuración al ver un número de revisión superior.
4. **➕ Agregar VLAN:** Nueva VLAN propagada a todos los switches del dominio VTP.
5. **🗑️ Borrar VLAN:** Base de datos reemplazada por una vacía → todos los switches pierden sus VLANs.
6. **💥 Efecto final:** Puertos sin VLAN asignada → denegación de servicio a nivel de red.

---

## 🌐 Documentación de la Red

### 🖥️ Topología en GNS3
<img width="991" height="511" alt="image" src="https://github.com/user-attachments/assets/e17b61c2-52cf-4816-a8c1-8dfdf16bbf9b" />

### 📡 Dispositivos y Conexiones

| Dispositivo | Rol | Interfaz Local | Conectado a | Dirección IP |
|:-----------:|:---:|:--------------:|:-----------:|:------------:|
| 🔀 IOU1 (Switch) | VTP Server | `e0/0` | Kali (`e0`) | — |
| 💻 Kali Linux | Atacante | `e0` | IOU1 (`e0/0`) | `10.13.67.10/24` |
| 💻 Kali Linux | Atacante | `e1` (tap0) | Cloud1 | DHCP |

### 🗺️ Direccionamiento IP

> Basado en los últimos dígitos de la matrícula **2025-1367**

| Dispositivo | Interfaz | Dirección IP | Máscara |
|:-----------:|:--------:|:------------:|:-------:|
| 💻 Kali Linux | `e0` | `10.13.67.10` | `/24` |
| 🔀 IOU1 | `e0/0` | `10.13.67.1` | `/24` |

### 🏷️ VLANs

| VLAN ID | Nombre | Red | Propósito |
|:-------:|:------:|:---:|:---------:|
| **10** | VLAN10 | `10.13.67.0/24` | VLAN legítima — objetivo del ataque |
| **20** | VLAN20 | `10.13.67.0/24` | VLAN legítima — objetivo del ataque |

### ⚙️ Configuración VTP — Switch IOU1

```cisco
IOU1(config)# vtp domain LAB-1367
IOU1(config)# vtp mode server
IOU1(config)# vtp version 2
IOU1(config)# interface e0/0
IOU1(config-if)# switchport trunk encapsulation dot1q
IOU1(config-if)# switchport mode trunk
```

---


### 02 — VLANs en el servidor VTP antes del ataque
<img width="888" height="422" alt="image" src="https://github.com/user-attachments/assets/788586ee-b889-423f-b39b-2f3edc125f87" />
  
---

### 03 — Ejecución del script (agregar VLAN)
<img width="867" height="598" alt="image" src="https://github.com/user-attachments/assets/95b6988b-6cd8-4223-872e-7a06f0b60293" />

---

### 04 — Comandos en el switch para aplicar el ataque
<img width="293" height="60" alt="Comandos switch" src="https://github.com/user-attachments/assets/cb22ba2e-1eda-442b-ba3c-7ebac092cf3a" />

---

### 05 — VLAN agregada propagada en el switch
<img width="461" height="192" alt="VLAN propagada" src="https://github.com/user-attachments/assets/a4d542be-17f4-4f59-a23d-689b77f30979" />

---

### 06 — Ejecución del script (borrar VLAN)
<img width="597" height="428" alt="image" src="https://github.com/user-attachments/assets/bfba1c1e-ec23-4fee-8e6f-1f589a309e6a" />


---

### 07 — Aplicación de contramedidas
<img width="797" height="497" alt="image" src="https://github.com/user-attachments/assets/ceeec565-ec2f-44cc-8626-9d9e9f62acaf" />

---

### 08 — Verificación post-contramedida
<img width="655" height="477" alt="image" src="https://github.com/user-attachments/assets/682e0967-fe10-484f-8b17-b179ffb91522" />

<img width="443" height="191" alt="Verificación 2" src="https://github.com/user-attachments/assets/848427c5-d6d8-410b-8365-0ffec947070a" />

---

## 🛡️ Contramedidas

### 🔐 Contramedida 1 — VTP Versión 3 con contraseña

VTPv3 introduce autenticación encriptada y el mecanismo de **Primary Server**, impidiendo que un atacante inyecte mensajes con número de revisión superior al legítimo:

```cisco
! ── Actualizar a VTP v3 y configurar contraseña encriptada ──
IOU1(config)# vtp version 3
IOU1(config)# vtp password 2025-1367 secret

! ── Designar como Primary Server (obligatorio en VTPv3) ──
IOU1# vtp primary

! ── Verificar ──
IOU1# show vtp status
IOU1# show vtp password
```

### 🚫 Contramedida 2 — Deshabilitar negociación de trunk (nonegotiate)

`switchport nonegotiate` deshabilita **DTP** en la interfaz, impidiendo que el atacante negocie un enlace troncal y envíe paquetes VTP:

```cisco
! ── Deshabilitar DTP en el puerto del atacante ──
IOU1(config)# interface e0/0
IOU1(config-if)# switchport nonegotiate

! ── En puertos de acceso ──
IOU1(config-if)# switchport mode access
IOU1(config-if)# switchport nonegotiate

! ── Verificar ──
IOU1# show interfaces e0/0 trunk
IOU1# show dtp interface e0/0
```

### 📊 Resumen de Efectividad

| # | Contramedida | Efectividad | Descripción |
|:-:|:------------:|:-----------:|:------------|
| 1 | 🔐 VTP v3 + password secret | 🟢 **Alta** | Autentica mensajes VTP; bloquea inyección con revisión falsa |
| 2 | 🚫 switchport nonegotiate | 🟢 **Alta** | Bloquea DTP; el atacante no puede establecer troncal ni enviar VTP |

---

## 🎬 Video Demostración

> 🎬 **[▶ Ver demostración en YouTube](#)** ← *(https://www.youtube.com/watch?v=0oqqCOVIK5M&t=38s)*

### El video incluye:

- ✅ Topología en GNS3 con nombre y matrícula visibles
- ✅ Fecha y hora del sistema visibles en pantalla
- ✅ Cara y voz del estudiante durante toda la demostración
- ✅ Ejecución del ataque VTP: agregar y borrar VLAN
- ✅ Demostración de las contramedidas y verificación posterior
- ✅ Duración máxima: 5 minutos

---

## 📁 Estructura del Repositorio

```
VTP-Attack/
│
├── 📄 MiguelRamirezMeli_2025-1367_Script_P1.py   # Script del ataque
├── 📖 README.md                                   # Documentación técnica

```

---

<div align="center">

> ⚠️ **Aviso Legal:** Este script fue desarrollado exclusivamente con fines educativos dentro de un entorno de laboratorio controlado (GNS3). Su uso fuera de este contexto puede ser ilegal. El autor no se hace responsable del uso indebido de esta herramienta.

<br>

![Made with ❤️](https://img.shields.io/badge/Made%20with-❤️-red?style=for-the-badge)
![Educational](https://img.shields.io/badge/Purpose-Educational_Only-blue?style=for-the-badge)
![ITLA](https://img.shields.io/badge/ITLA-2025--1367-green?style=for-the-badge)

</div>
