#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import getopt
from requests import get
import subprocess
import time
import signal
from stem import Signal
from stem.control import Controller
from packaging import version
import threading
import itertools

VERSION = "3.2.0"
IP_API = "https://api.ipify.org/?format=json"
LATEST_RELEASE_API = "https://api.github.com/repos/INTELEON404/torghost/releases/latest"

# === CONFIGURATION ===
ALIGN_WIDTH = 50  # Alignment width for straight lines

class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    WHITE = '\033[97m'
    GREY = '\033[90m'
    RED = '\033[31m'

# SYMBOLS & ICONS
INFO = f"{bcolors.CYAN}➜{bcolors.ENDC}"
SKULL = f"{bcolors.FAIL}☠{bcolors.ENDC}"

# BRAILLE SPINNER
spinner = itertools.cycle(['⠏', '⠛', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠍'])
stop_spinner = False

def t():
    # Styled Timestamp
    return f'{bcolors.GREY}[{time.strftime("%H:%M:%S")}]{bcolors.ENDC}'

# -- VISUAL HELPERS --
def print_step(message):
    """Prints a step in UPPERCASE with alignment, waiting for status."""
    # Convert message to uppercase as requested
    msg_upper = message.upper()
    sys.stdout.write(f"{t()} {INFO} {msg_upper:<{ALIGN_WIDTH}}")
    sys.stdout.flush()

def print_success():
    """Prints [DONE] in Green at the end of the line."""
    print(f" {bcolors.GREEN}[DONE]{bcolors.ENDC}")

def print_fail():
    """Prints [FAILED] in Red at the end of the line."""
    print(f" {bcolors.FAIL}[FAILED]{bcolors.ENDC}")

def print_box(lines):
    """Prints a beautiful box around a list of text lines."""
    length = max(len(line) for line in lines) + 6
    print(bcolors.CYAN + "╔" + "═" * length + "╗" + bcolors.ENDC)
    for line in lines:
        print(bcolors.CYAN + "║   " + bcolors.WHITE + f"{line:<{length-6}}" + bcolors.CYAN + "   ║" + bcolors.ENDC)
    print(bcolors.CYAN + "╚" + "═" * length + "╝" + bcolors.ENDC)

# -- ANIMATION --
def animate(message):
    global stop_spinner
    while not stop_spinner:
        for frame in spinner:
            if stop_spinner: break
            # Message is also uppercase in animation
            sys.stdout.write(f"\r{t()} {bcolors.WARNING}{frame}{bcolors.ENDC} {message.upper()} ")
            sys.stdout.flush()
            time.sleep(0.05)
    sys.stdout.write("\r" + " " * 80 + "\r")

def start_animation(msg):
    global stop_spinner
    stop_spinner = False
    t = threading.Thread(target=animate, args=(msg,))
    t.daemon = True
    t.start()

def stop_animation():
    global stop_spinner
    stop_spinner = True
    time.sleep(0.1)

def sigint_handler(signum, frame):
    stop_animation()
    print(f"\n{t()} {SKULL} {bcolors.FAIL}INTERRUPTED! FORCE STOPPING...{bcolors.ENDC}")
    stop_torghost()

def logo():
    os.system('clear')
    print(bcolors.RED + bcolors.BOLD)
    print("""
      ░▀█▀░█▀█░█▀▄░█▀▀░█░█░█▀█░█▀▀░▀█▀
      ░░█░░█░█░█▀▄░█░█░█▀█░█░█░▀▀█░░█░
      ░░▀░░▀▀▀░▀░▀░▀▀▀░▀░▀░▀▀▀░▀▀▀░░▀░
           v{V} - MOD BY INTELEON404
    """.format(V=VERSION).upper())
    print(bcolors.ENDC)

def usage():
    logo()
    # Commands are lowercase, descriptions are UPPERCASE
    print(f"""
    {bcolors.WHITE}COMMANDS:{bcolors.ENDC}
    {bcolors.CYAN}-s --start{bcolors.ENDC}      START TORGHOST (ROUTE ALL TRAFFIC)
    {bcolors.CYAN}-r --switch{bcolors.ENDC}     REQUEST NEW TOR EXIT NODE (NEW IP)
    {bcolors.CYAN}-x --stop{bcolors.ENDC}       STOP TORGHOST (RESTORE DEFAULT)
    {bcolors.CYAN}-h --help{bcolors.ENDC}       SHOW THIS HELP MENU
    {bcolors.CYAN}-u --update{bcolors.ENDC}     CHECK FOR UPDATES
    """)
    sys.exit()

def ip():
    try:
        return get(IP_API, timeout=5).json()["ip"]
    except:
        return "Unknown"

def check_root():
    if os.geteuid() != 0:
        print(f"{bcolors.FAIL}ERROR: ROOT PRIVILEGES REQUIRED!{bcolors.ENDC}")
        print(f"Try running with: {bcolors.BOLD}sudo python3 torghost.py{bcolors.ENDC}")
        sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

TorrcCfgString = """
VirtualAddrNetwork 10.0.0.0/10
AutomapHostsOnResolve 1
TransPort 9040
DNSPort 5353
ControlPort 9051
RunAsDaemon 1
"""
resolvString = 'nameserver 127.0.0.1'
Torrc = '/etc/tor/torghostrc'
resolv = '/etc/resolv.conf'

def start_torghost():
    logo()
    os.system('cp /etc/resolv.conf /etc/resolv.conf.bak 2>/dev/null')

    # 1. TORRC CONFIG
    print_step("Checking Torrc Configuration")
    if os.path.exists(Torrc) and TorrcCfgString in open(Torrc).read():
        print_success()
    else:
        sys.stdout.write("\r")
        start_animation("WRITING TORRC CONFIG")
        with open(Torrc, 'w') as f: f.write(TorrcCfgString)
        stop_animation()
        print_step("Writing Torrc Configuration")
        print_success()

    # 2. DNS CONFIG
    print_step("Configuring DNS (resolv.conf)")
    if resolvString in open(resolv).read():
        print_success()
    else:
        with open(resolv, 'w') as f: f.write(resolvString)
        print_success()

    # 3. STOPPING OLD SERVICES
    os.system('systemctl stop tor >/dev/null 2>&1')
    os.system('fuser -k 9051/tcp >/dev/null 2>&1')

    # 4. STARTING TOR
    sys.stdout.write("\r")
    start_animation("STARTING TOR DAEMON")
    os.system('sudo -u debian-tor tor -f /etc/tor/torghostrc >/dev/null 2>&1 &')
    
    for i in range(20): 
        if os.system('fuser 9051/tcp >/dev/null 2>&1') == 0:
            break
        time.sleep(0.2)
    
    stop_animation()
    print_step("Starting Tor Daemon")
    print_success()

    # 5. IPTABLES
    sys.stdout.write("\r")
    start_animation("APPLYING FIREWALL RULES")
    TOR_UID = subprocess.getoutput('id -ur debian-tor')
    iptables_rules = f"""
NON_TOR="192.168.1.0/24 192.168.0.0/24"
TOR_UID={TOR_UID}
TRANS_PORT="9040"
iptables -F
iptables -t nat -F
iptables -t nat -A OUTPUT -m owner --uid-owner $TOR_UID -j RETURN
iptables -t nat -A OUTPUT -p udp --dport 53 -j REDIRECT --to-ports 5353
for NET in $NON_TOR 127.0.0.0/9 127.128.0.0/10; do iptables -t nat -A OUTPUT -d $NET -j RETURN; done
iptables -t nat -A OUTPUT -p tcp --syn -j REDIRECT --to-ports $TRANS_PORT
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
for NET in $NON_TOR 127.0.0.0/8; do iptables -A OUTPUT -d $NET -j ACCEPT; done
iptables -A OUTPUT -m owner --uid-owner $TOR_UID -j ACCEPT
iptables -A OUTPUT -j REJECT
"""
    os.system(iptables_rules)
    stop_animation()
    print_step("Routing Traffic via IPTables")
    print_success()

    # 6. FETCH IP
    sys.stdout.write("\r")
    start_animation("FETCHING NEW PUBLIC IP")
    current_ip = ip()
    stop_animation()
    
    # FINAL OUTPUT
    print("\n")
    print_box([
        f"STATUS: {bcolors.GREEN}SECURE & ANONYMOUS{bcolors.WHITE}",
        f"NEW IP: {bcolors.WARNING}{current_ip}{bcolors.WHITE}",
        "TRAFFIC IS NOW ROUTED THROUGH TOR"
    ])
    print("\n")

def stop_torghost():
    stop_animation()
    print(f"\n{t()} {bcolors.WARNING}STOPPING TORGHOST SERVICES...{bcolors.ENDC}")

    print_step("Restoring DNS Settings")
    os.system('mv /etc/resolv.conf.bak /etc/resolv.conf 2>/dev/null || true')
    print_success()

    print_step("Flushing IPTables Rules")
    os.system('iptables -F; iptables -t nat -F; iptables -t mangle -F; iptables -X; iptables -P INPUT ACCEPT; iptables -P FORWARD ACCEPT; iptables -P OUTPUT ACCEPT')
    os.system('fuser -k 9051/tcp >/dev/null 2>&1')
    print_success()

    print_step("Restarting Network Manager")
    os.system('systemctl restart NetworkManager 2>/dev/null || true')
    print_success()

    print("\n")
    start_animation("VERIFYING ORIGINAL IP")
    real_ip = ip()
    stop_animation()
    
    print_box([
        f"STATUS: {bcolors.FAIL}DISCONNECTED{bcolors.WHITE}",
        f"REAL IP: {bcolors.CYAN}{real_ip}{bcolors.WHITE}",
        "YOUR ORIGINAL CONNECTION IS RESTORED"
    ])
    print("\n")

def switch_tor():
    stop_animation()
    print(f"{t()} {INFO} REQUESTING NEW CIRCUIT...")
    start_animation("CHANGING IDENTITY")

    try:
        with Controller.from_port(port=9051) as c:
            c.authenticate()
            c.signal(Signal.NEWNYM)
        time.sleep(2)
        stop_animation()
        print(f"{t()} {INFO} {'IDENTITY SWITCHED SUCCESSFULLY':<{ALIGN_WIDTH}} {bcolors.GREEN}[DONE]{bcolors.ENDC}")
    except:
        stop_animation()
        print(f"{t()} {INFO} {'FAILED TO SWITCH IDENTITY':<{ALIGN_WIDTH}} {bcolors.FAIL}[FAILED]{bcolors.ENDC}")
        return

    start_animation("FETCHING NEW IP ADDRESS")
    new_ip = ip()
    stop_animation()
    print_box([
        f"NEW IDENTITY ESTABLISHED",
        f"IP ADDRESS: {bcolors.WARNING}{new_ip}{bcolors.WHITE}"
    ])

def check_update():
    print(f"{t()} {INFO} CHECKING FOR UPDATES...")
    try:
        new = get(LATEST_RELEASE_API).json()["tag_name"][1:]
        if version.parse(new) > version.parse(VERSION):
            print(f"{t()} {bcolors.GREEN}NEW UPDATE AVAILABLE: v{new}{bcolors.ENDC}")
            if input(f"{t()} DOWNLOAD & INSTALL? [Y/N]: ").strip().lower() in ['','y','yes']:
                os.system('cd /tmp && rm -rf torghost && git clone https://github.com/SusmithKrishnan/torghost && cd torghost && sudo ./build.sh')
        else:
            print(f"{t()} {INFO} {'TORGHOST IS UP TO DATE':<{ALIGN_WIDTH}} {bcolors.GREEN}[DONE]{bcolors.ENDC}")
    except:
        print(f"{t()} {SKULL} {bcolors.FAIL}UPDATE CHECK FAILED (No Internet?){bcolors.ENDC}")

def main():
    check_root()
    if len(sys.argv) <= 1:
        usage()
    try:
        opts, _ = getopt.getopt(sys.argv[1:], "srxhu", ["start","switch","stop","help","update"])
    except:
        usage()
    for o, a in opts:
        if o in ("-h", "--help"): usage()
        elif o in ("-s", "--start"): start_torghost()
        elif o in ("-x", "--stop"): stop_torghost()
        elif o in ("-r", "--switch"): switch_tor()
        elif o in ("-u", "--update"): check_update()

if __name__ == "__main__":
    main()
