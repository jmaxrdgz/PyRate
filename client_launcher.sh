#!/usr/bin/env bash
# client_launcher.sh

# 1. Open video stream in browser (Linux/macOS)
open "http://127.0.0.1:8000/video/stream"

# 2. Activate env if needed for agent
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate pyrate

# 3. Launch dummy agent
python tests/dummy_agent.py

chmod +x client_launcher.sh
