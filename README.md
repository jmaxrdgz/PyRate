# PyRate
PyRate is a top-down 2D naval battle game where you command pirate ships in tactical sea skirmishes, built with Python.  
You are victorious if all enemy ships get destroyed, if the player gets destroyed it's game over.
  
### Player
Spawns in the middle of the map. Can sail forward, turn both direction and slow down but it can't sail backwards. It can shoot it's cannons on both sides, cannons have a 4s cooldown and a maximum range.

### Enemies
Enemy ships have a patrol zone where they randomly move. If the player enters their aggression zone, they start following it with a parallel trajectory to engage the fight. All ships have collision enabled, collision between the player and an enemy ship result in damage to both ships.  


# ⚙️ Installation & Launch
  
### Clone the repo  
```
git clone https://github.com/jmaxrdgz/PyRate.git
cd pyrate
``` 

### Create virtual environment  
Using conda  
```
conda env create -f environment.yml   
conda activate pyrate
```  
You can also use pip in an existing environment  
```pip install -r requirements.txt``` 
  
### Launch the game  
You can test the game with the keyboard using the following constant in ```settings.py```:  
```INPUT_MODE = "keyboard"```  
Then launch the game  
```python -m pyrate.main```  
 
  
# 🔌 API Usage
PyRate includes an HTTP API for controlling the player ship programmatically.  
  
### Start the API server
Make sure that the API control option is set in the ```pyrate/settings.py```file as such :  
```INPUT_MODE = "api"```  
Run the launcher script :  
```sh server_lancher.sh```  
This script launches the FastAPI server (uvicorn) on port 8000.
  
### Endpoints overview
Endpoint | Method | Description
|---------|--------|------------|
|/ | GET | Welcome message|
|/game/status | GET | Get global game state|
|/player/status | GET | Get player ship status|
|/player/command | POST | Send control command to the player|
|/enemies/status | GET | Get status of all enemies|
|/projectiles/status | GET | Get status of all projectiles|
|/game/update | POST | Force a game state update (1 frame step)|
|/video/stream | GET | Live MJPEG video stream|
  
### Command Format
```
{
  "action": "accelerate" | "decelerate" | "turn_left" | "turn_right" | "fire",
  "side": "left" | "right" // only used when action is "fire"
}
```

# 🤖 Dummy Agent
A simple agent script is included for testing or as a base to create your own.

### 📍 Location
```
tests/dummy_agent.py
```
  
### ▶️ Launch the Dummy Agent
On the client machine (where you want to control and view the game):
```
sh client_launcher.sh
```
This script will:
- Open the game stream in your browser
- Launch dummy_agent.py which sends commands to the player

### Agent Logic
- Randomly chooses one of: accelerate, decelerate, turn_left, turn_right  
- If an enemy is within 200 units, it prioritizes firing  
  
# ✏️ Create Your Own Agent
To write a custom agent:

1. Copy dummy_agent.py and rename it:
```
cp tests/dummy_agent.py tests/my_agent.py
```
2. Modify the logic inside run_agent():
```
def run_agent():
    while True:
        status = requests.get(f"{SERVER_URL}/player/status").json()
        # Insert your logic here...
        action = {"action": "turn_right"}
        requests.post(f"{SERVER_URL}/player/command", json=action)
        time.sleep(0.2)
```
3. Update client_launcher.sh to call your custom script:
```
python tests/my_agent.py &
```
  
# 🛑 Stop the Server and Client
To stop everything:

### Server (on server machine)
- Press Ctrl+C in the terminal running the server
- Or use:
```
pkill -f "uvicorn pyrate.api:app"
```
### Client (on client machine)
- Close the browser tab
- Press Ctrl+C to stop the agent, or:
```
pkill -f dummy_agent.py
```

# To-Do
### Map
- Add borders
- Add camera displacement 
- Add island and forts generation *
### Gameplay
- Add UI
- Add scores & objectives
- Add bonus drops & ship upgrades 
- Add multiplayer (Team vs team)
### API
- Add sensors (robotic-like : noise, noisy data...) *  
- Enrich API functionalities
