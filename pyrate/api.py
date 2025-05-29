from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import io
from PIL import Image
from pyrate.ui.renderer import render_frame_to_surface
from pydantic import BaseModel
from typing import List
import math
import pygame
import time

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

class DetectedShip(BaseModel):
    x: float
    y: float
    angle: float
    distance: float
    is_living: bool

class Command(BaseModel):
    action: str
    side: str = "left"

class CommandResponse(BaseModel):
    status: str

@app.get("/player/sensors", response_model=List[DetectedShip])
def get_player_sensors():
    game.update_sensors()
    detected = game.player_ship.detected_ships

    result = []
    for ship_data in detected:
        result.append(DetectedShip(
            x=ship_data["x"],
            y=ship_data["y"],
            angle=ship_data["angle"],
            distance=ship_data["distance"],
            is_living=ship_data["ship"].is_living
        ))

    print(f">> Player sensors detect {len(result)} ships")
    return result



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

@app.get("/game/frame")
def get_rendered_frame():
    """
    Return the current rendered frame as a JPEG image.
    """
    try:
        surface = render_frame_to_surface(game)
        raw_str = pygame.image.tostring(surface, 'RGB')
        img = Image.frombytes("RGB", surface.get_size(), raw_str)

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        buffer.seek(0)

        return StreamingResponse(buffer, media_type="image/jpeg")
    except Exception as e:
        print(f"Error rendering frame: {e}")
        raise HTTPException(status_code=500, detail="Failed to render frame")

@app.get("/video/stream")
def stream_video():
    """
    Stream the game video as MJPEG.
    """
    def generate():
        clock = pygame.time.Clock()
        while True:
            surface = render_frame_to_surface(game)
            raw_str = pygame.image.tostring(surface, "RGB")
            image = Image.frombytes("RGB", surface.get_size(), raw_str)
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG")
            frame = buffer.getvalue()

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )

            clock.tick(30)  # FPS target

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

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
    