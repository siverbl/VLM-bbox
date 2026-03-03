#!/usr/bin/env bash
set -euo pipefail

DEB_DIR="${1:-./debs}"
VENV_DIR="${2:-.venv}"

sudo dpkg -i "${DEB_DIR}/hailort-pcie-driver_5.2.0_all.deb" || true
sudo dpkg -i "${DEB_DIR}/hailort_5.2.0_arm64.deb" || true
sudo dpkg -i "${DEB_DIR}/hailo_gen_ai_model_zoo_5.2.0_arm64.deb" || true
sudo apt-get update
sudo apt-get -f install -y

python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

echo "Verify installed versions:"
dpkg -l | rg 'hailort|hailo-gen-ai-model-zoo' || true
hailortcli fw-control identify || true
