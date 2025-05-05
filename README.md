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
```python -m pyrate.main```  
 
  
# 🔌 API Usage
PyRate includes an HTTP API for controlling the player ship programmatically.  
  
### Start the API server
```uvicorn pyrate.api:app --reload```  
  
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
  
### Command Format
```
{
  "action": "accelerate" | "decelerate" | "turn_left" | "turn_right" | "fire",
  "side": "left" | "right" // only used when action is "fire"
}
```

# 🤖 Dummy Agent
A simple agent is available to control the player ship using the API. It sends random actions, and fires automatically when enemies are nearby.

### Location
See the script: ```tests/dummy_agent.py```

### Launch the Dummy Agent
Make sure the API server is running, then execute:

```
python dummy_agent.py
```

### Agent Logic
- Randomly chooses one of: accelerate, decelerate, turn_left, turn_right  
- If an enemy is within 200 units, it prioritizes firing  
  

# To-Do
### Map
- Add borders
- Add camera displacement 
- Add island and forts generation
### Gameplay
- Add UI
- Add scores & objectives
- Add bonus drops & ship upgrades
- Add colisions
