![Estudiante](https://img.shields.io/badge/Estudiante-Miguel%20Ramirez%20Meli-blue?style=flat-square)
![Matricula](https://img.shields.io/badge/Matr%C3%ADcula-2025--1367-blue?style=flat-square)
![Materia](https://img.shields.io/badge/Materia-Hacker%20%C3%89tico%202-orange?style=flat-square)
![Profesor](https://img.shields.io/badge/Profesor-Carlos%20Edwin-orange?style=flat-square)
![Institucion](https://img.shields.io/badge/Instituci%C3%B3n-ITLA-lightgrey?style=flat-square)
![Estado](https://img.shields.io/badge/Estado-Completado-success?style=flat-square)

# Guía: Ataque DoS con Raven-Storm

## Objetivo

Instalar y ejecutar Raven-Storm desde Kali Linux para realizar un ataque DoS de Capa 4 (TCP/UDP) contra un host Windows, y comparar su comportamiento con los ataques anteriores (hping3 y Metasploit).

## Entorno de laboratorio

| Rol | Máquina | Dirección IP |
|---|---|---|
| Atacante | Kali Linux | 10.13.67.13 |
| Víctima | Windows 10 | 10.13.67.14 |

## Herramienta

**Raven-Storm** — toolkit de DDoS en Python3 para pruebas de penetración, con ataques en Capa 3 (red), Capa 4 (transporte, TCP/UDP) y Capa 7 (aplicación, HTTP). Repositorio: `github.com/Tmpertor/Raven-Storm`

---

## Paso 1: Preparar la máquina víctima con Wireshark

1. En Windows 10, abrir Wireshark.
2. Iniciar captura en la interfaz **Ethernet**.
3. Dejarlo corriendo en segundo plano.

## Paso 2: Instalar Raven-Storm en Kali

4. En Kali, abrir una terminal como root:
   ```bash
   sudo su
   ```
5. Instalar la herramienta con el script oficial:
   ```bash
   curl -s https://raw.githubusercontent.com/Taguar258/Raven-Storm/master/install.sh | sudo bash -s
   ```
6. Confirmar que la instalación terminó sin errores.

## Paso 3: Lanzar Raven-Storm

7. Ejecutar la herramienta:
   ```bash
   sudo rst
   ```
8. Se abre el menú principal de Raven-Storm, mostrando los módulos disponibles por capa (L3, L4, L7).

## Paso 4: Cargar el módulo de Capa 4

9. Para cargar el módulo que trabaja sobre TCP/UDP, escribir:
   ```
   l4
   ```

## Paso 5: Configurar el ataque

10. Definir la IP objetivo:
    ```
    ip 10.13.67.14
    ```
11. Definir el puerto objetivo:
    ```
    port 445
    ```
12. Definir el número de hilos (threads) a usar:
    ```
    threads 2000
    ```
    > **Nota importante:** en la primera ejecución se configuró con `threads 20000`. Esto saturó el límite de procesos (`fork`) de la propia máquina Kali, impidiendo detener el ataque correctamente (ver Paso 7). Se recomienda usar un valor moderado (1000-2000) para fines de laboratorio.

## Paso 6: Ejecutar el ataque

13. Iniciar el ataque:
    ```
    run
    ```
14. Si pide confirmación, responder:
    ```
    Y
    ```
15. Dejarlo correr unos 15-20 segundos.
16. Detener con `Ctrl + C` (no usar `Ctrl + Z`, ver explicación abajo).

## Paso 7: Incidente durante la detención del ataque

Durante la primera ejecución, al intentar detener el ataque se presionó por error `Ctrl + Z` en vez de `Ctrl + C`. Esto generó el siguiente comportamiento:

```
Target 10.13.67.14 with port 445 not accepting request!
^Z
zsh: suspended  sudo rst
_zsh_autosuggest_bind_widgets:15: fork failed: resource temporarily unavailable
```

**Causas identificadas:**

- `Ctrl + Z` no termina el proceso, solo lo **suspende** (lo pausa en segundo plano, pero sigue reservando recursos).
- Con `threads 20000` activos, la máquina Kali alcanzó su límite de procesos simultáneos (`ulimit -u`), provocando el error `fork failed: resource temporarily unavailable` — el sistema ya no podía crear ni siquiera un proceso nuevo.
- El mensaje repetido `Target ... not accepting request!` indica que, para ese momento, el objetivo ya no estaba aceptando las conexiones del ataque.

**Solución aplicada:**

17. Terminar el proceso suspendido correctamente:
    ```bash
    kill -9 %1
    ```
18. Verificar que no quedaran procesos huérfanos:
    ```bash
    pkill -9 -f rst
    ps aux | grep python3
    ```
19. Revisar el límite de procesos del sistema:
    ```bash
    ulimit -u
    ```
20. Repetir el ataque con un número de threads reducido (Paso 5, punto 12).

## Paso 8: Verificar el efecto en la víctima

21. Cambiar a Windows 10 y revisar Wireshark.
22. Observar el volumen de paquetes TCP/UDP entrantes hacia el puerto 445, generados por los múltiples hilos simultáneos.
23. Notar si el sistema se percibe más lento.

---

## Explicación: qué ocurre del lado de Windows

A diferencia de hping3 (que usa un solo proceso enviando paquetes) o Metasploit (que aleatoriza la IP de origen), Raven-Storm genera el ataque mediante **múltiples hilos (threads) simultáneos**, cada uno abriendo y manteniendo conexiones hacia el objetivo. Con miles de hilos, el sistema atacante simula una carga equivalente a muchos clientes conectándose al mismo tiempo, aunque todos provengan de la misma IP de origen (a menos que se combine con múltiples instancias tipo botnet).

Esto agota tanto la cola de conexiones semiabiertas del host víctima como sus recursos de CPU y memoria para procesar cada hilo entrante, produciendo el mismo efecto de denegación de servicio, pero con un volumen de tráfico generado mucho mayor en menos tiempo que con hping3.

## Explicación: qué ocurre del lado del atacante (Kali)

El incidente del Paso 7 evidencia que Raven-Storm no solo pone en riesgo al objetivo: un número de threads mal dimensionado puede agotar los recursos de la **propia máquina atacante**. Cada thread requiere crear un proceso o hilo del sistema operativo; si ese número supera el límite configurado en Kali (`ulimit -u`), el sistema deja de poder crear procesos nuevos, afectando incluso a herramientas básicas de la terminal (como el autosugerido de zsh, visible en el error `fork failed`).

## Conclusión

Raven-Storm demuestra cómo la multiplicación de hilos de ataque, incluso desde un solo origen, puede generar una carga de tráfico comparable a un ataque distribuido. A diferencia de Metasploit, el tráfico aquí sigue viniendo de una única IP real, por lo que un bloqueo por IP (como el aplicado con Anti DDoS Guardian) seguiría siendo efectivo — pero el límite de conexiones semiabiertas por IP debe ser lo suficientemente bajo para detectar el patrón antes de que el volumen de hilos sature el sistema.

Adicionalmente, esta práctica mostró que el riesgo no es unidireccional: una configuración descuidada (un número de threads excesivo) puede terminar afectando también al equipo atacante, lo cual resalta la importancia de dimensionar correctamente los parámetros de la herramienta antes de ejecutarla, incluso en un entorno de laboratorio controlado.

---
**Nombre:** Miguel Ramirez Meli&nbsp;&nbsp;&nbsp;&nbsp;**ID:** 2025-1367
