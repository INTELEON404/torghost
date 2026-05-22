![TorGhost Banner](https://github.com/INTELEON404/Template/blob/main/torghost.png)

<p align="center">
  <img src="https://img.shields.io/badge/Language-Python3-blue?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/Platform-Linux-orange?style=for-the-badge&logo=linux">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge">
  <img src="https://img.shields.io/badge/Version-3.2.1-red?style=for-the-badge">
</p>

---

## ABOUT THE TOOL

**TorGhost** is a lightweight, efficient anonymity tool designed to route **all** your network traffic through the Tor network. Unlike a simple browser proxy, TorGhost uses IPTables to redirect all system traffic (TCP/UDP), ensuring total system-wide anonymity.

This version (v3.3.0) has been **MODDED & OPTIMIZED** by **INTELEON404** for:

- **Super Fast Performance:** Optimized start/stop logic (connects in seconds).
- **Clean Terminal Output:** No emojis, no box-drawing characters. Plain, readable ASCII output with aligned status blocks.
- **Stability:** Fixed dependency issues on Kali Linux 2023+ and Debian 12.
- **Cross-Distro Support:** Auto-detects the Tor user across Debian, Arch, Fedora, and more.
- **Kill Switch:** Blocks all traffic if Tor fails, preventing accidental exposure.

---

## FEATURES

- **System-Wide Routing:** Redirects all internet traffic through Tor via IPTables.
- **DNS Leak Protection:** Prevents your real DNS from leaking outside the tunnel.
- **Identity Switching:** Request a new Tor Exit Node (new IP) instantly via Tor's control port.
- **Kill Switch:** Rejects all non-Tor traffic if the daemon fails.
- **Auto-Update Check:** Built-in checker to compare against the latest GitHub release.
- **Atomic File Writes:** DNS and torrc changes use safe atomic writes with automatic backup and restore.
- **Graceful Interrupt Handling:** SIGINT/SIGTERM trigger automatic cleanup of iptables and DNS.

---

## INSTALLATION

### Prerequisites

- Linux system (Kali Linux, Parrot OS, Ubuntu, Debian, Arch, Fedora, etc.)
- Root privileges (`sudo`)
- Python 3.6+

### Step-by-Step Guide

**1. Clone the repository:**

```bash
git clone https://github.com/INTELEON404/torghost.git
cd torghost
```

**2. Install system dependencies:**

```bash
# Debian / Ubuntu / Kali
sudo apt install tor iptables

# Arch Linux
sudo pacman -S tor iptables

# Fedora / RHEL
sudo dnf install tor iptables
```

**3. Install Python dependencies:**

```bash
pip3 install requests stem packaging
```

**4. Make executable:**

```bash
chmod +x torghost.py
```

---

## HELP MENU

```
USAGE:
    sudo python3 torghost.py [OPTION]

OPTIONS:
    -s, --start     START TORGHOST     Route all traffic through Tor
    -r, --switch    SWITCH IDENTITY    Request new Tor exit node
    -x, --stop      STOP TORGHOST      Restore original connection
    -u, --update    CHECK UPDATE       Check for new version
    -i, --ip        SHOW IP            Display current IP address
    -h, --help      HELP MENU          Show this help message
```

---

## USAGE EXAMPLES

### Start Anonymity

Routes all traffic through Tor and displays a status report:

```bash
sudo python3 torghost.py -s
```

**Example output:**

```
============================================================
  [ STATUS REPORT ]  [ TORGHOST ACTIVE - YOU ARE ANONYMOUS ]
============================================================
  > YOUR IP       : 192.42.116.101
  > TOR STATUS    : VERIFIED
  > TRAFFIC       : All traffic routed through Tor

  Use 'sudo python3 torghost.py -r' to switch identity
  Use 'sudo python3 torghost.py -x' to stop TorGhost
============================================================
```

### Switch Identity

Changes your Tor Exit Node to get a fresh IP address:

```bash
sudo python3 torghost.py -r
```

### Stop Anonymity

Flushes IPTables rules and restores your original connection:

```bash
sudo python3 torghost.py -x
```

### Show Current IP

Displays your current IP and whether Tor is active:

```bash
sudo python3 torghost.py -i
```

### Check for Updates

Compares your local version against the latest GitHub release:

```bash
sudo python3 torghost.py -u
```

---

## HOW IT WORKS

1. Writes a custom `torrc` to `/etc/tor/torghostrc` with `TransPort`, `DNSPort`, and `ControlPort` configured.
2. Backs up `/etc/resolv.conf` and points DNS to `127.0.0.1` to prevent DNS leaks.
3. Starts the Tor daemon under the system Tor user (`debian-tor`, `tor`, etc.).
4. Applies IPTables rules to:
   - Allow Tor user traffic to bypass the redirect.
   - Redirect all DNS (UDP 53) through Tor's DNS port.
   - Redirect all TCP traffic through Tor's transparent proxy port.
   - Reject everything else (kill switch).
5. Verifies the connection via `check.torproject.org`.

On stop, all rules are flushed, DNS is restored from backup, and Tor is shut down.

---

## SECURITY NOTES

- Always verify your IP after starting with `-i`.
- Use HTTPS websites for maximum security.
- Some services may block known Tor exit nodes.
- DNS leaks are prevented automatically via IPTables and DNS redirect.
- The kill switch (`iptables -A OUTPUT -j REJECT`) is active on failures.
- If interrupted (Ctrl+C), cleanup is performed automatically.

---

> [!Caution]
This tool is for **EDUCATIONAL PURPOSES ONLY**. The developer (INTELEON404) is not responsible for any misuse or illegal activities performed using this tool. Use it responsibly and legally to protect your privacy.

> [!WARNING]
> TorGhost modifies IPTables and DNS settings system-wide. Use carefully and always verify your connection after enabling Tor routing.
---

## CREDITS

- **Original Author:** [SusmithKrishnan](https://github.com/SusmithKrishnan/)
- **Modded & Optimized By:** [INTELEON404](https://github.com/INTELEON404)
