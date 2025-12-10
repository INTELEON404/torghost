#!/bin/bash
# TORGHOST INSTALLER
# Run: sudo ./install.sh

# COLORS
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;96m'
YELLOW='\033[1;33m'
GREY='\033[0;90m'
NC='\033[0m' # No Color

# ALIGNMENT WIDTH
WIDTH=50

# FUNCTION TO PRINT STATUS (Upper Case & Aligned)
print_status() {
    # Get current time
    TIME=$(date +%T)
    # Convert message to uppercase
    MSG=$(echo "$1" | tr '[:lower:]' '[:upper:]')
    # Print formatted string: [TIME] ➜ MESSAGE...     
    printf "${GREY}[$TIME]${NC} ${CYAN}➜${NC} %-${WIDTH}s" "$MSG"
}

print_success() {
    printf " ${GREEN}[DONE]${NC}\n"
}

print_fail() {
    printf " ${RED}[FAILED]${NC}\n"
    exit 1
}

# ROOT CHECK
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}PLEASE RUN AS ROOT (sudo ./install.sh)${NC}"
    exit 1
fi

clear
echo -e "${RED}========================================${NC}"
echo -e "      ${YELLOW}TORGHOST - INSTALLER${NC}      "
echo -e "${RED}========================================${NC}"
echo

# 1. UPDATE PACKAGE LIST
print_status "Updating package list"
sudo apt update -qq >/dev/null 2>&1 && print_success || print_fail

# 2. INSTALL SYSTEM DEPENDENCIES
print_status "Installing tor, python3, build-essential"
sudo apt install -y tor python3-pip cython3 build-essential python3-dev >/dev/null 2>&1 && print_success || print_fail

# 3. INSTALL PYTHON DEPENDENCIES
print_status "Installing Python libraries"
# Added --break-system-packages to fix PEP 668 error on Kali/Debian 12+
pip3 install --break-system-packages --quiet stem requests packaging >/dev/null 2>&1 && print_success || print_fail

# 4. PREPARE BUILD DIRECTORY
print_status "Preparing build environment"
rm -rf build
mkdir -p build
if [ -f "torghost.py" ]; then
    print_success
else
    printf " ${RED}[MISSING torghost.py]${NC}\n"
    exit 1
fi

# 5. COMPILING
print_status "Compiling torghost binary"
cd build
cython3 --embed ../torghost.py -o torghost.c >/dev/null 2>&1
gcc -Os $(python3-config --includes) torghost.c -o torghost $(python3-config --libs) -lutil >/dev/null 2>&1
if [ -f "torghost" ]; then
    print_success
else
    print_fail
fi

# 6. INSTALLING BINARY
print_status "Installing to /usr/local/bin"
sudo install -m 755 torghost /usr/local/bin/torghost && print_success || print_fail

# 7. CLEANUP
print_status "Cleaning up temporary files"
cd ..
rm -rf build torghost.c
print_success

echo
if command -v torghost >/dev/null; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}       INSTALLATION SUCCESSFUL          ${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo
    echo -e "COMMANDS (USE WITH SUDO):"
    echo -e "  torghost -s    ${YELLOW}START TOR ROUTING${NC}"
    echo -e "  torghost -r    ${YELLOW}SWITCH IDENTITY${NC}"
    echo -e "  torghost -x    ${YELLOW}STOP TOR ROUTING${NC}"
    echo -e "  torghost -u    ${YELLOW}CHECK FOR UPDATES${NC}"
    echo
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}          INSTALLATION FAILED           ${NC}"
    echo -e "${RED}========================================${NC}"
fi
