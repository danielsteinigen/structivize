#!/bin/bash
# ==========================================================
# ℹ️  Note: Please review this script before running
# ==========================================================
#
# This script will install system packages, configure tools,
# and modify your environment (e.g. ~/.bashrc).
#
# It's recommended to examine setup scripts before executing them,
# particularly when working in sensitive or production setups.
#
# Use responsibly and adjust commands as needed for your system.
#
# ==========================================================
set -e

LOG() {
  echo ""
  echo "🔧 $1"
  echo ""
}

read -p "ℹ️  This script modifies your environment. Continue? [y/N]: " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 1
fi

# === Check for sudo ===
if ! command -v sudo &> /dev/null; then
  echo "❌ This script requires sudo access. Please install sudo or run as root."
  exit 1
fi

# === Check and install make if not present ===
if ! command -v make &> /dev/null; then
  LOG "'make' is not installed. Installing it..."
  sudo apt-get update
  sudo apt-get install -y make
else
  LOG "'make' is already installed."
fi

# === Check if uv is installed globally ===
if ! command -v uv &> /dev/null; then
  LOG "'uv' is not installed. Installing it (user local)..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  source "$HOME/.local/bin/env"
else
  LOG "'uv' is already installed."
fi

# === Check for Python 3.11 installed by uv ===
if uv python list | grep -q '3\.11'; then
  echo "✅ Python 3.11 is already installed by uv:"
  uv python list | grep '3\.11'
else
  echo "🔧 Installing Python 3.11 via uv..."
  uv python install 3.11
fi


# === Check if nvm is installed ===
if [ ! -d "$HOME/.nvm" ]; then
  LOG "Installing Node Version Manager (nvm)..."
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash
  export NVM_DIR="$HOME/.nvm"
  source "$NVM_DIR/nvm.sh"
  echo 'export NVM_DIR="$HOME/.nvm"' >> "$HOME/.bashrc"
  echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> "$HOME/.bashrc"
else
  LOG "nvm already installed."
  export NVM_DIR="$HOME/.nvm"
  source "$NVM_DIR/nvm.sh"
fi

# === Install Node 22 ===
if nvm ls | grep -q 'v22\.'; then
  echo "✅ A Node.js 22.x version is already installed:"
  nvm ls | grep 'v22\.'
else
  echo "🔧 Installing latest Node.js 22"
  nvm install 22
fi
nvm use 22
nvm alias default 22


# === Check if Docker is installed ===
if ! command -v docker &> /dev/null; then
  echo "🔧 Docker is not installed. Installing it..."

  # Update package index and install prerequisites
  sudo apt-get update
  sudo apt-get install -y ca-certificates curl

  # Add Docker’s official GPG key
  sudo install -m 0755 -d /etc/apt/keyrings
  sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  sudo chmod a+r /etc/apt/keyrings/docker.asc

  # Set up the Docker repository
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
    https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

  # Install Docker Engine
  sudo apt-get update
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  sudo usermod -aG docker $USER

  echo "✅ Docker installed successfully."

else
  echo "✅ Docker is already installed: $(docker --version)"
fi


# === Run Makefile setup ===
LOG "Running 'make setup'"
make setup

LOG "✅ Setup complete! Restart your shell or run 'source ~/.bashrc'"
