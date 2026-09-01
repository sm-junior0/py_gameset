"""Interactive game world widget."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.properties import StringProperty
from kivy.uix.widget import Widget

from farmquest.config import GRAVITY, GROUND_Y, PLAYER_JUMP_SPEED, PLAYER_RESPAWN_Y, PLAYER_SPEED, TARGET_FPS, WORLD_WIDTH
from farmquest.data.level_data import build_level
from farmquest.entities.level import RectEntity
from farmquest.entities.player import Player
from farmquest.systems.camera import CameraSystem
from farmquest.systems.collision import resolve_world_collisions
from farmquest.systems.interaction import find_interaction


@dataclass
class InputState:
    """Mutable movement input flags."""

    left: bool = False
    right: bool = False


class GameWorld(Widget):
    """Draws and updates the side-scrolling prototype level."""

    nearby_label = StringProperty("")

    def __init__(
        self,
        on_zone_interaction: Callable[[RectEntity], None],
        on_checkpoint: Callable[[RectEntity], None],
        on_hazard: Callable[[], None],
        avatar_id: str = "sunrise",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.level = build_level()
        self.solids = self.level["solids"]
        self.hazards = self.level["hazards"]
        self.checkpoints = self.level["checkpoints"]
        self.interactions = self.level["interactions"]
        self.player = Player(
            x=float(self.level["spawn_x"]),
            y=float(self.level["spawn_y"]),
            width=48.0,
            height=72.0,
            avatar_id=avatar_id,
        )
        self.spawn_x = self.player.x
        self.spawn_y = self.player.y
        self.input_state = InputState()
        self.camera = CameraSystem(world_width=WORLD_WIDTH, view_width=1280)
        self.on_zone_interaction = on_zone_interaction
        self.on_checkpoint = on_checkpoint
        self.on_hazard = on_hazard
        self.current_zone: RectEntity | None = None
        self.completed_zone_kinds: set[str] = set()
        self.crop_stage = "seed"
        self._update_event = None
        self.start_updates()
        self.bind(pos=self._sync_camera, size=self._sync_camera)

    def _sync_camera(self, *_args) -> None:
        self.camera.view_width = max(1.0, self.width)
        self.canvas.ask_update()

    def set_avatar(self, avatar_id: str) -> None:
        """Change the player's placeholder look."""
        self.player.avatar_id = avatar_id

    def respawn(self) -> None:
        """Move the player back to the latest checkpoint."""
        self.player.respawn(self.spawn_x, self.spawn_y)

    def reset_session(self, avatar_id: str) -> None:
        """Reset world state for a fresh player."""
        self.spawn_x = float(self.level["spawn_x"])
        self.spawn_y = float(self.level["spawn_y"])
        self.player.respawn(self.spawn_x, self.spawn_y)
        self.player.avatar_id = avatar_id
        self.completed_zone_kinds.clear()
        self.crop_stage = "seed"
        self.current_zone = None
        self.nearby_label = ""
        self.input_state.left = False
        self.input_state.right = False
        self.start_updates()

    def start_updates(self) -> None:
        """Start the physics loop if it is not already running."""
        if self._update_event is None:
            self._update_event = Clock.schedule_interval(self.update, 1.0 / TARGET_FPS)

    def stop_updates(self) -> None:
        """Stop the physics loop if it is running."""
        if self._update_event is not None:
            self._update_event.cancel()
            self._update_event = None

    def mark_zone_completed(self, kind: str) -> None:
        """Hide a completed single-use interaction zone."""
        self.completed_zone_kinds.add(kind)

    def trigger_jump(self) -> None:
        """Attempt to jump."""
        if self.player.on_ground:
            self.player.velocity_y = PLAYER_JUMP_SPEED
            self.player.on_ground = False

    def update(self, dt: float) -> None:
        """Advance physics and redraw the world."""
        previous_x = self.player.x
        previous_y = self.player.y

        self.player.velocity_x = 0.0
        if self.input_state.left and not self.input_state.right:
            self.player.velocity_x = -PLAYER_SPEED
        elif self.input_state.right and not self.input_state.left:
            self.player.velocity_x = PLAYER_SPEED

        self.player.velocity_y += GRAVITY * dt
        self.player.x += self.player.velocity_x * dt
        self.player.y += self.player.velocity_y * dt
        self.player.x = max(0.0, min(self.player.x, WORLD_WIDTH - self.player.width))

        resolve_world_collisions(self.player, self.solids, previous_x, previous_y)

        if self.player.y < PLAYER_RESPAWN_Y:
            self.on_hazard()
            self.respawn()

        for hazard in self.hazards:
            if self.player.intersects(hazard):
                self.on_hazard()
                self.respawn()
                break

        for checkpoint in self.checkpoints:
            if self.player.intersects(checkpoint):
                self.spawn_x = checkpoint.x
                self.spawn_y = checkpoint.y
                self.on_checkpoint(checkpoint)

        active_interactions = [
            zone
            for zone in self.interactions
            if zone.kind not in self.completed_zone_kinds
        ]
        self.current_zone = find_interaction(self.player, active_interactions)
        self.nearby_label = self.current_zone.label if self.current_zone else ""
        self.camera.update(self.player.x + (self.player.width / 2))
        self.redraw()

    def interact(self) -> None:
        """Trigger the nearby interaction zone if present."""
        if self.current_zone is not None:
            self.on_zone_interaction(self.current_zone)

    def redraw(self) -> None:
        """Draw the world with placeholder shapes."""
        offset = self.camera.offset_x
        self.canvas.clear()
        with self.canvas:
            Color(0.72, 0.9, 1.0, 1.0)
            Rectangle(pos=self.pos, size=self.size)

            Color(0.95, 0.87, 0.62, 1.0)
            Ellipse(pos=(self.x + self.width - 180, self.y + self.height - 160), size=(120, 120))

            self._draw_hills(offset)
            self._draw_solids(offset)
            self._draw_hazards(offset)
            self._draw_checkpoints(offset)
            self._draw_interactions(offset)
            self._draw_crop(offset)
            self._draw_player(offset)

    def _world_to_screen(self, x: float, y: float) -> tuple[float, float]:
        return self.x + x - self.camera.offset_x, self.y + y

    def _draw_hills(self, offset: float) -> None:
        Color(0.57, 0.78, 0.45, 1.0)
        Rectangle(pos=(self.x - (offset * 0.2), self.y + 60), size=(self.width + 400, 180))
        Color(0.42, 0.66, 0.3, 1.0)
        Rectangle(pos=(self.x - (offset * 0.35), self.y + 30), size=(self.width + 500, 120))

    def _draw_solids(self, offset: float) -> None:
        for solid in self.solids:
            screen_x, screen_y = self._world_to_screen(solid.x, solid.y)
            Color(0.45, 0.31, 0.18, 1.0) if solid.kind == "ground" else Color(0.53, 0.38, 0.23, 1.0)
            Rectangle(pos=(screen_x, screen_y), size=(solid.width, solid.height))

    def _draw_hazards(self, offset: float) -> None:
        for hazard in self.hazards:
            screen_x, screen_y = self._world_to_screen(hazard.x, hazard.y)
            Color(0.39, 0.24, 0.14, 1.0)
            Rectangle(pos=(screen_x, screen_y), size=(hazard.width, hazard.height))
            Color(0.18, 0.14, 0.1, 1.0)
            Line(rectangle=(screen_x, screen_y, hazard.width, hazard.height), width=2)

    def _draw_checkpoints(self, offset: float) -> None:
        for checkpoint in self.checkpoints:
            screen_x, screen_y = self._world_to_screen(checkpoint.x, checkpoint.y)
            Color(1.0, 0.86, 0.2, 0.45)
            Rectangle(pos=(screen_x, screen_y), size=(checkpoint.width, checkpoint.height))

    def _draw_interactions(self, offset: float) -> None:
        for zone in self.interactions:
            if zone.kind in self.completed_zone_kinds:
                continue
            screen_x, screen_y = self._world_to_screen(zone.x, zone.y)
            if zone == self.current_zone:
                Color(0.1, 0.3, 0.8, 0.55)
            else:
                Color(0.0, 0.0, 0.0, 0.18)
            Rectangle(pos=(screen_x, screen_y), size=(zone.width, zone.height))
            Color(1.0, 1.0, 1.0, 0.8)
            Line(rectangle=(screen_x, screen_y, zone.width, zone.height), width=2)

    def _draw_crop(self, offset: float) -> None:
        crop_x, crop_y = self._world_to_screen(2485, GROUND_Y + 20)
        stage = self.crop_stage
        if stage == "seed":
            Color(0.53, 0.33, 0.12, 1.0)
            Ellipse(pos=(crop_x + 10, crop_y), size=(12, 12))
        elif stage == "growing":
            Color(0.17, 0.58, 0.16, 1.0)
            Rectangle(pos=(crop_x + 10, crop_y), size=(10, 46))
            Rectangle(pos=(crop_x + 24, crop_y + 14), size=(10, 32))
        else:
            Color(0.88, 0.76, 0.19, 1.0)
            Rectangle(pos=(crop_x + 12, crop_y), size=(8, 60))
            Rectangle(pos=(crop_x + 26, crop_y + 10), size=(8, 54))

    def _draw_player(self, offset: float) -> None:
        screen_x, screen_y = self._world_to_screen(self.player.x, self.player.y)
        body = (0.9, 0.45, 0.28, 1.0) if self.player.avatar_id == "sunrise" else (0.22, 0.62, 0.82, 1.0)
        Color(*body)
        Rectangle(pos=(screen_x, screen_y), size=(self.player.width, self.player.height))
        Color(0.12, 0.12, 0.12, 1.0)
        Rectangle(pos=(screen_x + 8, screen_y + 52), size=(10, 10))
        Rectangle(pos=(screen_x + 30, screen_y + 52), size=(10, 10))
