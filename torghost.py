#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import getopt
import subprocess
import time
import signal
import threading
import itertools
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from contextlib import contextmanager

try:
    from requests import get, RequestException
    from stem import Signal as TorSignal
    from stem.control import Controller
    from packaging import version
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip3 install requests stem packaging") 
    sys.exit(1)

# ==================== CONFIGURATION ====================
VERSION = "3.3.0"
IP_API = "https://api.ipify.org/?format=json"
TOR_CHECK_API = "https://check.torproject.org/api/ip"
LATEST_RELEASE_API = "https://api.github.com/repos/INTELEON404/torghost/releases/latest"

TOR_USERS = ['debian-tor', 'tor', 'toranon', '_tor']
TOR_TRANS_PORT = "9040"
TOR_DNS_PORT = "5353"
TOR_CONTROL_PORT = "9051"

TORRC_PATH = '/etc/tor/torghostrc'
RESOLV_CONF = '/etc/resolv.conf'
RESOLV_BACKUP = '/etc/resolv.conf.torghost.bak'

NON_TOR_NETS = "192.168.0.0/16 10.0.0.0/8 172.16.0.0/12"

ALIGN_WIDTH = 55


# ==================== COLOR SCHEME ====================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    GREY = '\033[90m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    ENDC = '\033[0m'
    RESET = '\033[0m'


# ==================== ICONS & SYMBOLS ====================
class Icons:
    CHECK   = f"{Colors.GREEN}[+]{Colors.ENDC}"
    CROSS   = f"{Colors.RED}[-]{Colors.ENDC}"
    ARROW   = f"{Colors.CYAN}->{Colors.ENDC}"
    SKULL   = f"{Colors.RED}[!!]{Colors.ENDC}"
    SHIELD  = f"{Colors.GREEN}[*]{Colors.ENDC}"
    LOCK    = f"{Colors.YELLOW}[#]{Colors.ENDC}"
    UNLOCK  = f"{Colors.RED}[~]{Colors.ENDC}"
    GLOBE   = f"{Colors.BLUE}[@]{Colors.ENDC}"
    WARNING = f"{Colors.YELLOW}[!]{Colors.ENDC}"
    INFO    = f"{Colors.CYAN}[i]{Colors.ENDC}"
    ROCKET  = f"{Colors.MAGENTA}[>>]{Colors.ENDC}"
    FIRE    = f"{Colors.RED}[~]{Colors.ENDC}"


