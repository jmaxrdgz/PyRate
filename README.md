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
 
  
Below is an updated **README.md** that reflects the current API endpoints, request/response schemas, and naming conventions from your latest `api.py` and `game.py`.

---

# 🔌 PyRate HTTP API Usage

PyRate provides an HTTP API for programmatic control of player ships, retrieving game‐state information, and streaming a live MJPEG video.

## Prerequisites

1. **Set input mode to API**
   In `pyrate/settings.py`, ensure:

   ```python
   INPUT_MODE = "api"
   ```
2. **Launch the server**
   From the project root, run:

   ```bash
   sh server_lancher.sh
   ```

   This script starts a Uvicorn/FastAPI server, listening on port **8000** by default.

---

## Endpoints Overview

| Endpoint                       | Method | Description                                                                                                |
| ------------------------------ | ------ | ---------------------------------------------------------------------------------------------------------- |
| `/`                            | GET    | Welcome message (basic health check).                                                                      |
| `/players/{player_id}/status`  | GET    | Retrieve a specific player ship’s status.                                                                  |
| `/players/{player_id}/sensor`  | GET    | Retrieve “nearby\_ships” sensor readings for a given player ship (includes friendlies/enemies with noise). |
| `/players/{player_id}/command` | POST   | Issue a control command (accelerate/decelerate/turn/fire) to a specific player ship.                       |
| `/video/stream`                | GET    | Live MJPEG video stream of the current game frame.                                                         |
| `/game/control`                | POST   | Switch the global control mode between `"keyboard"` and `"api"`.                                           |

---

## 1. Welcome (GET `/`)

```http
GET http://localhost:8000/
```

**Response:**

```json
{
  "message": "Welcome to the PyRate API!"
}
```

---

## 2. Get a Player’s Status (GET `/players/{player_id}/status`)

Retrieve angle, rotation velocity, speed, health, living status, and last‐fire timestamp for one player ship.

```http
GET http://localhost:8000/players/{player_id}/status
```

* **Path parameter**

  * `player_id` (integer): zero‐based index of the player ship (e.g. `0`, `1`, …).

* **Successful Response (200)**

  ```json
  {
    "angle": 45.0,
    "rotation_velocity": 2.5,
    "speed": 10.0,
    "health": 75.0,
    "is_living": true,
    "last_fire_time": {
      "seconds": 1624275600.0,
      "nanoseconds": 123000000
    }
  }
  ```

  * `angle`: Current orientation in degrees (0–360).
  * `rotation_velocity`: Angular speed (degrees per frame).
  * `speed`: Current forward speed.
  * `health`: Remaining health (0–100).
  * `is_living`: `true` if the ship is still alive; otherwise `false`.
  * `last_fire_time`: A timestamp object (seconds + nanoseconds) of when this ship last fired a cannon.

* **Error Responses**

  * `404 Not Found` if `player_id` is out of range.

---

## 3. Get Sensor Readings (GET `/players/{player_id}/sensor`)

Fetch a list of **“nearby\_ships”** that the specified player can sense, each with distance, (noisy) angle, living status, health category, and identity. Friendlies are labeled `"friendly"`, and distant unknown targets are `"Unknown"`.

```http
GET http://localhost:8000/players/{player_id}/sensor
```

* **Path parameter**

  * `player_id` (integer): index of the player ship making the sensor query.

* **Successful Response (200)**

  ```json
  {
    "nearby_ships": [
      {
        "entity": "friendly",
        "distance": 150.234,
        "angle": 30.12,
        "is_living": true,
        "health": "high"
      },
      {
        "entity": "EnemyShip42",
        "distance": 250.789,
        "angle": 120.45,
        "is_living": true,
        "health": "low"
      },
      {
        "entity": "Unknown",
        "distance": 380.532,
        "angle": 278.91,
        "is_living": true,
        "health": "high"
      }
      // … more entries for every other ship (players + enemies) except self
    ]
  }
  ```

  * Each object in `"nearby_ships"` contains:

    * `entity`:

      * `"friendly"` if the other ship is on the same team as the querying player.
      * Otherwise, the ship’s `name` (e.g. `"EnemyShip42"`), or `"Unknown"` if distance ≥ 400.
    * `distance`: Euclidean distance (with noise applied if < 400).
    * `angle`: Bearing in degrees **(noisy)** from the querying ship to that target.
    * `is_living`: `true`/`false` depending on if that ship is still alive.
    * `health`: `"low"` if health ≤ 40, else `"high"`.

