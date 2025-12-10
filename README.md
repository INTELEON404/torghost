# 👻 TORGHOST v3.2.0 - MOD BY INTELEON404

<p align="center">
  <img src="https://img.shields.io/badge/Language-Python3-blue?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/Platform-Linux-orange?style=for-the-badge&logo=linux">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge">
</p>

```text
  ████████╗ ██████╗ ██████╗  ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗
  ╚══██╔══╝██╔═══██╗██╔══██╗██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝
     ██║   ██║   ██║██████╔╝██║  ███╗███████║██║   ██║███████╗   ██║   
     ██║   ██║   ██║██╔══██╗██║   ██║██╔══██║██║   ██║╚════██║   ██║   
     ██║   ╚██████╔╝██║  ██║╚██████╔╝██║  ██║╚██████╔╝███████║   ██║   
     ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   
                 ANONYMITY TOOLKIT v3.2.0 - MOD BY INTELEON404
````

## 💀 ABOUT THE TOOL

**TorGhost** is a lightweight, efficient anonymity tool designed to route **all** your network traffic through the Tor network. Unlike a simple browser proxy, TorGhost uses IPTables to redirect all system traffic (TCP/UDP), ensuring total system-wide anonymity.

This version (v3.2.0) has been **MODDED & OPTIMIZED** by **INTELEON404** for:

  * 🚀 **Super Fast Performance:** Optimized start/stop logic (connects in seconds).
  * 💎 **Professional UI:** Clean, uppercase, and perfectly aligned terminal output.
  * 🛡️ **Stability:** Fixed dependency issues on Kali Linux 2023+ & Debian 12.

## ⚡ FEATURES

  * **System-Wide Routing:** Redirects all internet traffic through Tor.
  * **DNS Leak Protection:** Prevents your real DNS from leaking.
  * **Identity Switching:** Request a new Tor Exit Node (New IP) instantly.
  * **Kill Switch:** Blocks all traffic if Tor fails (via IPTables rules).
  * **Auto-Update:** Built-in updater to fetch the latest version.

-----

## 📥 INSTALLATION

### Prerequisites

  * Linux System (Kali Linux, Parrot OS, Ubuntu, Debian, etc.)
  * Root Privileges (`sudo`)

### Step-by-Step Guide

1.  **Clone the Repository:**

    ```bash
    git clone [https://github.com/INTELEON404/torghost.git](https://github.com/INTELEON404/torghost.git)
    cd torghost
    ```

2.  **Give Permission & Install:**

    ```bash
    chmod +x install.sh
    sudo ./install.sh
    ```

    *(The installer will automatically fetch dependencies and compile the binary.)*

-----

## ℹ️ HELP MENU

You can view the help menu by running `torghost -h`.

```text
    COMMANDS:
    -s --start      START TORGHOST (ROUTE ALL TRAFFIC)
    -r --switch     REQUEST NEW TOR EXIT NODE (NEW IP)
    -x --stop       STOP TORGHOST (RESTORE DEFAULT)
    -h --help       SHOW THIS HELP MENU
    -u --update     CHECK FOR UPDATES
```

-----

## 🎮 USAGE EXAMPLES

### 🟢 Start Anonymity

Routes all traffic through Tor.

```bash
sudo torghost -s
```

### 🔄 Switch Identity

Changes your Tor Exit Node to get a fresh IP address.

```bash
sudo torghost -r
```

### 🔴 Stop Anonymity

Flushes IPTables and restores your original internet connection.

```bash
sudo torghost -x
```

-----

## ⚠️ DISCLAIMER

This tool is for **EDUCATIONAL PURPOSES ONLY**. The developer (INTELEON404) is not responsible for any misuse or illegal activities performed using this tool. Use it responsibly to protect your privacy.

-----

## 👨‍💻 CREDITS

  * **Original Author:** [SusmithKrishnan](https://github.com/SusmithKrishnan/)
  * **Modded & Optimized By:** [INTELEON404](https://www.google.com/search?q=https://github.com/INTELEON404)
