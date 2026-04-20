FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /workspace

# Install base system dependencies
RUN apt-get update && apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:mscore-ubuntu/mscore-stable && \
    apt-get update && apt-get install -y \
    ca-certificates curl wget git build-essential cmake unzip \
    texlive-latex-base latexmk ghostscript texlive-latex-extra cm-super \
    texlive-extra-utils pdf2svg default-jre imagemagick graphviz musescore3 xvfb \
    libcairo2-dev libeigen3-dev libffi-dev libfreetype6-dev \
    libpng-dev libpython3-dev libxml2-dev zlib1g-dev inkscape

# Modify ImageMagick policy
RUN sed -i '/<\/policymap>/i \
<policy domain="coder" rights="read|write" pattern="PDF" />\
<policy domain="coder" rights="read|write" pattern="PS" />\
<policy domain="coder" rights="read|write" pattern="EPS" />' /etc/ImageMagick-6/policy.xml

# Install uv (fast Python installer)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Install Python 3.11 using uv
RUN uv python install 3.11
ENV PATH="/root/.local/share/uv/python/3.11.*/bin:$PATH"

# Install nvm and Node.js 22.14
ENV NVM_DIR=/root/.nvm
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash \
    && . "$NVM_DIR/nvm.sh" && nvm install 22 && nvm use 22 && nvm alias default 22 \
    && ln -s "$NVM_DIR/versions/node/$(. "$NVM_DIR/nvm.sh" && nvm version 22)/bin/node" /usr/local/bin/node \
    && ln -s "$NVM_DIR/versions/node/$(. "$NVM_DIR/nvm.sh" && nvm version 22)/bin/npm" /usr/local/bin/npm \
    && ln -s "$NVM_DIR/versions/node/$(. "$NVM_DIR/nvm.sh" && nvm version 22)/bin/npx" /usr/local/bin/npx

# Install node-based tools
RUN npm install -g netlistsvg@1.0.2 state-machine-cat@12.0.22 @mermaid-js/mermaid-cli markmap-cli@0.18.11 @softwaretechnik/dbml-renderer@1.0.30 @dbml/cli@3.13.0-alpha.1 \
    prisma@6.6.0 prisma-dbml-generator@0.12.0

RUN npm install prisma@6.6.0 -D && npm install @prisma/client@6.6.0

WORKDIR /tools_rendering

# Netlistsvg
RUN git clone https://github.com/nturley/netlistsvg.git

# LilyPond
RUN wget -q https://gitlab.com/lilypond/lilypond/-/releases/v2.24.4/downloads/lilypond-2.24.4-linux-x86_64.tar.gz && \
    tar -xzf lilypond-2.24.4-linux-x86_64.tar.gz

# abcm2ps
RUN git clone https://github.com/lewdlime/abcm2ps.git && \
    cd abcm2ps && ./configure && make

# OSS CAD Suite
RUN wget -q https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2024-12-02/oss-cad-suite-linux-x64-20241202.tgz && \
    tar -xzf oss-cad-suite-linux-x64-20241202.tgz

# Ditaa, KiCad, R2DT
RUN wget -q https://sourceforge.net/projects/ditaa/files/ditaa/0.9/ditaa0_9.zip && \
    wget -q https://gitlab.com/kicad/libraries/kicad-symbols/-/archive/5.1.12/kicad-symbols-5.1.12.tar.gz && \
    tar -xzf kicad-symbols-5.1.12.tar.gz && unzip ditaa0_9.zip && \
    curl -LO https://github.com/r2dt-bio/R2DT/releases/download/v2.0/cms.tar.gz && \
    tar -xzf cms.tar.gz

# Asymptote
RUN wget -q https://sourceforge.net/projects/asymptote/files/3.01/asymptote-3.01.x86_64.tgz && \
    tar -C / -zxf asymptote-3.01.x86_64.tgz

# VARNA & PlantUML
RUN wget -q https://varna.lisn.upsaclay.fr/bin/VARNAv3-93.jar && \
    wget -q https://github.com/plantuml/plantuml/releases/download/v1.2025.2/plantuml-mit-1.2025.2.jar

# OpenBabel (local prefix)
RUN wget -q https://sourceforge.net/projects/openbabel/files/openbabel/2.4.0/openbabel-openbabel-2-4-0.tar.gz && \
    tar -xzf openbabel-openbabel-2-4-0.tar.gz && \
    cd openbabel-openbabel-2-4-0 && mkdir build && cd build && \
    cmake .. -DCMAKE_INSTALL_PREFIX=/tools_rendering/openbabel-openbabel-2-4-0/local && \
    make && make install

# D2 Language
RUN curl -fsSL https://d2lang.com/install.sh | sh -s --

ENV TOOL_PATH=/tools_rendering
ENV KICAD_SYMBOL_DIR=/tools_rendering/kicad-symbols-5.1.12
ENV BABEL_LIBDIR=/tools_rendering/openbabel-openbabel-2-4-0/local/lib/openbabel/2.4.0
ENV R2DT_LIBRARY=/tools_rendering/2.0
ENV QT_QPA_PLATFORM=offscreen

# === Install repo and Python package ===
WORKDIR /workspace
COPY . /workspace
RUN uv venv --python 3.11
RUN uv pip install --python /workspace/.venv/bin/python --upgrade pip
RUN uv pip install --python /workspace/.venv/bin/python -e ".[all]"
RUN /workspace/.venv/bin/plotly_get_chrome

ENV PATH=/workspace/.venv/bin:/tools_rendering/lilypond-2.24.4/bin:/tools_rendering/oss-cad-suite/bin:/tools_rendering/openbabel-openbabel-2-4-0/local/bin:/usr/local/texlive/2024/bin/x86_64-linux:$PATH

WORKDIR /workspace

CMD ["bash"]
