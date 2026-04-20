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

TOOLS_DIR := $(CURDIR)/tools_rendering

.PHONY: all setup node-tools system-deps imagemagick-policy rendering-tools \
        abcm2ps oss-cad ditaa asymptote kicad r2dt varna plantuml openbabel d2lang \
        bpmn-python python-package clean

all: setup

setup: system-deps node-tools imagemagick-policy rendering-tools abcm2ps \
       oss-cad ditaa asymptote kicad r2dt varna plantuml openbabel d2lang \
       python-package bpmn-python
	@echo "✅ All done! Restart your terminal or run 'source ~/.bashrc'"

node-tools:
	@echo "🔧 Installing Node.js CLI tools"
	npm install -g netlistsvg@1.0.2 state-machine-cat@12.0.22 \
		@mermaid-js/mermaid-cli markmap-cli@0.18.11 \
		@softwaretechnik/dbml-renderer@1.0.30 @dbml/cli@3.13.0-alpha.1 \
		prisma@6.6.0 prisma-dbml-generator@0.12.0
	npm install prisma@6.6.0 -D
	npm install @prisma/client@6.6.0
	cd $(TOOLS_DIR) && git clone https://github.com/nturley/netlistsvg.git

system-deps:
	@echo "🔧 Installing system dependencies via apt"
	@echo 'export TOOL_PATH=$(TOOLS_DIR)' >> ~/.bashrc
	mkdir -p $(TOOLS_DIR)
	sudo apt update
	sudo apt install -y software-properties-common
	sudo add-apt-repository -y ppa:mscore-ubuntu/mscore-stable
	sudo apt update
	sudo apt install -y texlive-latex-base latexmk ghostscript texlive-latex-extra cm-super \
		texlive-extra-utils pdf2svg default-jre imagemagick graphviz musescore3 xvfb \
		build-essential cmake git libcairo2-dev libeigen3-dev libffi-dev \
		libfreetype6-dev libpng-dev libpython3-dev libxml2-dev zlib1g-dev unzip inkscape
	@echo 'export PATH=/usr/local/texlive/2024/bin/x86_64-linux:$$PATH' >> ~/.bashrc
	@echo 'export QT_QPA_PLATFORM=offscreen' >> ~/.bashrc

imagemagick-policy:
	@echo "🔧 Modifying ImageMagick policy.xml"
	sudo sed -i '/<\/policymap>/i \
	<policy domain="coder" rights="read|write" pattern="PDF" />\
	<policy domain="coder" rights="read|write" pattern="PS" />\
	<policy domain="coder" rights="read|write" pattern="EPS" />' /etc/ImageMagick-6/policy.xml

rendering-tools:
	@echo "🔧 Installing LilyPond"
	cd $(TOOLS_DIR) && wget -q https://gitlab.com/lilypond/lilypond/-/releases/v2.24.4/downloads/lilypond-2.24.4-linux-x86_64.tar.gz && \
		tar -xvzf lilypond-2.24.4-linux-x86_64.tar.gz
	@echo 'export PATH=$(TOOLS_DIR)/lilypond-2.24.4/bin:$$PATH' >> ~/.bashrc

abcm2ps:
	@echo "🔧 Installing abcm2ps"
	cd $(TOOLS_DIR) && git clone https://github.com/lewdlime/abcm2ps.git && \
	cd abcm2ps && ./configure && make

oss-cad:
	@echo "🔧 Installing OSS CAD Suite"
	cd $(TOOLS_DIR) && \
	wget -q https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2024-12-02/oss-cad-suite-linux-x64-20241202.tgz && \
	tar -xvzf oss-cad-suite-linux-x64-20241202.tgz
	@echo 'export PATH=$(TOOLS_DIR)/oss-cad-suite/bin:$$PATH' >> ~/.bashrc

ditaa:
	@echo "🔧 Downloading Ditaa"
	mkdir -p $(TOOLS_DIR)/ditaa
	cd $(TOOLS_DIR)/ditaa && wget -q https://sourceforge.net/projects/ditaa/files/ditaa/0.9/ditaa0_9.zip
	unzip ditaa0_9.zip

asymptote:
	@echo "🔧 Downloading Asymptote"
	mkdir -p $(TOOLS_DIR)/asymptote
	cd $(TOOLS_DIR)/asymptote && wget -q https://sourceforge.net/projects/asymptote/files/3.01/asymptote-3.01.x86_64.tgz
	sudo tar -C / -zxf asymptote-3.01.x86_64.tgz 

kicad:
	@echo "🔧 Downloading KiCad symbols"
	cd $(TOOLS_DIR) && \
	wget -q https://gitlab.com/kicad/libraries/kicad-symbols/-/archive/5.1.12/kicad-symbols-5.1.12.tar.gz && \
	tar -xvzf kicad-symbols-5.1.12.tar.gz
	@echo 'export KICAD_SYMBOL_DIR=$(TOOLS_DIR)/kicad-symbols-5.1.12' >> ~/.bashrc

r2dt:
	@echo "🔧 Installing R2DT"
	mkdir -p $(TOOLS_DIR)/r2dt_temp
	sudo docker pull rnacentral/r2dt
	cd $(TOOLS_DIR) && curl -LO https://github.com/r2dt-bio/R2DT/releases/download/v2.0/cms.tar.gz && tar -xzf cms.tar.gz
	@echo 'export R2DT_LIBRARY=$(TOOLS_DIR)/2.0' >> ~/.bashrc

varna:
	@echo "🔧 Downloading VARNA"
	cd $(TOOLS_DIR) && wget -q https://varna.lisn.upsaclay.fr/bin/VARNAv3-93.jar

plantuml:
	@echo "🔧 Downloading PlantUML"
	cd $(TOOLS_DIR) && wget -q https://github.com/plantuml/plantuml/releases/download/v1.2025.2/plantuml-mit-1.2025.2.jar

openbabel:
	@echo "🔧 Installing OpenBabel into its local directory"
	cd $(TOOLS_DIR) && \
	wget -q https://sourceforge.net/projects/openbabel/files/openbabel/2.4.0/openbabel-openbabel-2-4-0.tar.gz && \
	tar -zxvf openbabel-openbabel-2-4-0.tar.gz && \
	cd openbabel-openbabel-2-4-0 && mkdir -p build && cd build && \
	cmake .. -DCMAKE_INSTALL_PREFIX=$(TOOLS_DIR)/openbabel-openbabel-2-4-0/local && \
	make && make install
	@echo 'export PATH=$(TOOLS_DIR)/openbabel-openbabel-2-4-0/local/bin:$$PATH' >> ~/.bashrc
	@echo 'export BABEL_LIBDIR=$(TOOLS_DIR)/openbabel-openbabel-2-4-0/local/lib/openbabel/2.4.0' >> ~/.bashrc

d2lang:
	@echo "🔧 Installing D2 language"
	curl -fsSL https://d2lang.com/install.sh | sh -s --

python-package:
	@echo "🔧 Installing local Python package via uv"
	uv venv --python 3.11
	uv pip install --python .venv/bin/python --upgrade pip
	uv pip install --python .venv/bin/python -e ".[all]"
	plotly_get_chrome
	playwright install	

clean:
	rm -rf $(TOOLS_DIR)