# ==================== SPINNER ANIMATION ====================
SPINNER_FRAMES = ['⠏', '⠛', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠍']
spinner_active = False
spinner_thread = None


def timestamp() -> str:
    return f'{Colors.GREY}[{time.strftime("%H:%M:%S")}]{Colors.ENDC}'


def animate_spinner(message: str):
    global spinner_active
    frames = itertools.cycle(SPINNER_FRAMES)
    while spinner_active:
        frame = next(frames)
        sys.stdout.write(f'\r{timestamp()} {Colors.YELLOW}{frame}{Colors.ENDC} {message.upper()}...')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\r' + ' ' * 100 + '\r')
    sys.stdout.flush()


def start_spinner(message: str):
    global spinner_active, spinner_thread
    spinner_active = True
    spinner_thread = threading.Thread(target=animate_spinner, args=(message,), daemon=True)
    spinner_thread.start()


def stop_spinner():
    global spinner_active
    spinner_active = False
    if spinner_thread:
        time.sleep(0.1)


# ==================== UI HELPERS ====================
def print_step(message: str, width: int = ALIGN_WIDTH):
    sys.stdout.write(f"{timestamp()} {Icons.ARROW} {message.upper():<{width}}")
    sys.stdout.flush()


def print_success():
    print(f" {Colors.GREEN}[DONE]{Colors.ENDC}")


def print_fail():
    print(f" {Colors.RED}[FAIL]{Colors.ENDC}")


def print_warning(message: str):
    print(f"{timestamp()} {Icons.WARNING} {Colors.YELLOW}{message}{Colors.ENDC}")


def print_error(message: str):
    print(f"{timestamp()} {Icons.CROSS} {Colors.RED}{message}{Colors.ENDC}")


def print_info(message: str):
    print(f"{timestamp()} {Icons.INFO} {Colors.CYAN}{message}{Colors.ENDC}")


def print_status_block(title: str, subtitle: str, fields: list, hints: list = None):
    """
    Print a clean status block without box-drawing characters.

    title    : e.g. "STATUS REPORT"
    subtitle : e.g. "TORGHOST ACTIVE - YOU ARE ANONYMOUS"
    fields   : list of (label, value, color) tuples
    hints    : optional list of plain hint strings
    """
    sep = f"{Colors.CYAN}{'=' * 60}{Colors.ENDC}"
    print(sep)
    print(f"  [ {Colors.BOLD}{Colors.WHITE}{title}{Colors.ENDC} ]  "
          f"[ {Colors.BOLD}{Colors.GREEN}{subtitle}{Colors.ENDC} ]")
    print(sep)
    for label, value, color in fields:
        print(f"  {Colors.CYAN}>{Colors.ENDC} {Colors.BOLD}{label:<14}{Colors.ENDC}: "
              f"{color}{Colors.BOLD}{value}{Colors.ENDC}")
    if hints:
        print()
        for hint in hints:
            print(f"  {Colors.GREY}{hint}{Colors.ENDC}")
    print(sep)


def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')


def print_logo():
    clear_screen()
    logo = f"""{Colors.RED}{Colors.BOLD}
                   ░▀█▀░█▀█░█▀▄░█▀▀░█░█░█▀█░█▀▀░▀█▀
                   ░░█░░█░█░█▀▄░█░█░█▀█░█░█░▀▀█░░█░
                   ░░▀░░▀▀▀░▀░▀░▀▀▀░▀░▀░▀▀▀░▀▀▀░░▀░
{Colors.ENDC}
    {Colors.CYAN}{'=' * 67}{Colors.ENDC}
    {Colors.WHITE}              ANONYMOUS ROUTING THROUGH TOR NETWORK{Colors.ENDC}
    {Colors.GREY}                 Version {VERSION} | By INTELEON404{Colors.ENDC}
    {Colors.CYAN}{'=' * 67}{Colors.ENDC}
"""
    print(logo)


def print_usage():
    print_logo()
    usage_text = f"""
    {Colors.BOLD}{Colors.WHITE}USAGE:{Colors.ENDC}
        sudo python3 torghost.py [OPTION]

    {Colors.BOLD}{Colors.WHITE}OPTIONS:{Colors.ENDC}
        {Colors.GREEN}-s, --start{Colors.ENDC}     {Colors.WHITE}START TORGHOST{Colors.ENDC}     Route all traffic through Tor
        {Colors.YELLOW}-r, --switch{Colors.ENDC}    {Colors.WHITE}SWITCH IDENTITY{Colors.ENDC}    Request new Tor exit node
        {Colors.RED}-x, --stop{Colors.ENDC}      {Colors.WHITE}STOP TORGHOST{Colors.ENDC}      Restore original connection
        {Colors.CYAN}-u, --update{Colors.ENDC}    {Colors.WHITE}CHECK UPDATE{Colors.ENDC}       Check for new version
        {Colors.MAGENTA}-i, --ip{Colors.ENDC}        {Colors.WHITE}SHOW IP{Colors.ENDC}            Display current IP address
        {Colors.BLUE}-h, --help{Colors.ENDC}      {Colors.WHITE}HELP MENU{Colors.ENDC}          Show this help message

    {Colors.BOLD}{Colors.WHITE}EXAMPLES:{Colors.ENDC}
        {Colors.GREY}# Start anonymous routing{Colors.ENDC}
        sudo python3 torghost.py --start

        {Colors.GREY}# Switch to new identity{Colors.ENDC}
        sudo python3 torghost.py --switch

        {Colors.GREY}# Stop and restore normal connection{Colors.ENDC}
        sudo python3 torghost.py --stop

    {Colors.BOLD}{Colors.YELLOW}SECURITY NOTES:{Colors.ENDC}
        * Always verify your IP after starting
        * Use HTTPS websites for maximum security
        * Some services may block Tor exit nodes
        * DNS leaks are prevented automatically
        * Kill switch active on failures

    {Colors.CYAN}{'=' * 67}{Colors.ENDC}
    """
    print(usage_text)


# ==================== SYSTEM CHECKS ====================
def check_root() -> bool:
    if os.geteuid() != 0:
        print_error("ROOT PRIVILEGES REQUIRED!")
        print(f"\n{Colors.YELLOW}Run with:{Colors.ENDC} {Colors.BOLD}sudo python3 torghost.py [OPTION]{Colors.ENDC}\n")
        return False
    return True


def detect_tor_user() -> Optional[str]:
    for user in TOR_USERS:
        try:
            result = subprocess.run(['id', '-u', user], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return user
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    return None


def get_tor_uid(tor_user: str) -> Optional[str]:
    try:
        result = subprocess.run(['id', '-ur', tor_user], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def check_dependencies() -> Tuple[bool, list]:
    required = ['tor', 'iptables']
    missing = [cmd for cmd in required if not shutil.which(cmd)]
    return len(missing) == 0, missing


def is_tor_running() -> bool:
    try:
        result = subprocess.run(['lsof', '-i', f':{TOR_CONTROL_PORT}', '-t'], capture_output=True, timeout=2)
        return result.returncode == 0
    except:
        try:
            result = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True, timeout=2)
            return f':{TOR_CONTROL_PORT}' in result.stdout
        except:
            return False


# ==================== NETWORK FUNCTIONS ====================
def get_ip(retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            response = get(IP_API, timeout=10)
            response.raise_for_status()
            return response.json()["ip"]
        except RequestException:
            if attempt < retries - 1:
                time.sleep(1)
            continue
    return "Unable to fetch"


def verify_tor_connection() -> Tuple[bool, str]:
    try:
        response = get(TOR_CHECK_API, timeout=10)
        data = response.json()
        return data.get("IsTor", False), data.get("IP", "Unknown")
    except:
        return False, "Unknown"


# ==================== FILE OPERATIONS ====================
@contextmanager
def atomic_write(filepath: str):
    temp_fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(filepath))
    try:
        with os.fdopen(temp_fd, 'w') as f:
            yield f
        shutil.move(temp_path, filepath)
    except:
        os.unlink(temp_path)
        raise


def backup_file(filepath: str, backup_path: str) -> bool:
    try:
        if os.path.exists(filepath):
            shutil.copy2(filepath, backup_path)
            return True
    except Exception as e:
        print_error(f"Failed to backup {filepath}: {e}")
    return False


def restore_file(backup_path: str, original_path: str) -> bool:
    try:
        if os.path.exists(backup_path):
            shutil.move(backup_path, original_path)
            return True
    except Exception as e:
        print_error(f"Failed to restore {original_path}: {e}")
    return False


# ==================== TOR CONFIGURATION ====================
def generate_torrc_config() -> str:
    return f"""# TorGhost Configuration
VirtualAddrNetwork 10.0.0.0/10
AutomapHostsOnResolve 1
TransPort {TOR_TRANS_PORT}
DNSPort {TOR_DNS_PORT}
ControlPort {TOR_CONTROL_PORT}
RunAsDaemon 1

# Security Enhancements
AvoidDiskWrites 1
HardwareAccel 1
SafeLogging 1
"""


def write_torrc_config() -> bool:
    try:
        config = generate_torrc_config()
        if os.path.exists(TORRC_PATH):
            with open(TORRC_PATH, 'r') as f:
                if config.strip() == f.read().strip():
                    return True
        with atomic_write(TORRC_PATH) as f:
            f.write(config)
        os.chmod(TORRC_PATH, 0o644)
        return True
    except Exception as e:
        print_error(f"Failed to write Torrc: {e}")
        return False


def configure_dns() -> bool:
    try:
        dns_config = "nameserver 127.0.0.1\n"
        if os.path.exists(RESOLV_CONF):
            with open(RESOLV_CONF, 'r') as f:
                if dns_config.strip() in f.read():
                    return True
        if not backup_file(RESOLV_CONF, RESOLV_BACKUP):
            print_warning("Could not backup resolv.conf")
        with atomic_write(RESOLV_CONF) as f:
            f.write(dns_config)
        return True
    except Exception as e:
        print_error(f"Failed to configure DNS: {e}")
        return False


# ==================== TOR DAEMON MANAGEMENT ====================
def stop_existing_tor():
    commands = [
        'systemctl stop tor 2>/dev/null',
        'service tor stop 2>/dev/null',
        'killall tor 2>/dev/null',
    ]
    for cmd in commands:
        subprocess.run(cmd, shell=True, capture_output=True)
    try:
        subprocess.run(f'fuser -k {TOR_CONTROL_PORT}/tcp', shell=True, capture_output=True, timeout=5)
    except:
        pass
    time.sleep(1)


def start_tor_daemon(tor_user: str) -> bool:
    try:
        subprocess.Popen(
            ['sudo', '-u', tor_user, 'tor', '-f', TORRC_PATH],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        for _ in range(60):
            if is_tor_running():
                time.sleep(2)
                return True
            time.sleep(0.5)
        print_error("Tor daemon failed to start within timeout")
        return False
    except Exception as e:
        print_error(f"Failed to start Tor daemon: {e}")
        return False


# ==================== IPTABLES MANAGEMENT ====================
def apply_iptables_rules(tor_uid: str) -> bool:
    rules = f"""
iptables -F
iptables -t nat -F
iptables -t mangle -F
iptables -X

iptables -t nat -A OUTPUT -m owner --uid-owner {tor_uid} -j RETURN
iptables -t nat -A OUTPUT -p udp --dport 53 -j REDIRECT --to-ports {TOR_DNS_PORT}

for NET in {NON_TOR_NETS} 127.0.0.0/8; do
    iptables -t nat -A OUTPUT -d $NET -j RETURN
done

iptables -t nat -A OUTPUT -p tcp --syn -j REDIRECT --to-ports {TOR_TRANS_PORT}
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

for NET in {NON_TOR_NETS} 127.0.0.0/8; do
    iptables -A OUTPUT -d $NET -j ACCEPT
done

iptables -A OUTPUT -m owner --uid-owner {tor_uid} -j ACCEPT
iptables -A OUTPUT -j REJECT
"""
    try:
        result = subprocess.run(rules, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except Exception as e:
        print_error(f"Failed to apply iptables rules: {e}")
        return False


def flush_iptables() -> bool:
    flush_commands = """
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT
iptables -F
iptables -t nat -F
iptables -t mangle -F
iptables -X
"""
    try:
        result = subprocess.run(flush_commands, shell=True, capture_output=True, timeout=10)
        return result.returncode == 0
    except Exception as e:
        print_error(f"Failed to flush iptables: {e}")
        return False


# ==================== MAIN FUNCTIONS ====================
def start_torghost():
    print_logo()
    print_info("INITIATING TORGHOST SEQUENCE...\n")

    print_step("CHECKING DEPENDENCIES")
    deps_ok, missing = check_dependencies()
    if not deps_ok:
        print_fail()
        print_error(f"Missing dependencies: {', '.join(missing)}")
        print(f"\n{Colors.YELLOW}Install with:{Colors.ENDC}")
        print(f"  Debian/Ubuntu: sudo apt install tor iptables")
        print(f"  Arch Linux:    sudo pacman -S tor iptables")
        print(f"  Fedora/RHEL:   sudo dnf install tor iptables\n")
        return
    print_success()

    print_step("DETECTING TOR USER")
    tor_user = detect_tor_user()
    if not tor_user:
        print_fail()
        print_error("Could not find Tor user on system")
        print(f"{Colors.YELLOW}Try installing Tor: sudo apt install tor{Colors.ENDC}")
        return
    print_success()
    print_info(f"Tor user detected: {Colors.BOLD}{tor_user}{Colors.ENDC}")

    tor_uid = get_tor_uid(tor_user)
    if not tor_uid:
        print_error("Could not get Tor UID")
        return

    print_step("CONFIGURING TORRC")
    if not write_torrc_config():
        print_fail()
        return
    print_success()

    print_step("CONFIGURING DNS RESOLVER")
    if not configure_dns():
        print_fail()
        print_warning("DNS configuration failed - possible leak risk")
        return
    print_success()

    print_step("STOPPING EXISTING TOR SERVICES")
    stop_existing_tor()
    print_success()

    print_step("STARTING TOR DAEMON")
    start_spinner("Bootstrapping Tor network")
    success = start_tor_daemon(tor_user)
    stop_spinner()

    if not success:
        print_step("STARTING TOR DAEMON")
        print_fail()
        print_error("Failed to start Tor daemon")
        print_warning("Restoring original settings...")
        restore_file(RESOLV_BACKUP, RESOLV_CONF)
        return
    print_step("STARTING TOR DAEMON")
    print_success()

    print_step("APPLYING FIREWALL RULES")
    if not apply_iptables_rules(tor_uid):
        print_fail()
        print_error("Failed to apply iptables rules")
        print_warning("Cleaning up...")
        stop_existing_tor()
        restore_file(RESOLV_BACKUP, RESOLV_CONF)
        return
    print_success()

    print_step("FETCHING NEW IP ADDRESS")
    start_spinner("Connecting to Tor network")
    time.sleep(3)
    new_ip = get_ip()
    stop_spinner()
    print_step("FETCHING NEW IP ADDRESS")
    print_success()

    print_step("VERIFYING TOR CONNECTION")
    start_spinner("Checking Tor status")
    is_tor, verified_ip = verify_tor_connection()
    stop_spinner()
    print_step("VERIFYING TOR CONNECTION")
    if is_tor:
        print_success()
    else:
        print_warning("Could not verify Tor connection")

    print("\n")
    print_status_block(
        title="STATUS REPORT",
        subtitle="TORGHOST ACTIVE - YOU ARE ANONYMOUS",
        fields=[
            ("YOUR IP",     new_ip,                              Colors.YELLOW),
            ("TOR STATUS",  "VERIFIED" if is_tor else "ACTIVE",  Colors.GREEN),
            ("TRAFFIC",     "All traffic routed through Tor",     Colors.WHITE),
        ],
        hints=[
            "Use 'sudo python3 torghost.py -r' to switch identity",
            "Use 'sudo python3 torghost.py -x' to stop torghost",
        ]
    )
    print()


def stop_torghost():
    stop_spinner()
    print_logo()
    print_warning("STOPPING TORGHOST...\n")

    print_step("RESTORING DNS SETTINGS")
    if restore_file(RESOLV_BACKUP, RESOLV_CONF):
        print_success()
    else:
        print_warning("No DNS backup found")
        try:
            with atomic_write(RESOLV_CONF) as f:
                f.write("nameserver 8.8.8.8\nnameserver 8.8.4.4\n")
            print_success()
        except:
            print_fail()

    print_step("FLUSHING IPTABLES RULES")
    if flush_iptables():
        print_success()
    else:
        print_fail()
        print_warning("Some iptables rules may remain")

    print_step("STOPPING TOR DAEMON")
    stop_existing_tor()
    print_success()

    print_step("RESTARTING NETWORK MANAGER")
    commands = [
        'systemctl restart NetworkManager 2>/dev/null',
        'service network-manager restart 2>/dev/null',
        'systemctl restart systemd-networkd 2>/dev/null'
    ]
    restarted = False
    for cmd in commands:
        result = subprocess.run(cmd, shell=True, capture_output=True)
        if result.returncode == 0:
            restarted = True
            break
    if restarted:
        print_success()
    else:
        print_warning("Network manager restart failed (may not be needed)")

    print_step("VERIFYING ORIGINAL IP")
    start_spinner("Fetching current IP")
    time.sleep(2)
    original_ip = get_ip()
    stop_spinner()
    print_step("VERIFYING ORIGINAL IP")
    print_success()

    print("\n")
    print_status_block(
        title="STATUS REPORT",
        subtitle="TORGHOST STOPPED - NORMAL CONNECTION",
        fields=[
            ("YOUR IP",    original_ip,                Colors.CYAN),
            ("TOR STATUS", "INACTIVE",                 Colors.RED),
            ("NOTE",       "Original connection restored", Colors.WHITE),
        ]
    )
    print()


def switch_identity():
    print_logo()
    print_info("REQUESTING NEW TOR IDENTITY...\n")

    if not is_tor_running():
        print_error("TorGhost is not running!")
        print(f"{Colors.YELLOW}Start it first:{Colors.ENDC} sudo python3 torghost.py -s\n")
        return

    print_step("CONNECTING TO TOR CONTROLLER")
    try:
        with Controller.from_port(port=int(TOR_CONTROL_PORT)) as controller:
            controller.authenticate()
            print_success()

            print_step("REQUESTING NEW CIRCUIT")
            controller.signal(TorSignal.NEWNYM)
            print_success()

    except Exception as e:
        print_fail()
        print_error(f"Failed to switch identity: {e}")
        return

    print_step("ESTABLISHING NEW CIRCUIT")
    start_spinner("Building new identity")
    time.sleep(5)
    stop_spinner()
    print_step("ESTABLISHING NEW CIRCUIT")
    print_success()

    print_step("FETCHING NEW IP ADDRESS")
    start_spinner("Verifying new identity")
    new_ip = get_ip()
    is_tor, _ = verify_tor_connection()
    stop_spinner()
    print_step("FETCHING NEW IP ADDRESS")
    print_success()

    print("\n")
    print_status_block(
        title="IDENTITY SWITCHED",
        subtitle="NEW IDENTITY ESTABLISHED",
        fields=[
            ("NEW IP",     new_ip,                             Colors.YELLOW),
            ("TOR STATUS", "VERIFIED" if is_tor else "ACTIVE", Colors.GREEN),
            ("NOTE",       "Previous identity discarded",       Colors.WHITE),
        ]
    )
    print()


def show_ip():
    print_logo()

    print_step("FETCHING IP ADDRESS")
    start_spinner("Retrieving network information")
    current_ip = get_ip()
    is_tor, _ = verify_tor_connection()
    tor_running = is_tor_running()
    stop_spinner()
    print_step("FETCHING IP ADDRESS")
    print_success()

    tor_status_val   = "ACTIVE (Verified)" if is_tor else "NOT ACTIVE"
    tor_status_color = Colors.GREEN if is_tor else Colors.RED
    daemon_val       = "RUNNING" if tor_running else "STOPPED"
    daemon_color     = Colors.GREEN if tor_running else Colors.RED

    fields = [
        ("YOUR IP",    current_ip,     Colors.YELLOW),
        ("TOR STATUS", tor_status_val, tor_status_color),
        ("DAEMON",     daemon_val,     daemon_color),
    ]

    hints = None
    if not is_tor and tor_running:
        hints = ["[!] Tor is running but connection is not verified"]

    print("\n")
    print_status_block(title="NETWORK STATUS", subtitle="CURRENT IP INFO", fields=fields, hints=hints)
    print()


def check_update():
    print_logo()
    print_info("CHECKING FOR UPDATES...\n")

    print_step("FETCHING LATEST VERSION")
    try:
        response = get(LATEST_RELEASE_API, timeout=10)
        response.raise_for_status()
        latest_version = response.json()["tag_name"].lstrip('v')
        print_success()

        print_info(f"Current version : {Colors.BOLD}{VERSION}{Colors.ENDC}")
        print_info(f"Latest version  : {Colors.BOLD}{latest_version}{Colors.ENDC}\n")

        if version.parse(latest_version) > version.parse(VERSION):
            print_status_block(
                title="UPDATE AVAILABLE",
                subtitle=f"VERSION {latest_version} IS READY",
                fields=[
                    ("CURRENT",  VERSION,                                         Colors.YELLOW),
                    ("LATEST",   latest_version,                                  Colors.GREEN),
                    ("DOWNLOAD", "https://github.com/INTELEON404/torghost",       Colors.CYAN),
                ],
                hints=[
                    "cd /tmp && git clone https://github.com/INTELEON404/torghost",
                    "cd torghost && sudo chmod +x torghost.py",
                ]
            )
        else:
            print_status_block(
                title="UPDATE CHECK",
                subtitle="TORGHOST IS UP TO DATE",
                fields=[
                    ("VERSION", VERSION, Colors.GREEN),
                    ("STATUS",  "Latest release installed", Colors.WHITE),
                ]
            )
        print()

    except RequestException:
        print_fail()
        print_error("Failed to check for updates")
        print_warning("Check your internet connection\n")
    except Exception as e:
        print_fail()
        print_error(f"Update check failed: {e}\n")


# ==================== SIGNAL HANDLER ====================
def signal_handler(signum, frame):
    stop_spinner()
    print(f"\n\n{timestamp()} {Icons.SKULL} {Colors.RED}{Colors.BOLD}INTERRUPT RECEIVED!{Colors.ENDC}")
    print_warning("Emergency shutdown initiated...\n")
    flush_iptables()
    stop_existing_tor()
    restore_file(RESOLV_BACKUP, RESOLV_CONF)
    print(f"{timestamp()} {Icons.INFO} {Colors.CYAN}Cleanup completed{Colors.ENDC}\n")
    sys.exit(0)


# ==================== MAIN ====================
def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if not check_root():
        sys.exit(1)

    if len(sys.argv) <= 1:
        print_usage()
        sys.exit(0)

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "srxhuia",
            ["start", "switch", "stop", "help", "update", "ip", "about"]
        )
    except getopt.GetoptError as e:
        print_error(f"Invalid option: {e}")
        print_usage()
        sys.exit(1)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_usage()
        elif opt in ("-s", "--start"):
            start_torghost()
        elif opt in ("-r", "--switch"):
            switch_identity()
        elif opt in ("-x", "--stop"):
            stop_torghost()
        elif opt in ("-i", "--ip"):
            show_ip()
        elif opt in ("-u", "--update"):
            check_update()
        else:
            print_usage()


if __name__ == "__main__":
    main()
