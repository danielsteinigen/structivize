# Structivize

A modular Python rendering toolkit for generating structured visualizations from code in specific formal representation languages (FRL), comprising several tools in multiple domains.

# Installation

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

### Install NVM and Node.js (v22.14.0)
```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash
export NVM_DIR="$HOME/.nvm"
source "$NVM_DIR/nvm.sh"
nvm install 22
```

### Run make script
ℹ️ **Note: Please review the Makefile before running** 

This script will install system packages, configure tools, and modify your environment. It's recommended to examine setup scripts before executing them, particularly when working in sensitive or production setups. Use responsibly and adjust commands as needed for your system.

```bash
make setup
```

## Install structivize package only (not recommended)

This will install the package with all additional Python libraries. Please note that many renderers require additional JavaScript or CLI-Tools, that are only installed when executing the Makefile (see above).

```bash
uv pip install structivize[all]
```

Install from local repo:
```bash
uv pip install -r requirements.txt
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

# Usage

## CLI
Render a single file with a specific renderer:
```bash
structivize --renderer bio_fasta --code examples/biology/bio_fasta/sample_bio_fasta.txt
```

Choose output settings:
```bash
structivize --renderer bio_fasta --code examples/biology/bio_fasta/sample_bio_fasta.txt --format png --output output/plc_example
```

Choose a specific tool (for renderers that offer multiple tools):
```bash
structivize --renderer bio_fasta --code examples/biology/bio_fasta/sample_bio_fasta.txt --tool logomaker
```

Override tool settings (JSON values supported):
```bash
structivize --renderer bio_fasta --code examples/biology/bio_fasta/sample_bio_fasta.txt \
  --tool logomaker \
  --tool-config logomaker.color_scheme="classic" \
  --tool-config logomaker.show_spines=true
```

## Python API
Import a renderer directly:
```python
from structivize.renderers.biology.renderer_bio_fasta import RendererBioFasta

renderer = RendererBioFasta(code_path="examples/biology/bio_fasta/sample_bio_fasta.txt")
result = renderer.render(tool="logomaker")
print(result.success, result.path_image)
```

Use the registry:
```python
from structivize.renderer import Renderer

renderer = Renderer.from_dict(
    renderer="bio_fasta",
    code_path="examples/biology/bio_fasta/sample_bio_fasta.txt",
    output_base_path="output/bio_fasta_example",
    output_format="png",
    tool_configs={"logomaker": {"color_scheme": "classic", "show_spines": True}},
)
result = renderer.render(tool="logomaker")
print(result.success, result.path_image)
```


# Licensing and Third-Party Tools

This repository and toolkit are licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

**External Tools and Libraries**

This toolkit integrates and relies on several external tools and libraries. Please note:

  * These external tools and libraries (dependencies) are **used as-is** and are **not modified** by this toolkit.
  * Users must download and install these dependencies themselves.
  * **Each dependency has its own license** that applies independently.
  * **No warranty** is provided for the use of these external tools or libraries.

For a complete list of external tools and libraries, along with their licenses and links, see [Tools & Libraries License Information](tools_licenses.md).
