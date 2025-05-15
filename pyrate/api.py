from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import io
from PIL import Image
from pyrate.ui.renderer import render_frame_to_surface
from pydantic import BaseModel
from typing import List
import math
import pygame
import random
import time

from pyrate.engine.game import Game
from pyrate.engine.entities.ship import Ship
from pyrate.engine.entities.projectile import Cannonball

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


class ControlMode(BaseModel):
    mode: str


@app.get("/")
def read_root():
    return {"message": "Welcome to the PyRate API!"}


@app.get("/game/status")
def get_game_status():
    """
    Retrieve general game status: all players' positions, number of enemies, and projectile count.
    """
    players = [
        {"id": idx, "x": p.x, "y": p.y, "is_living": p.is_living}
        for idx, p in enumerate(game.player_ships)
    ]
    enemies = [
        {"id": idx, "x": e.x, "y": e.y, "is_living": e.is_living}
        for idx, e in enumerate(game.enemy_ships)
    ]
    status = {
        "players": players,
        "enemies": enemies,
        "projectile_count": len(game.projectiles),
    }
    return status


@app.get("/players/status", response_model=List[ShipStatus])
def get_all_players_status():
    """
    Retrieve the status of all player ships.
    """
    result = []
    for p in game.player_ships:
        result.append(ShipStatus(
            x=p.x, y=p.y, angle=p.angle, speed=p.speed,
            is_living=p.is_living,
            projectile_count=len(p.projectiles)
        ))
    return result


@app.get("/players/{player_id}/status", response_model=ShipStatus)
def get_player_status(player_id: int):
    """
    Retrieve a single player ship's status by its index.
    """
    try:
        p = game.player_ships[player_id]
    except IndexError:
        raise HTTPException(404, f"No player with id {player_id}")
    return ShipStatus(
        x=p.x, y=p.y, angle=p.angle, speed=p.speed,
        is_living=p.is_living,
        projectile_count=len(p.projectiles)
    )


@app.post("/players/{player_id}/command", response_model=CommandResponse)
def command_player(player_id: int, cmd: Command):
    """
    Issue a command to control a specific player ship.
    """
    try:
        ship = game.player_ships[player_id]
    except IndexError:
        raise HTTPException(404, f"No player with id {player_id}")

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
        raise HTTPException(400, "Unknown command")

    # immediately step one frame so the command takes effect
    game.update()
    return CommandResponse(status="ok")


@app.get("/enemies/status")
def get_enemies_status():
    """
    Retrieve the list of enemy ship statuses.
    """
    enemies_data = []
    for i, enemy in enumerate(game.enemy_ships):
        enemies_data.append({
            "id": i,
            "x": enemy.x,
            "y": enemy.y,
            "angle": enemy.angle,
            "is_living": enemy.is_living,
        })
    return {"enemies": enemies_data}


@app.get("/projectiles/status")
def get_projectiles_status():
    projectiles_data = []
    for proj in game.projectiles:
        projectiles_data.append(ProjectileStatus(
            x=proj.x,
            y=proj.y,
            angle=proj.angle,
            speed=proj.speed,
            radius=getattr(proj, 'radius', 0)
        ))
    return {"projectiles": projectiles_data}


@app.post("/game/update")
def trigger_game_update():
    game.update()
    return {"status": "game updated"}


@app.get("/game/frame")
def get_rendered_frame():
    try:
        surface = render_frame_to_surface(game)
        raw_str = pygame.image.tostring(surface, 'RGB')
        img = Image.frombytes("RGB", surface.get_size(), raw_str)
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/jpeg")
    except Exception:
        raise HTTPException(500, "Failed to render frame")


@app.get("/video/stream")
def stream_video():
    def generate():
        clock = pygame.time.Clock()
        while True:
            surface = render_frame_to_surface(game)
            raw_str = pygame.image.tostring(surface, "RGB")
            img = Image.frombytes("RGB", surface.get_size(), raw_str)
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buf.getvalue() + b"\r\n"
            )
            clock.tick(30)
    return StreamingResponse(generate(),
        media_type="multipart/x-mixed-replace; boundary=frame")


@app.post("/game/control")
def set_control_mode(cm: ControlMode):
    if cm.mode not in ("keyboard", "api"):
        raise HTTPException(400, "mode must be 'keyboard' or 'api'")
    game.control_mode = cm.mode
    return {"status": "ok", "mode": cm.mode}
