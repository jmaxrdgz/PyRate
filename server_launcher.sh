#!/usr/bin/env bash
# server_launcher.sh

# 1. Activate your conda env
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate pyrate

# 2. (Optional) Export SDL dummy driver for headless
export SDL_VIDEODRIVER=dummy

# 3. Start the API (game engine runs inside)
uvicorn pyrate.api:app --host 0.0.0.0 --port 8000 --reload

chmod +x server_launcher.sh
