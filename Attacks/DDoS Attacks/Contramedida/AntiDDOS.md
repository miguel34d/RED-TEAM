![Estudiante](https://img.shields.io/badge/Estudiante-Miguel%20Ramirez%20Meli-blue?style=flat-square)
![Matricula](https://img.shields.io/badge/Matr%C3%ADcula-2025--1367-blue?style=flat-square)
![Materia](https://img.shields.io/badge/Materia-Hacker%20%C3%89tico%202-orange?style=flat-square)
![Profesor](https://img.shields.io/badge/Profesor-Carlos%20Edwin-orange?style=flat-square)
![Institucion](https://img.shields.io/badge/Instituci%C3%B3n-ITLA-lightgrey?style=flat-square)
![Estado](https://img.shields.io/badge/Estado-Completado-success?style=flat-square)

# Guía: Detección y Mitigación de DDoS con Anti DDoS Guardian

## Objetivo

Instalar Anti DDoS Guardian en la máquina víctima, detectar en tiempo real un ataque SYN flood entrante, y aplicar una contramedida (bloqueo de IP).

## Entorno de laboratorio

| Rol | Máquina | Dirección IP |
|---|---|---|
| Atacante | Kali Linux | 10.13.67.13 |
| Víctima (protegida) | Windows 10 | 10.13.67.14 |

## Herramienta

**Anti DDoS Guardian** (BeeThink) — software de protección contra ataques DDoS/DoS para servidores Windows. Fuente oficial: [beethink.com/antiddos.htm](https://www.beethink.com/antiddos.htm)

---

## Paso 1: Descargar el instalador

1. Ir al sitio oficial del fabricante: `https://www.beethink.com/antiddos.htm`
2. Descargar el archivo **Anti_DDoS_Guardian_setup.exe** en la máquina Windows 10 (víctima).

## Paso 2: Ejecutar el instalador

3. Hacer doble clic en **Anti_DDoS_Guardian_setup.exe**.
4. Si aparece la ventana de **User Account Control** → clic en **Yes**.
5. Si aparece **Open File - Security Warning** → clic en **Run**.
6. En la ventana **Setup - Anti DDoS Guardian**, clic en **Next**.

## Paso 3: Configurar opciones de instalación

7. En la ventana **Stop Windows Remote Desktop Brute Force**: desmarcar la opción **Install Stop RDP Brute Force** → clic **Next**.
8. En la ventana **Select Additional Tasks**: marcar la opción **Create a desktop shortcut** → clic **Next**.
9. En la ventana **Ready to Install**: clic en **Install**.
10. Al finalizar la instalación, en la ventana **Completing the Anti DDoS Guardian Setup Wizard**: desmarcar **Launch Mini IP Blocker** → clic **Finish**.

## Paso 4: Configurar el asistente Anti-DDoS Wizard

Al terminar la instalación se abre automáticamente el **Anti-DDoS Wizard**, donde se deja la configuración recomendada por defecto en cada pantalla, haciendo clic en **Continue(C)** en todas:

11. **Ingress TCP connection request rate:** máximo de solicitudes de conexión TCP entrantes = `3` por segundo, por cada IP cliente. Clic **Continue**.
12. **TCP concurrent connection number:** máximo de conexiones TCP simultáneas por IP cliente = `15`. Clic **Continue**.
13. **Bandwidth:** ancho de banda máximo de ingreso y egreso = `524288` KB/s cada uno. Clic **Continue**.
14. **UDP packet number:** máximo de paquetes UDP entrantes por segundo = `1000000`. Clic **Continue**.
15. **ICMP packet number:** máximo de paquetes ICMP entrantes por segundo = `1000000`. Clic **Continue**.
16. **TCP half connection:** máximo de conexiones TCP semiabiertas (*half-open*) concurrentes = `50`. Este es el parámetro clave frente a un ataque SYN flood, ya que limita directamente el recurso que este tipo de ataque intenta agotar. Clic **Continue**.
17. **Client computer number:** máximo de direcciones IP cliente concurrentes = `1500`. Clic **Continue**.
18. Finalizar el asistente.

## Paso 5: Abrir Anti DDoS Guardian

19. Hacer clic en **Show hidden icons** en la esquina inferior derecha del Desktop.
20. Clic en el ícono de **Anti DDoS Guardian**.
21. Se abre la ventana principal mostrando el tráfico entrante/saliente en tiempo real, con columnas: Tiempo, Outgoing, Incoming, Local IP Address, Remote IP Address, Puerto, Protocolo e Información.
22. En este punto, el tráfico mostrado corresponde al tráfico normal de la red (DNS, NetBIOS, consultas de Windows, etc.) — esta es la línea base (estado antes del ataque).

## Paso 6: Lanzar el ataque desde Kali

23. En Kali, abrir una terminal.
24. Entrar como root:
    ```bash
    sudo su
    ```
25. Ejecutar el SYN flood hacia la víctima:
    ```bash
    hping3 -S 10.13.67.14 -p 445 --flood
    ```
26. Dejarlo corriendo (no es necesario detenerlo de inmediato, ya que se usará para la verificación de bloqueo más adelante).

## Paso 7: Detectar el ataque en Anti DDoS Guardian

27. Cambiar a la ventana de Windows 10 con Anti DDoS Guardian abierto.
28. Observar cómo aparece una nueva fila marcada en **color rojo**, correspondiente a la IP atacante, mostrando un conteo de paquetes **Incoming** extremadamente alto (del orden de millones) en el puerto 445, muy por encima del resto del tráfico normal (que se mantiene en decenas o cientos de paquetes).

## Paso 8: Aplicar la contramedida (bloqueo de IP)

29. Hacer doble clic sobre la fila marcada en rojo (la sesión del ataque).
30. Se abre la ventana **Anti DDoS Guardian Traffic Detail Viewer**, mostrando el contenido crudo de la sesión, la IP remota y el total de bytes entrantes.
31. En el panel izquierdo de esa ventana, hacer clic en **Block IP**.
32. Verificar que el estado de esa sesión cambie (el indicador pasa a rojo de forma permanente, señalando que la IP quedó bloqueada).

## Paso 9: Verificar que el bloqueo funcionó

33. Volver a Kali y relanzar el mismo ataque:
    ```bash
    hping3 -S 10.13.67.14 -p 445 --flood
    ```
34. Observar en Anti DDoS Guardian que el contador de paquetes entrantes de esa IP ya no incrementa con normalidad, confirmando que el bloqueo es efectivo.
35. Detener el ataque en Kali con `Ctrl + C`.

## Paso 10: Finalizar

36. Cerrar Wireshark y Anti DDoS Guardian.
37. (Opcional) Desinstalar Anti DDoS Guardian desde **Panel de Control → Programas → Programas y características**, si la máquina es de uso compartido.

---

## Explicación: cómo mitiga el problema

Anti DDoS Guardian actúa como una capa adicional sobre la pila TCP/IP de Windows, imponiendo límites configurables **antes** de que el sistema operativo llegue a saturarse. El parámetro de **conexiones TCP semiabiertas (half-open = 50)** es el más relevante frente a un SYN flood: cuando una IP supera ese umbral, Anti DDoS Guardian ignora sus nuevas solicitudes en lugar de dejarlas llegar al stack TCP/IP real de Windows y consumir la tabla de conexiones del sistema operativo. Esto evita que el ataque llegue a agotar el mismo recurso (la tabla de conexiones semiabiertas) que explotan tanto hping3 como Metasploit.

## Conclusión

Anti DDoS Guardian demostró ser una herramienta efectiva de defensa perimetral a nivel de host, al identificar automáticamente el patrón anómalo de tráfico basado en el umbral de conexiones semiabiertas configurado, y permitir el bloqueo inmediato de la IP atacante, restaurando así la disponibilidad del servicio para los usuarios legítimos.

Como recomendación adicional, se sugiere complementar esta protección a nivel de host con medidas a nivel de red (firewalls perimetrales, listas de control de acceso y servicios de mitigación de DDoS basados en la nube), especialmente ante ataques distribuidos desde múltiples orígenes simultáneos como el simulado con Metasploit, donde el bloqueo manual de una sola IP resultaría insuficiente.

---
**Nombre:** Miguel Ramirez Meli&nbsp;&nbsp;&nbsp;&nbsp;**ID:** 2025-1367
