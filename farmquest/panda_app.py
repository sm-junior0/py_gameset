"""Pitch-ready Panda3D prototype for FarmQuest: From Seed to Plate."""

from __future__ import annotations

from dataclasses import dataclass
from math import sin
from textwrap import wrap
from time import monotonic
from typing import Callable

from farmquest.config import AUDIO_PATHS
from farmquest.entities.game_state import ProgressState
from farmquest.managers.game_state_manager import GameStateManager


@dataclass(slots=True)
class Station:
    """An interactive stop in the farm-to-table journey."""

    kind: str
    label: str
    x: float
    y: float
    color: tuple[float, float, float, float]


class FarmQuest3DApp:
    """A colorful, guided 3D farm-to-table game prototype."""

    def __init__(self) -> None:
        from direct.gui.DirectGui import DirectButton, DirectFrame
        from direct.gui.OnscreenText import OnscreenText
        from direct.showbase.ShowBase import ShowBase
        from panda3d.core import (
            AmbientLight,
            CardMaker,
            ClockObject,
            DirectionalLight,
            TextNode,
            TransparencyAttrib,
            WindowProperties,
        )

        self.DirectButton = DirectButton
        self.DirectFrame = DirectFrame
        self.OnscreenText = OnscreenText
        self.ShowBase = ShowBase
        self.CardMaker = CardMaker
        self.TextNode = TextNode
        self.TransparencyAttrib = TransparencyAttrib
        self.clock = ClockObject.getGlobalClock()

        class _Base(ShowBase):
            pass

        self.base = _Base()
        self.base.disableMouse()
        self.base.setBackgroundColor(0.58, 0.8, 0.94, 1)
        props = WindowProperties()
        props.setTitle("FarmQuest 3D: From Seed to Plate")
        props.setSize(1280, 720)
        if self.base.win is not None:
            self.base.win.requestProperties(props)

        self.state_manager = GameStateManager()
        self.mode = "title"
        self.avatar_id = "sunrise"
        self.keys: set[str] = set()
        self.completed: set[str] = set()
        self.repeat_counts: dict[str, int] = {}
        self.velocity_z = 0.0
        self.grounded = True
        self.nearby: Station | None = None
        self.last_progress = monotonic()
        self.message_until = 0.0
        self.overlay_feedback = None
        self.player = None
        self.crop_node = None
        self.cart_node = None
        self.station_nodes: dict[str, object] = {}
        self.station_label_nodes: dict[str, object] = {}
        self.music = None
        self.sounds: dict[str, object] = {}
        self.menu_nodes: list[object] = []
        self.hud_nodes: list[object] = []
        self.world_nodes: list[object] = []
        self.stations = self._stations()

        self._setup_lighting()
        self._load_audio()
        self._bind_controls()
        self.show_title()
        self.base.taskMgr.add(self._update, "farmquest-frame")

    def run(self) -> None:
        """Run the Panda3D application."""
        self.base.run()

    def _setup_lighting(self) -> None:
        ambient = self._ambient_light("ambient", (0.56, 0.6, 0.62, 1))
        sun = self._directional_light("sun", (1.0, 0.9, 0.68, 1), (-38, -48, 0))
        fill = self._directional_light("fill", (0.28, 0.42, 0.5, 1), (120, -20, 0))
        self.base.render.setLight(ambient)
        self.base.render.setLight(sun)
        self.base.render.setLight(fill)

    def _ambient_light(self, name: str, color):
        from panda3d.core import AmbientLight

        light = AmbientLight(name)
        light.setColor(color)
        return self.base.render.attachNewNode(light)

    def _directional_light(self, name: str, color, hpr):
        from panda3d.core import DirectionalLight

        light = DirectionalLight(name)
        light.setColor(color)
        node = self.base.render.attachNewNode(light)
        node.setHpr(*hpr)
        return node

    def _bind_controls(self) -> None:
        for key in ["w", "a", "s", "d", "arrow_left", "arrow_right", "space", "shift", "e", "escape"]:
            self.base.accept(key, self._key_down, [key])
            self.base.accept(f"{key}-up", self._key_up, [key])

    def _stations(self) -> list[Station]:
        blue = (0.1, 0.38, 0.9, 0.92)
        green = (0.1, 0.62, 0.32, 0.92)
        gold = (0.95, 0.7, 0.12, 0.92)
        clay = (0.78, 0.42, 0.22, 0.92)
        return [
            Station("question_1", "Soil Question", 9, 0, blue),
            Station("collect_seed", "Hidden Seed", 17, -4.2, gold),
            Station("prepare_soil", "Prepare Soil", 25, 0, clay),
            Station("question_2", "Planting Question", 30, 0, blue),
            Station("plant_seed", "Plant Seed", 35, 0, green),
            Station("water_crop", "Water Source", 42, 3.8, blue),
            Station("protect_crop", "Remove Weed", 48, 0, green),
            Station("question_3", "Crop-Care Question", 53, 0, blue),
            Station("start_growth", "Time Passing", 58, 0, gold),
            Station("mature_crop", "Grow Crop", 63, 0, gold),
            Station("harvest_crop", "Harvest", 68, 0, green),
            Station("process_maize", "Maize Mill", 76, -2.2, clay),
            Station("cook_meal", "Kitchen", 86, 2.6, clay),
            Station("serve_meal", "Serving Table", 96, 0, gold),
        ]

    def show_title(self) -> None:
        """Show the main menu."""
        self.mode = "title"
        self._play_music()
        self._clear_menu()
        self._clear_hud()
        self._clear_world()
        self.menu_nodes.append(self._panel(-1.2, 1.2, -0.78, 0.78, (0.91, 0.97, 0.84, 0.96)))
        self.menu_nodes.append(self._text("FarmQuest 3D", 0, 0.42, 0.135, (0.03, 0.18, 0.12, 1), shadow=True))
        self.menu_nodes.append(self._text("From Seed to Plate", 0, 0.25, 0.062, (0.32, 0.23, 0.08, 1)))
        self.menu_nodes.append(
            self._text(
                "A guided agriculture adventure for events: players learn by doing and earn a virtual reward.",
                0,
                0.11,
                0.045,
                (0.08, 0.27, 0.18, 1),
                width=42,
            )
        )
        self.menu_nodes.append(self._button("Start Adventure", (0, 0, -0.12), self.show_character_select, scale=0.085))
        self.menu_nodes.append(self._button("Pitch Overview", (-0.34, 0, -0.34), self.show_pitch_overview, scale=0.058, color=(0.85, 0.95, 0.97, 1)))
        self.menu_nodes.append(self._button("Staff Reset", (0.34, 0, -0.34), self.staff_reset, scale=0.058, color=(0.85, 0.95, 0.97, 1)))

    def show_pitch_overview(self) -> None:
        """Show a concise leader-facing explanation."""
        self.mode = "pitch"
        self._clear_menu()
        self._clear_hud()
        self._clear_world()
        self.menu_nodes.append(self._panel(-1.28, 1.28, -0.78, 0.78, (0.94, 0.98, 0.9, 0.97)))
        self.menu_nodes.append(self._text("Pitch Overview", 0, 0.47, 0.095, (0.03, 0.18, 0.12, 1), shadow=True))
        body = (
            "Players choose a character and crop, then complete a simple adventure: find seed, prepare soil, "
            "plant, water, protect, harvest, mill, cook, and serve.\n\n"
            "Every stage gives visible points. Today the reward is virtual; later, real coupons or sponsor prizes "
            "should be issued only through secure server-side verification.\n\n"
            "The event music studio can place the authorized theme at assets/audio/original_event_theme.ogg."
        )
        self.menu_nodes.append(self._text(body, 0, 0.08, 0.045, (0.06, 0.23, 0.15, 1), width=68))
        self.menu_nodes.append(self._button("Play Demo", (-0.28, 0, -0.55), self.show_character_select, scale=0.06))
        self.menu_nodes.append(self._button("Back", (0.28, 0, -0.55), self.show_title, scale=0.06, color=(0.85, 0.95, 0.97, 1)))

    def show_character_select(self) -> None:
        """Choose one of two original avatars."""
        self.mode = "menu"
        self._clear_menu()
        self.menu_nodes.append(self._panel(-1.25, 1.25, -0.78, 0.78, (0.94, 0.98, 0.9, 0.96)))
        self.menu_nodes.append(self._text("Choose Your Explorer", 0, 0.46, 0.09, (0.03, 0.18, 0.12, 1), shadow=True))
        self.menu_nodes.append(self._avatar_card("Sunrise Explorer", "sunrise", -0.42, (0.92, 0.38, 0.2, 1)))
        self.menu_nodes.append(self._avatar_card("River Explorer", "river", 0.42, (0.14, 0.52, 0.78, 1)))

    def show_crop_select(self, avatar_id: str) -> None:
        """Choose maize and preview future crops."""
        self.avatar_id = avatar_id
        self.mode = "menu"
        self._clear_menu()
        self.menu_nodes.append(self._panel(-1.25, 1.25, -0.78, 0.78, (0.91, 0.97, 0.88, 0.96)))
        self.menu_nodes.append(self._text("Choose What to Plant", 0, 0.46, 0.09, (0.03, 0.18, 0.12, 1), shadow=True))
        self.menu_nodes.append(self._crop_card("Maize", "Play Now", -0.62, 0.16, self.start_game, (0.96, 0.78, 0.2, 1)))
        locked = [("Beans", -0.2), ("Potatoes", 0.22), ("Bananas", 0.64), ("Coffee", 1.06)]
        for crop, x in locked:
            self.menu_nodes.append(self._crop_card(crop, "Coming Soon", x - 0.42, -0.2, lambda: None, (0.62, 0.69, 0.63, 1)))

    def start_game(self) -> None:
        """Start a full maize journey."""
        self.mode = "game"
        self._play_music()
        self._clear_menu()
        self._clear_hud()
        self._clear_world()
        self.state_manager.reset()
        self.state_manager.select_avatar(self.avatar_id)
        self.state_manager.start_game()
        self.completed.clear()
        self.repeat_counts.clear()
        self.velocity_z = 0.0
        self.grounded = True
        self.nearby = None
        self.last_progress = monotonic()
        self._build_world()
        self._build_hud()
        self._toast("W/A/S/D move. Shift runs. Space jumps. E interacts.")

    def show_results(self) -> None:
        """Show final score and reward."""
        self.mode = "results"
        self._play_sound("complete")
        self._clear_menu()
        self._clear_hud()
        results = self.state_manager.results()
        seconds = int(float(results["completion_time"]))
        minutes, seconds = divmod(seconds, 60)
        self.menu_nodes.append(self._panel(-1.28, 1.28, -0.78, 0.78, (0.93, 0.97, 0.87, 0.97)))
        self.menu_nodes.append(self._text("Journey Complete", 0, 0.47, 0.095, (0.03, 0.18, 0.12, 1), shadow=True))
        summary = (
            f"Final Score: {results['total_score']}/100\n"
            f"Knowledge {results['knowledge_score']}   Accuracy {results['accuracy_score']}   Completion {results['completion_score']}\n"
            f"Time {minutes:02d}:{seconds:02d}\n"
            f"Virtual Reward: {results['reward']}\n"
            "Seed -> soil -> planting -> watering -> care -> harvest -> mill -> cook -> serve"
        )
        self.menu_nodes.append(self._text(summary, 0, 0.15, 0.052, (0.08, 0.25, 0.17, 1), width=46))
        self.menu_nodes.append(self._button("Play Again", (-0.32, 0, -0.42), self.show_character_select, scale=0.065))
        self.menu_nodes.append(self._button("Title", (0.32, 0, -0.42), self.show_title, scale=0.065, color=(0.85, 0.95, 0.97, 1)))

    def staff_reset(self) -> None:
        """Reset local session state for event staff."""
        self.state_manager.reset()
        self.completed.clear()
        self.repeat_counts.clear()
        self.show_title()

    def _build_world(self) -> None:
        self.world_nodes.append(self._plane("meadow", 112, 20, (55, 0, -0.04), (0.31, 0.68, 0.33, 1)))
        self.world_nodes.append(self._plane("golden-path", 108, 3.4, (55, 0, 0.0), (0.82, 0.67, 0.39, 1)))
        self.world_nodes.append(self._plane("water", 10, 5, (42, 5.2, 0.02), (0.2, 0.62, 0.86, 0.82)))
        self.world_nodes[-1].setTransparency(self.TransparencyAttrib.MAlpha)
        self._build_area_landmarks()
        self._build_obstacles()
        self._build_crop_rows()
        self.player = self._box("player", (1, 0, 1.1), (0.75, 0.75, 1.8), self._avatar_color())
        self.world_nodes.append(self.player)
        head = self._box("player-head", (1, 0, 2.35), (0.55, 0.55, 0.55), (0.42, 0.25, 0.15, 1))
        head.reparentTo(self.player)
        head.setPos(0, 0, 0.78)
        self.crop_node = self._box("hero-crop", (35, 1.9, 0.3), (0.35, 0.35, 0.55), (0.43, 0.25, 0.12, 1))
        self.world_nodes.append(self.crop_node)
        self.cart_node = self._box("harvest-cart", (70, -1.4, 0.45), (1.4, 0.9, 0.7), (0.62, 0.37, 0.18, 1))
        self.world_nodes.append(self.cart_node)
        self._build_path_arrows()
        for station in self.stations:
            beacon = self._box(f"beacon-{station.kind}", (station.x, station.y, 0.08), (1.25, 1.25, 0.14), station.color)
            beacon.setTransparency(self.TransparencyAttrib.MAlpha)
            self.station_nodes[station.kind] = beacon
            self.world_nodes.append(beacon)
            sign = self._sign(station.label, station.x, station.y, 1.65)
            self.station_label_nodes[station.kind] = sign
            self.world_nodes.append(sign)

    def _build_area_landmarks(self) -> None:
        for x, label, color in [
            (2, "Welcome", (0.9, 0.96, 0.68, 1)),
            (25, "Farm Plot", (0.66, 0.38, 0.19, 1)),
            (42, "Water", (0.24, 0.67, 0.9, 1)),
            (76, "Mill", (0.76, 0.55, 0.33, 1)),
            (86, "Kitchen", (0.92, 0.88, 0.72, 1)),
            (96, "Serve", (0.96, 0.78, 0.18, 1)),
        ]:
            self.world_nodes.append(self._box(f"arch-{label}", (x, -2.8, 1.4), (0.35, 0.35, 2.8), color))
            self.world_nodes.append(self._box(f"arch-top-{label}", (x, -2.8, 2.85), (2.5, 0.28, 0.35), color))
            self.world_nodes.append(self._sign(label, x, -3.15, 3.35, scale=0.48))
        self.world_nodes.append(self._box("mill-house", (76, -5, 2.1), (4.8, 3.6, 4.2), (0.72, 0.52, 0.31, 1)))
        self.world_nodes.append(self._box("mill-roof", (76, -5, 4.45), (5.4, 4.0, 0.55), (0.44, 0.18, 0.12, 1)))
        self.world_nodes.append(self._box("kitchen-house", (86, 4.7, 1.9), (4.8, 3.8, 3.8), (0.92, 0.9, 0.76, 1)))
        self.world_nodes.append(self._box("kitchen-roof", (86, 4.7, 4.05), (5.4, 4.3, 0.55), (0.22, 0.47, 0.58, 1)))
        self.world_nodes.append(self._box("serving-table", (96, 0, 0.75), (2.5, 1.2, 0.45), (0.58, 0.31, 0.15, 1)))

    def _build_obstacles(self) -> None:
        for x in [13, 21.5, 38.5, 61]:
            self.world_nodes.append(self._box(f"log-{x}", (x, 0, 0.46), (1.55, 1.0, 0.85), (0.5, 0.28, 0.12, 1)))
        for x in [6, 14, 22, 31, 47, 59, 73, 90, 101]:
            self.world_nodes.append(self._box(f"tree-trunk-{x}", (x, -8.2, 1.0), (0.45, 0.45, 2.0), (0.36, 0.2, 0.1, 1)))
            self.world_nodes.append(self._box(f"tree-top-{x}", (x, -8.2, 2.55), (1.7, 1.7, 1.3), (0.08, 0.42, 0.21, 1)))
            self.world_nodes.append(self._box(f"shrub-{x}", (x + 1.8, 7.4, 0.55), (1.0, 1.0, 0.7), (0.2, 0.55, 0.27, 1)))

    def _build_crop_rows(self) -> None:
        for row_y in [1.8, 2.8, 3.8]:
            for x in [44, 45.2, 46.4, 47.6, 48.8]:
                self.world_nodes.append(self._box(f"maize-{x}-{row_y}", (x, row_y, 1.1), (0.22, 0.22, 2.2), (0.15, 0.58, 0.2, 1)))
                self.world_nodes.append(self._box(f"maize-cob-{x}-{row_y}", (x + 0.18, row_y, 1.6), (0.22, 0.14, 0.5), (0.92, 0.76, 0.18, 1)))

    def _build_path_arrows(self) -> None:
        """Create a quiet visual guide along the main adventure route."""
        for x in range(6, 98, 6):
            arrow = self._box(f"path-arrow-{x}", (x, -1.35, 0.06), (0.9, 0.18, 0.08), (0.96, 0.78, 0.2, 0.72))
            arrow.setTransparency(self.TransparencyAttrib.MAlpha)
            self.world_nodes.append(arrow)

    def _build_hud(self) -> None:
        self.hud_nodes.append(self._panel(-1.34, 1.34, 0.72, 0.98, (0.03, 0.14, 0.1, 0.84)))
        self.objective_text = self._text("", -1.27, 0.89, 0.042, (1, 1, 1, 1), align=self.TextNode.ALeft, parent_list=self.hud_nodes)
        self.message_text = self._text("", -1.27, 0.78, 0.037, (0.96, 0.84, 0.35, 1), align=self.TextNode.ALeft, parent_list=self.hud_nodes)
        self.score_text = self._text("", 1.26, 0.88, 0.047, (0.98, 0.86, 0.28, 1), align=self.TextNode.ARight, parent_list=self.hud_nodes)
        self.hud_nodes.extend([self.objective_text, self.message_text, self.score_text])
        self.hud_nodes.append(self._panel(-1.28, -0.16, -0.96, -0.8, (0.04, 0.16, 0.12, 0.75)))
        self.controls_text = self._text("WASD move | Shift run | Space jump | E interact | Esc title", -1.24, -0.9, 0.032, (1, 1, 1, 1), align=self.TextNode.ALeft, parent_list=self.hud_nodes)
        self.hud_nodes.append(self.controls_text)

    def _update(self, task):
        if self.mode == "game" and self.player is not None:
            dt = min(self.clock.getDt(), 0.033)
            self._move_player(dt)
            self._update_camera()
            self._update_crop()
            self._update_cart()
            self._animate_markers()
            self._update_hud()
        return task.cont

    def _move_player(self, dt: float) -> None:
        speed = 9.5 if "shift" in self.keys else 5.6
        dx = (1 if "d" in self.keys or "arrow_right" in self.keys else 0) - (1 if "a" in self.keys or "arrow_left" in self.keys else 0)
        dy = (1 if "w" in self.keys else 0) - (1 if "s" in self.keys else 0)
        pos = self.player.getPos()
        new_x = max(0.4, min(101.5, pos.x + dx * speed * dt))
        new_y = max(-5.8, min(5.8, pos.y + dy * speed * dt))
        if dx or dy:
            if abs(dx) >= abs(dy):
                self.player.setH(90 if dx > 0 else -90)
            else:
                self.player.setH(0 if dy > 0 else 180)
        self.velocity_z -= 18.5 * dt
        new_z = pos.z + self.velocity_z * dt
        if new_z <= 1.1:
            new_z = 1.1
            self.velocity_z = 0
            self.grounded = True
        self.player.setPos(new_x, new_y, new_z)
        self.nearby = self._nearest_station(new_x, new_y)
        if monotonic() - self.last_progress > 30:
            self._toast(self.state_manager.current_hint())
            self.last_progress = monotonic()

    def _nearest_station(self, x: float, y: float) -> Station | None:
        for station in self.stations:
            if station.kind in self.completed:
                continue
            if abs(station.x - x) <= 2.0 and abs(station.y - y) <= 2.0:
                return station
        return None

    def _update_camera(self) -> None:
        pos = self.player.getPos()
        bob = sin(monotonic() * 0.7) * 0.06
        self.base.camera.setPos(pos.x - 8.8, pos.y - 9.2, 6.4 + bob)
        self.base.camera.lookAt(pos.x + 2.4, pos.y, 1.7)

    def _update_crop(self) -> None:
        if self.crop_node is None:
            return
        stage = self.state_manager.crop_manager.stage
        if stage == "seed":
            self.crop_node.setScale(0.35, 0.35, 0.55)
            self.crop_node.setColor(0.43, 0.25, 0.12, 1)
            self.crop_node.setZ(0.3)
        elif stage == "growing":
            self.crop_node.setScale(0.55, 0.55, 2.1)
            self.crop_node.setColor(0.16, 0.58, 0.2, 1)
            self.crop_node.setZ(1.05)
        else:
            self.crop_node.setScale(0.8, 0.8, 2.9)
            self.crop_node.setColor(0.92, 0.74, 0.16, 1)
            self.crop_node.setZ(1.45)

    def _update_cart(self) -> None:
        if self.cart_node is None or self.player is None:
            return
        if self.state_manager.state == ProgressState.CROP_HARVESTED:
            pos = self.player.getPos()
            self.cart_node.show()
            self.cart_node.setPos(pos.x - 1.4, pos.y - 0.9, 0.45)
        elif self.state_manager.state == ProgressState.MAIZE_PROCESSED:
            self.cart_node.setPos(78, -2.5, 0.45)
            self.cart_node.setColor(0.86, 0.82, 0.68, 1)
            self.cart_node.show()
        elif self.state_manager.state in {ProgressState.MEAL_COOKED, ProgressState.COMPLETED}:
            self.cart_node.hide()
        else:
            self.cart_node.setPos(70, -1.4, 0.45)
            self.cart_node.show()

    def _animate_markers(self) -> None:
        pulse = 1 + sin(monotonic() * 4.0) * 0.12
        current_kind = self._next_station_kind()
        for kind, node in self.station_nodes.items():
            label = self.station_label_nodes.get(kind)
            if kind in self.completed:
                node.hide()
                if label is not None:
                    label.hide()
            elif kind == current_kind:
                node.show()
                if label is not None:
                    label.show()
                node.setColor(*self._station_by_kind(kind).color)
                node.setScale(1.25 * pulse, 1.25 * pulse, 0.16 * pulse)
            else:
                node.show()
                if label is not None:
                    label.hide()
                node.setColor(0.72, 0.78, 0.72, 0.34)
                node.setScale(0.72, 0.72, 0.08)

    def _next_station_kind(self) -> str | None:
        for station in self.stations:
            if station.kind not in self.completed:
                return station.kind
        return None

    def _station_by_kind(self, kind: str) -> Station:
        for station in self.stations:
            if station.kind == kind:
                return station
        raise KeyError(kind)

    def _update_hud(self) -> None:
        self.objective_text.setText(f"Objective: {self.state_manager.current_objective()}")
        self.score_text.setText(f"Score {self.state_manager.score_manager.total_score}/100")
        if monotonic() > self.message_until:
            nearby = self.nearby.label if self.nearby else "Follow the glowing path markers"
            self.message_text.setText(f"Nearby: {nearby}")

    def _key_down(self, key: str) -> None:
        self.keys.add(key)
        if self.mode != "game":
            return
        if key == "space" and self.grounded:
            self.velocity_z = 7.8
            self.grounded = False
            self._play_sound("jump")
        elif key == "e":
            self._interact()
        elif key == "escape":
            self.show_title()

    def _key_up(self, key: str) -> None:
        self.keys.discard(key)

    def _interact(self) -> None:
        if self.nearby is None:
            self._toast("Move closer to a glowing station marker.")
            return
        kind = self.nearby.kind
        if kind.startswith("question_"):
            self._show_question(kind)
            return
        if kind == "prepare_soil":
            self._repeat(kind, 3, "Hoe the highlighted soil", "Soil prepared.")
            return
        if kind == "water_crop":
            self._repeat(kind, 3, "Fill the water indicator", "Crop watered.")
            return
        if kind == "cook_meal":
            self._show_cooking()
            return
        result = self.state_manager.attempt_action(kind)
        self._toast(result.message)
        if result.success:
            self._complete(kind)
            effect_map = {
                "collect_seed": "seed",
                "plant_seed": "plant",
                "protect_crop": "growth",
                "start_growth": "growth",
                "mature_crop": "growth",
                "harvest_crop": "harvest",
                "process_maize": "mill",
                "serve_meal": "complete",
            }
            self._play_sound(effect_map.get(kind, ""))
            if kind == "start_growth":
                self._toast("Growth is accelerated for this game. Real maize requires much more time and continued care.", seconds=5)
            if kind == "serve_meal":
                self.show_results()

    def _repeat(self, kind: str, target: int, progress: str, done: str) -> None:
        count = self.repeat_counts.get(kind, 0) + 1
        self.repeat_counts[kind] = count
        if count < target:
            self._toast(f"{progress}: {count}/{target}")
            return
        result = self.state_manager.attempt_action(kind)
        self._toast(done if result.success else result.message)
        if result.success:
            self._complete(kind)
            self._play_sound("soil" if kind == "prepare_soil" else "water")

    def _complete(self, kind: str) -> None:
        self.completed.add(kind)
        self.last_progress = monotonic()
        self._toast(f"Stage complete. Score {self.state_manager.score_manager.total_score}/100")

    def _show_question(self, question_id: str) -> None:
        self.mode = "overlay"
        self._clear_hud()
        question = self.state_manager.quiz_manager.get_question(question_id)
        self.menu_nodes.append(self._panel(-1.18, 1.18, -0.72, 0.72, (0.94, 0.98, 0.9, 0.97)))
        self.menu_nodes.append(self._text(str(question["prompt"]), 0, 0.43, 0.065, (0.03, 0.18, 0.12, 1), width=42))
        self.overlay_feedback = self._text("", 0, -0.5, 0.04, (0.58, 0.2, 0.11, 1), width=58)
        self.menu_nodes.append(self.overlay_feedback)
        for index, choice in enumerate(question["choices"]):
            self.menu_nodes.append(
                self._button(str(choice), (0, 0, 0.17 - index * 0.18), lambda idx=index: self._answer_question(question_id, idx), scale=0.065)
            )

    def _answer_question(self, question_id: str, index: int) -> None:
        result = self.state_manager.submit_question(question_id, index)
        if result["correct"]:
            self.completed.add(question_id)
            self.mode = "game"
            self._clear_menu()
            self._build_hud()
            self._toast("Correct. " + str(result["feedback"]), seconds=5)
            self.last_progress = monotonic()
        else:
            if self.overlay_feedback is not None:
                self.overlay_feedback.setText("Not quite. " + str(result["feedback"]))

    def _show_cooking(self) -> None:
        self.mode = "overlay"
        self._clear_hud()
        self._clear_menu()
        self.menu_nodes.append(self._panel(-1.1, 1.1, -0.7, 0.7, (0.94, 0.98, 0.9, 0.97)))
        self.menu_nodes.append(self._text("Cooking Mini-Game", 0, 0.43, 0.08, (0.03, 0.18, 0.12, 1), shadow=True))
        self.menu_nodes.append(self._text(f"Next: {self.state_manager.cooking_manager.current_step.title()}", 0, 0.26, 0.052, (0.12, 0.29, 0.18, 1)))
        self.overlay_feedback = self._text("", 0, -0.52, 0.04, (0.58, 0.2, 0.11, 1), width=54)
        self.menu_nodes.append(self.overlay_feedback)
        for index, step in enumerate(["heat pot", "add flour", "stir"]):
            self.menu_nodes.append(self._button(step.title(), (0, 0, 0.05 - index * 0.16), lambda selected=step: self._cook_step(selected), scale=0.065))

    def _cook_step(self, step: str) -> None:
        if self.state_manager.cooking_manager.submit_step(step):
            if self.state_manager.cooking_manager.is_complete():
                result = self.state_manager.attempt_action("cook_meal")
                self.completed.add("cook_meal")
                self._play_sound("cook")
                self.mode = "game"
                self._clear_menu()
                self._build_hud()
                self._toast(result.message, seconds=4)
            else:
                self._show_cooking()
        else:
            self.state_manager.score_manager.record_mistake()
            if self.overlay_feedback is not None:
                self.overlay_feedback.setText("That cooking step is out of order. Follow the highlighted sequence.")

    def _toast(self, text: str, seconds: float = 3.0) -> None:
        if hasattr(self, "message_text"):
            self.message_text.setText(text)
            self.message_until = monotonic() + seconds

    def _load_audio(self) -> None:
        """Load optional music and sound effects without blocking gameplay."""
        theme_path = AUDIO_PATHS["theme"]
        if theme_path.exists():
            self.music = self.base.loader.loadMusic(str(theme_path))
            if self.music is not None:
                self.music.setLoop(True)
                self.music.setVolume(0.55)
        else:
            print(f"Optional theme music missing: {theme_path}")

        for name, path in AUDIO_PATHS.items():
            if name in {"theme", "legacy_theme"}:
                continue
            if not path.exists():
                continue
            sound = self.base.loader.loadSfx(str(path))
            if sound is not None:
                sound.setVolume(0.75)
                self.sounds[name] = sound

    def _play_music(self) -> None:
        """Start the authorized theme if it is available."""
        if self.music is not None and self.music.status() != self.music.PLAYING:
            self.music.play()

    def _play_sound(self, name: str) -> None:
        """Play an optional sound effect."""
        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()

    def _avatar_card(self, label: str, avatar_id: str, x: float, color):
        nodes = self._panel(x - 0.28, x + 0.28, -0.28, 0.2, (1, 1, 1, 0.94))
        self.menu_nodes.append(self._text(label, x, 0.05, 0.045, (0.04, 0.19, 0.13, 1)))
        preview = self._box(f"avatar-preview-{avatar_id}", (0, 0, 0), (0.08, 0.08, 0.08), color)
        preview.reparentTo(self.base.aspect2d)
        preview.setPos(x, 0, -0.08)
        preview.setScale(0.08)
        self.menu_nodes.append(preview)
        self.menu_nodes.append(self._button("Select", (x, 0, -0.35), lambda: self.show_crop_select(avatar_id), scale=0.055))
        return nodes

    def _crop_card(self, crop: str, status: str, x: float, z: float, command: Callable[[], None], color):
        panel = self._panel(x - 0.18, x + 0.18, z - 0.16, z + 0.18, (1, 1, 1, 0.92))
        self.menu_nodes.append(self._text(crop, x, z + 0.06, 0.043, (0.04, 0.19, 0.13, 1)))
        self.menu_nodes.append(self._button(status, (x, 0, z - 0.08), command, scale=0.045, color=color))
        return panel

    def _button(self, text: str, pos, command: Callable[[], None], scale: float = 0.065, color=(0.96, 0.77, 0.22, 1)):
        return self.DirectButton(
            text=text,
            pos=pos,
            scale=scale,
            command=command,
            frameColor=color,
            text_fg=(0.03, 0.16, 0.1, 1),
            relief=1,
            pad=(0.24, 0.12),
        )

    def _text(
        self,
        text: str,
        x: float,
        z: float,
        scale: float,
        color,
        align=None,
        width: int | None = None,
        shadow: bool = False,
        parent_list: list[object] | None = None,
    ):
        display = "\n".join(wrap(text, width)) if width else text
        return self.OnscreenText(
            text=display,
            pos=(x, z),
            scale=scale,
            align=align or self.TextNode.ACenter,
            fg=color,
            shadow=(0, 0, 0, 0.22) if shadow else None,
            mayChange=True,
        )

    def _panel(self, left: float, right: float, bottom: float, top: float, color):
        panel = self.DirectFrame(frameSize=(left, right, bottom, top), frameColor=color)
        panel.setTransparency(self.TransparencyAttrib.MAlpha)
        return panel

    def _plane(self, name: str, width: float, depth: float, pos, color):
        card = self.CardMaker(name)
        card.setFrame(-width / 2, width / 2, -depth / 2, depth / 2)
        node = self.base.render.attachNewNode(card.generate())
        node.setP(-90)
        node.setPos(*pos)
        node.setColor(*color)
        return node

    def _box(self, name: str, pos, scale, color):
        model = self.base.loader.loadModel("models/box")
        model.reparentTo(self.base.render)
        model.setName(name)
        model.setPos(*pos)
        model.setScale(*scale)
        model.setColor(*color)
        return model

    def _sign(self, text: str, x: float, y: float, z: float, scale: float = 0.42):
        node = self.TextNode(f"sign-{text}")
        node.setText(text)
        node.setAlign(self.TextNode.ACenter)
        path = self.base.render.attachNewNode(node)
        path.setPos(x, y, z)
        path.setScale(scale)
        path.setBillboardPointEye()
        path.setColor(0.04, 0.18, 0.12, 1)
        return path

    def _avatar_color(self):
        return (0.9, 0.38, 0.22, 1) if self.avatar_id == "sunrise" else (0.14, 0.52, 0.78, 1)

    def _clear_menu(self) -> None:
        for node in self._unique_nodes(self.menu_nodes):
            if hasattr(node, "destroy"):
                node.destroy()
            else:
                node.removeNode()
        self.menu_nodes.clear()
        self.overlay_feedback = None

    def _clear_hud(self) -> None:
        for node in self._unique_nodes(self.hud_nodes):
            if hasattr(node, "destroy"):
                node.destroy()
            else:
                node.removeNode()
        self.hud_nodes.clear()

    def _unique_nodes(self, nodes: list[object]) -> list[object]:
        seen: set[int] = set()
        unique = []
        for node in nodes:
            identity = id(node)
            if identity not in seen:
                seen.add(identity)
                unique.append(node)
        return unique

    def _clear_world(self) -> None:
        for node in self.world_nodes:
            node.removeNode()
        self.world_nodes.clear()
        self.station_nodes.clear()
        self.station_label_nodes.clear()
        self.player = None
        self.crop_node = None
