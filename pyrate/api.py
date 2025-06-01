from typing import Literal
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import io
from PIL import Image
from pyrate.ui.renderer import render_frame_to_surface
from pydantic import BaseModel
import pygame

from pyrate.engine.game import Game

app = FastAPI()
game = Game()


class FireTimestamp(BaseModel):
    left: float
    right: float


class ShipStatus(BaseModel):
    angle: float
    rotation_velocity: float
    speed: float
    health: float
    is_living: bool
    last_fire_time: FireTimestamp


class Command(BaseModel):
    action: str
    side: Literal["left", "right"]


class CommandResponse(BaseModel):
    status: str


class ControlMode(BaseModel):
    mode: str


@app.get("/")
def read_root():
    return {"message": "Welcome to the PyRate API!"}


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
        angle=p.angle, 
        rotation_velocity=p.rotation_velocity,
        speed=p.speed,
        health=p.health,
        is_living=p.is_living,
        last_fire_time=p.last_fire_time
    )


@app.get("/players/{player_id}/sensor")
def get_sensor_status(player_id: int):
    """
    Retrieve the list of enemy ship statuses.
    """
    try:
        p = game.player_ships[player_id]
    except IndexError:
        raise HTTPException(404, f"No player with id {player_id}")
    return {"nearby_ships": game.get_ship_sensor(p)}


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

    return CommandResponse(status="ok")


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
            # NOTE: Can be lowered to reduce load on the server
            clock.tick(30) # Video stream frate rate
    return StreamingResponse(generate(),
        media_type="multipart/x-mixed-replace; boundary=frame")


@app.post("/game/control")
def set_control_mode(cm: ControlMode):
    if cm.mode not in ("keyboard", "api"):
        raise HTTPException(400, "mode must be 'keyboard' or 'api'")
    game.control_mode = cm.mode
    return {"status": "ok", "mode": cm.mode}
