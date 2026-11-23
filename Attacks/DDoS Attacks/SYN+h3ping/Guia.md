[01-hping3.md](https://github.com/user-attachments/files/35276079/01-hping3.md)![Estudiante](https://img.shields.io/badge/Estudiante-Miguel%20Ramirez%20Meli-blue?style=flat-square)
![Matricula](https://img.shields.io/badge/Matr%C3%ADcula-2025--1367-blue?style=flat-square)
![Materia](https://img.shields.io/badge/Materia-Hacker%20%C3%89tico%202-orange?style=flat-square)
![Profesor](https://img.shields.io/badge/Profesor-Carlos%20Edwin-orange?style=flat-square)
![Institucion](https://img.shields.io/badge/Instituci%C3%B3n-ITLA-lightgrey?style=flat-square)
![Estado](https://img.shields.io/badge/Estado-Completado-success?style=flat-square)

# Guía: Ataque SYN Flood con hping3

## Objetivo

Ejecutar un ataque DoS (SYN Flooding) sobre un host Windows utilizando hping3 desde Kali Linux, y explicar el efecto que produce sobre el sistema operativo víctima.

## Entorno de laboratorio

| Rol | Máquina | Dirección IP |
|---|---|---|
| Atacante | Kali Linux | 10.13.67.13 |
| Víctima | Windows 10 | 10.13.67.14 |

## Herramienta

**hping3** — herramienta de línea de comandos para creación y manipulación de paquetes TCP/IP, usada para auditoría de redes, pruebas de firewall y generación de tráfico de estrés.

---

## Paso 1: Preparar la máquina víctima (Windows 10) con Wireshark

1. En Windows 10, abrir el buscador de Windows y escribir `wireshark`.
2. Clic en **Open** para lanzar la aplicación.
3. En la ventana **Wireshark Network Analyzer**, hacer doble clic sobre la interfaz de red principal (**Ethernet**) para iniciar la captura del tráfico.
4. Dejar Wireshark corriendo en segundo plano durante todo el procedimiento.

## Paso 2: Confirmar la dirección IP de la víctima

5. En Windows 10, abrir **cmd** o **PowerShell**.
6. Ejecutar:
   ```
   ipconfig
   ```
7. Anotar la dirección IPv4 de la interfaz activa (en este caso, `10.13.67.14`).

## Paso 3: Identificar un puerto abierto en la víctima

8. En Kali, abrir una terminal.
9. Entrar como usuario root:
   ```bash
   sudo su
   ```
10. Ingresar la contraseña cuando se solicite.
11. Escanear los puertos comunes de un host Windows:
    ```bash
    nmap -p 135,139,445,3389,5985 10.13.67.14
    ```
    O realizar un escaneo general:
    ```bash
    nmap 10.13.67.14
    ```
12. Resultado obtenido:
    ```
    PORT     STATE SERVICE
    135/tcp  open  msrpc
    139/tcp  open  netbios-ssn
    445/tcp  open  microsoft-ds
    3389/tcp open  ms-wbt-server
    ```
13. Se selecciona el puerto **445** (SMB) como objetivo del ataque por tratarse de un servicio activo real en la víctima.

## Paso 4: Ejecutar el ataque SYN Flood

14. En la terminal de Kali (ya como root), ejecutar:
    ```bash
    hping3 -S 10.13.67.14 -p 445 --flood
    ```

    | Parámetro | Función |
    |---|---|
    | `-S` | Activa la bandera SYN en los paquetes enviados |
    | `-p 445` | Define el puerto de destino |
    | `--flood` | Envía paquetes al máximo de velocidad posible, sin esperar respuesta |

15. La terminal mostrará:
    ```
    HPING 10.13.67.14 (eth0 10.13.67.14): S set, 40 headers + 0 data bytes
    hping in flood mode, no replies will be shown
    ```
16. Dejar el ataque corriendo durante 10-20 segundos.
17. Detener el ataque con:
    ```
    Ctrl + C
    ```
18. Se mostrará la estadística final del envío (paquetes transmitidos, recibidos y porcentaje de pérdida).

## Paso 5: Verificar el efecto en la víctima

19. Cambiar a la ventana de **Windows 10**.
20. Observar en Wireshark el volumen masivo de paquetes `TCP [SYN]` entrantes desde la IP de Kali (`10.13.67.13`) hacia el puerto 445.
21. Notar si el sistema se percibe más lento al interactuar con él.

---

## Explicación: qué ocurre del lado de Windows

Toda conexión TCP normal se establece mediante un *three-way handshake*:

1. El cliente envía un paquete **SYN**.
2. El servidor (Windows 10) responde con **SYN-ACK** y reserva una entrada en su tabla de conexiones (TCB) en estado **SYN_RECEIVED**, dentro de la cola de conexiones semiabiertas (*backlog queue*), esperando el `ACK` final.
3. El cliente responde con **ACK**, completando la conexión.

En este ataque, Kali **nunca envía el ACK final**. Como los paquetes SYN llegan a una velocidad muchísimo mayor de la que el sistema libera las conexiones vencidas (por timeout), la cola de conexiones semiabiertas se satura rápidamente. Una vez saturada, Windows **descarta nuevas solicitudes SYN legítimas** porque ya no tiene espacio en la tabla para procesarlas — esto produce la denegación de servicio.

Adicionalmente, procesar miles de paquetes SYN por segundo consume ciclos de CPU y memoria, generando lentitud generalizada del sistema, no solo del puerto atacado.

En Wireshark se evidenció exactamente este comportamiento: paquetes `[SYN]` entrantes masivos, respuestas `[SYN, ACK]` generadas por Windows por cada uno, y cierres forzados con `[RST]` cuando el sistema finalmente descartaba las conexiones no completadas.

## Conclusión

El ataque demuestra la vulnerabilidad estructural del *three-way handshake* de TCP frente a un flujo masivo y unidireccional de paquetes SYN desde una única IP de origen. Al no usar spoofing, este tipo de ataque es relativamente sencillo de identificar y bloquear a nivel de firewall mediante reglas basadas en la IP de origen o en límites de tasa de conexión por IP.

---
**Nombre:** Miguel Ramirez Meli&nbsp;&nbsp;&nbsp;&nbsp;**ID:** 2025-1367