* **Error Responses**

  * `404 Not Found` if `player_id` is invalid.

---

## 4. Send a Control Command (POST `/players/{player_id}/command`)

Issue one of: `"accelerate"`, `"decelerate"`, `"turn_left"`, `"turn_right"`, or `"fire"`. If firing, specify `"side"` as `"left"` or `"right"`.

```http
POST http://localhost:8000/players/{player_id}/command
Content-Type: application/json

{
  "action": "fire",
  "side": "left"
}
```

* **Path parameter**

  * `player_id` (integer): index of the player ship to control.

* **Request Body (JSON)**

  | Field    | Type                                                                            | Description                                           |
  | -------- | ------------------------------------------------------------------------------- | ----------------------------------------------------- |
  | `action` | `"accelerate"`<br>`"decelerate"`<br>`"turn_left"`<br>`"turn_right"`<br>`"fire"` | Which action to perform.                              |
  | `side`   | `"left"` or `"right"`                                                           | Only used if `action` is `"fire"`; ignored otherwise. |

* **Successful Response (200)**

  ```json
  {
    "status": "ok"
  }
  ```

* **Error Responses**

  * `400 Bad Request` if `action` is not recognized, or if `side` is missing/invalid when `action` is `"fire"`.
  * `404 Not Found` if `player_id` is invalid.

---

## 5. Live Video Stream (GET `/video/stream`)

Streams the current game display as an MJPEG over an HTTP multipart response. Connect your client (e.g., a browser or video‐viewing tool) to:

```http
GET http://localhost:8000/video/stream
```

You will receive a continuous stream of JPEG frames, boundary‐delimited by `--frame`.

> **Note:** The server caps updates at approximately **30 FPS** by default (`clock.tick(30)`).

---

## 6. Switch Control Mode (POST `/game/control`)

Toggle between keyboard input and API control for all player ships.

```http
POST http://localhost:8000/game/control
Content-Type: application/json

{
  "mode": "keyboard"
}
```

* **Request Body (JSON)**

  | Field  | Type                    | Description               |
  | ------ | ----------------------- | ------------------------- |
  | `mode` | `"keyboard"` or `"api"` | Sets `game.control_mode`. |

* **Successful Response (200)**
  ```json
  {
    "status": "ok",
    "mode": "keyboard"
  }
  ```

* **Error Responses**
  * `400 Bad Request` if `mode` is not `"keyboard"` or `"api"`.

---

## Example Workflow

1. **Start the server**
   ```bash
   sh server_lancher.sh
   ```

2. **Check that the server is running**
   ```bash
   curl http://localhost:8000/
   # → {"message":"Welcome to the PyRate API!"}
   ```

3. **Switch to API mode (optional, since default is “api”)**
   ```bash
   curl -X POST http://localhost:8000/game/control \
     -H "Content-Type: application/json" \
     -d '{"mode":"api"}'
   # → {"status":"ok","mode":"api"}
   ```

4. **Get the status of player 0**
   ```bash
   curl http://localhost:8000/players/0/status
   # → { "angle": 0.0, "rotation_velocity": 0.0, …, "last_fire_time": { "seconds": 0.0, "nanoseconds": 0 } }
   ```

5. **Issue an “accelerate” command to player 0**
   ```bash
   curl -X POST http://localhost:8000/players/0/command \
     -H "Content-Type: application/json" \
     -d '{"action": "accelerate"}'
   # → {"status":"ok"}
   ```

6. **Get sensor readings for player 0**
   ```bash
   curl http://localhost:8000/players/0/sensor
   # → { "nearby_ships": [ … ] }
   ```

7. **Open a browser (or MJPEG‐compatible client) to view live video**
   ```
   http://localhost:8000/video/stream
   ```  
   On MacOS, the video stream should open automaticaly.


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
- Add sensors (robotic-like : noise, noisy data...) *  
- Check load on game host (if not enough put visualizer on another port)
- Prepare demo competition