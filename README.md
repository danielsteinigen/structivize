# Structivize

A modular Python rendering toolkit for generating structured visualizations from code in specific formal representation languages (FRL), comprising several tools in multiple domains.

# Usage

## Installation with Setup Script
ℹ️ **Note: Please review the setup script before running** 

This script will install system packages, configure tools, and modify your environment. It's recommended to examine setup scripts before executing them, particularly when working in sensitive or production setups. Use responsibly and adjust commands as needed for your system.

```bash
chmod +x setup.sh && ./setup.sh
```

## Manual installation
### Create virtual Python environment e.g. using uv
```
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.11
source .venv/bin/activate
```
### Install structvize package
```bash
uv pip install structivize
```

### Install NVM and Node.js (v22.14.0)
```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash
export NVM_DIR="$HOME/.nvm"
source "$NVM_DIR/nvm.sh"
nvm install 22
```

### Run make script
```bash
make setup
```

## using docker
### install docker
```
sudo apt-get install docker.io
sudo usermod -aG docker ${USER}
```
### build docker image
```bash
docker build -t myproject:latest .
docker run -it --rm -v $(pwd):/workspace myproject:latest
```
