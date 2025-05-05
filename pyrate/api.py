from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import math

from pyrate.engine.game import Game
from pyrate.engine.entities.ship import Ship
from pyrate.engine.entities.projectile import Cannonball

# To run the API: uvicorn pyrate.api:app --reload

app = FastAPI()
game = Game()

class ShipStatus(BaseModel):
    x: float
    y: float
    angle: float
    speed: float
    is_living: bool
    projectile_count: int

class ProjectileStatus(BaseModel):
    x: float
    y: float
    angle: float
    speed: float
    radius: float

class Command(BaseModel):
    action: str
    side: str = "left"

class CommandResponse(BaseModel):
    status: str

@app.get("/")
def read_root():
    print(">> Root endpoint hit")
    return {"message": "Welcome to the PyRate API!"}

@app.get("/game/status")
def get_game_status():
    """
    Retrieve general game status: player position, number of enemies, and projectile count.
    """
    status = {
        "player_x": game.player_ship.x,
        "player_y": game.player_ship.y,
        "enemy_count": len(game.enemies),
        "projectile_count": len(game.projectiles),
    }
    print(">> Game status requested:", status)
    return status

@app.get("/player/status", response_model=ShipStatus)
def get_player_status():
    """
    Retrieve the player ship's status.
    """
    player = game.player_ship
    status = ShipStatus(
        x=player.x,
        y=player.y,
        angle=player.angle,
        speed=player.speed,
        is_living=player.is_living,
        projectile_count=len(player.projectiles)
    )
    print(">> Player status:", status)
    return status

@app.post("/player/command", response_model=CommandResponse)
def command_player(cmd: Command):
    """
    Issue a command to control the player ship.
    """
    print(f">> Received command: action={cmd.action}, side={cmd.side}")
    handle_input_api(game.player_ship, cmd)
    game.update()
    return CommandResponse(status="ok")

@app.get("/enemies/status")
def get_enemies_status():
    """
    Retrieve the list of enemy ship statuses.
    """
    enemies_data = []
    for i, enemy in enumerate(game.enemies):
        enemies_data.append({
            "id": i,
            "x": enemy.x,
            "y": enemy.y,
            "angle": enemy.angle,
            "is_living": enemy.is_living,
        })
    print(f">> Enemies status: {enemies_data}")
    return {"enemies": enemies_data}

@app.get("/projectiles/status")
def get_projectiles_status():
    """
    Retrieve the list of projectile statuses.
    """
    projectiles_data = []
    for proj in game.projectiles:
        projectiles_data.append(ProjectileStatus(
            x=proj.x,
            y=proj.y,
            angle=proj.angle,
            speed=proj.speed,
            radius=getattr(proj, 'radius', 0)
        ))
    print(f">> Projectiles status: {projectiles_data}")
    return {"projectiles": projectiles_data}

@app.post("/game/update")
def trigger_game_update():
    """
    Trigger a manual game update on the server.
    """
    print(">> Manual game update triggered")
    game.update()
    return {"status": "game updated"}

# Input handler directly in the API
def handle_input_api(ship: Ship, cmd: Command):
    action = cmd.action.lower()
    if action == "accelerate":
        ship.accelerate()
    elif action == "decelerate":
        ship.decelerate()
    elif action == "turn_left":
        ship.turn_left()
    elif action == "turn_right":
        ship.turn_right()
    elif action == "fire":
        ship.fire(cmd.side)
    else:
        raise HTTPException(status_code=400, detail="Unknown command")
