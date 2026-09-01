"""Standard-library desktop edition for Python versions without Kivy wheels."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from time import monotonic

from farmquest.config import GROUND_Y, WORLD_WIDTH
from farmquest.data.level_data import build_level
from farmquest.entities.level import RectEntity
from farmquest.entities.player import Player
from farmquest.managers.game_state_manager import GameStateManager
from farmquest.systems.camera import CameraSystem
from farmquest.systems.collision import resolve_world_collisions
from farmquest.systems.interaction import find_interaction


class TkFarmQuestApp:
    """Tkinter implementation that runs with the user's existing Python."""

    width = 1280
    height = 720

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("FarmQuest - Python Desktop Edition")
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.minsize(960, 540)
        self.state_manager = GameStateManager()
        self.avatar_id = "sunrise"
        self.selected_crop = "Maize"
        self.level = build_level()
        self.player = Player(
            x=float(self.level["spawn_x"]),
            y=float(self.level["spawn_y"]),
            width=48,
            height=72,
            avatar_id=self.avatar_id,
        )
        self.spawn_x = self.player.x
        self.spawn_y = self.player.y
        self.camera = CameraSystem(world_width=WORLD_WIDTH, view_width=self.width)
        self.completed_zones: set[str] = set()
        self._repeat_counts: dict[str, int] = {}
        self.keys: set[str] = set()
        self.last_frame = monotonic()
        self.last_progress = monotonic()
        self.current_zone: RectEntity | None = None
        self.running = False
        self.screen = tk.Frame(self.root, bg="#eef7df")
        self.screen.pack(fill="both", expand=True)

    def run(self) -> None:
        """Start the desktop edition."""
        self.show_title()
        self.root.mainloop()

    def clear_screen(self) -> None:
        """Remove current screen widgets."""
        for child in self.screen.winfo_children():
            child.destroy()

    def show_title(self) -> None:
        """Show the title screen."""
        self.running = False
        self.clear_screen()
        tk.Label(
            self.screen,
            text="FarmQuest: From Seed to Plate",
            font=("Segoe UI", 44, "bold"),
            bg="#eef7df",
            fg="#143527",
        ).pack(pady=(90, 12))
        tk.Label(
            self.screen,
            text="Find the seed, grow the crop, mill it, cook it, and serve the meal.",
            font=("Segoe UI", 20),
            bg="#eef7df",
            fg="#2d4636",
        ).pack(pady=8)
        tk.Button(
            self.screen,
            text="Start Adventure",
            font=("Segoe UI", 18, "bold"),
            command=self.show_avatar_selection,
            width=22,
            height=2,
        ).pack(pady=24)
        tk.Button(
            self.screen,
            text="Staff Reset",
            font=("Segoe UI", 14),
            command=self.staff_reset,
            width=18,
        ).pack()

    def show_avatar_selection(self) -> None:
        """Show avatar choices."""
        self.clear_screen()
        tk.Label(
            self.screen,
            text="Choose Your Explorer",
            font=("Segoe UI", 34, "bold"),
            bg="#eef7df",
            fg="#183024",
        ).pack(pady=(70, 24))
        choices = tk.Frame(self.screen, bg="#eef7df")
        choices.pack()
        self._avatar_button(choices, "Sunrise Explorer", "sunrise", "#e67349").pack(side="left", padx=40)
        self._avatar_button(choices, "River Explorer", "river", "#389dce").pack(side="left", padx=40)

    def _avatar_button(self, parent: tk.Widget, label: str, avatar_id: str, color: str) -> tk.Frame:
        frame = tk.Frame(parent, bg="white", highlightbackground="#2d4636", highlightthickness=2, padx=34, pady=24)
        tk.Canvas(frame, width=100, height=130, bg="white", highlightthickness=0).pack()
        preview = frame.winfo_children()[0]
        preview.create_rectangle(28, 36, 72, 116, fill=color, outline="#111")
        preview.create_oval(26, 8, 74, 52, fill="#8f5d3f", outline="#111")
        tk.Button(
            frame,
            text=label,
            font=("Segoe UI", 16, "bold"),
            command=lambda: self.show_crop_selection(avatar_id),
            width=18,
        ).pack(pady=(16, 0))
        return frame

    def show_crop_selection(self, avatar_id: str) -> None:
        """Let players choose maize and preview future crops."""
        self.avatar_id = avatar_id
        self.clear_screen()
        tk.Label(
            self.screen,
            text="Choose What to Grow",
            font=("Segoe UI", 34, "bold"),
            bg="#eef7df",
            fg="#143527",
        ).pack(pady=(58, 12))
        tk.Label(
            self.screen,
            text="Maize is ready for today's farm-to-table challenge.",
            font=("Segoe UI", 17),
            bg="#eef7df",
            fg="#2d4636",
        ).pack(pady=(0, 24))
        grid = tk.Frame(self.screen, bg="#eef7df")
        grid.pack()
        self._crop_card(grid, "Maize", "Ready", "#e8c547", lambda: self.start_game(avatar_id)).grid(row=0, column=0, padx=14, pady=14)
        for index, crop in enumerate(["Beans", "Potatoes", "Bananas", "Coffee"], start=1):
            self._crop_card(grid, crop, "Coming Soon", "#bfc8bd", lambda: None).grid(row=index // 3, column=index % 3, padx=14, pady=14)

    def _crop_card(self, parent: tk.Widget, crop: str, status: str, color: str, command) -> tk.Frame:
        card = tk.Frame(parent, bg="white", highlightthickness=2, highlightbackground="#315241", padx=18, pady=16)
        canvas = tk.Canvas(card, width=180, height=116, bg="white", highlightthickness=0)
        canvas.pack()
        canvas.create_oval(58, 28, 122, 92, fill=color, outline="#315241", width=2)
        canvas.create_text(90, 60, text=crop[0], font=("Segoe UI", 28, "bold"), fill="#143527")
        tk.Label(card, text=crop, font=("Segoe UI", 17, "bold"), bg="white", fg="#143527").pack()
        tk.Button(card, text=status, font=("Segoe UI", 12, "bold"), command=command, width=15).pack(pady=(10, 0))
        return card

    def start_game(self, avatar_id: str) -> None:
        """Reset and start the game."""
        self.clear_screen()
        self.avatar_id = avatar_id
        self.selected_crop = "Maize"
        self.state_manager.reset()
        self.state_manager.select_avatar(avatar_id)
        self.state_manager.start_game()
        self.completed_zones.clear()
        self._repeat_counts.clear()
        self.spawn_x = float(self.level["spawn_x"])
        self.spawn_y = float(self.level["spawn_y"])
        self.player.respawn(self.spawn_x, self.spawn_y)
        self.player.avatar_id = avatar_id
        self.keys.clear()
        self.running = True
        self.last_frame = monotonic()
        self.last_progress = monotonic()

        self.canvas = tk.Canvas(self.screen, bg="#9fddf0", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.hud = tk.Label(
            self.screen,
            text="",
            font=("Segoe UI", 13, "bold"),
            bg="#143527",
            fg="white",
            anchor="w",
            padx=12,
            pady=8,
        )
        self.hud.place(x=0, y=0, relwidth=1)
        self.stage_badge = tk.Label(
            self.screen,
            text="Score: 30",
            font=("Segoe UI", 13, "bold"),
            bg="#f7d34d",
            fg="#143527",
            padx=14,
            pady=7,
        )
        self.stage_badge.place(relx=1.0, x=-12, y=52, anchor="ne")
        controls = tk.Frame(self.screen, bg="#143527")
        controls.place(relx=0.5, rely=1.0, anchor="s")
        for text, action in [
            ("Left", lambda: self._tap_move(-1)),
            ("Right", lambda: self._tap_move(1)),
            ("Jump", self.jump),
            ("Interact", self.interact),
            ("Pause", self.pause),
        ]:
            tk.Button(controls, text=text, font=("Segoe UI", 13, "bold"), command=action, width=10).pack(side="left", padx=5, pady=8)

        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.root.focus_set()
        self.message("Tutorial: A/D or arrows move, W/Space jumps, Shift runs, E interacts.")
        self.game_loop()

    def game_loop(self) -> None:
        """Update physics and drawing."""
        if not self.running:
            return
        now = monotonic()
        dt = min(0.033, now - self.last_frame)
        self.last_frame = now
        self.update_player(dt)
        self.draw()
        self.root.after(16, self.game_loop)

    def update_player(self, dt: float) -> None:
        """Move the player, resolve collisions, and find interactions."""
        previous_x = self.player.x
        previous_y = self.player.y
        left = "a" in self.keys or "Left" in self.keys
        right = "d" in self.keys or "Right" in self.keys
        speed = 460 if "Shift_L" in self.keys or "Shift_R" in self.keys else 320
        self.player.velocity_x = (-speed if left else 0) + (speed if right else 0)
        self.player.velocity_y -= 2200 * dt
        self.player.x = max(0, min(WORLD_WIDTH - self.player.width, self.player.x + self.player.velocity_x * dt))
        self.player.y += self.player.velocity_y * dt
        resolve_world_collisions(self.player, self.level["solids"], previous_x, previous_y)
        if self.player.y < -260 or any(self.player.intersects(hazard) for hazard in self.level["hazards"]):
            self.message("You slipped. Back to the latest checkpoint.")
            self.player.respawn(self.spawn_x, self.spawn_y)
        for checkpoint in self.level["checkpoints"]:
            if self.player.intersects(checkpoint):
                self.spawn_x = checkpoint.x
                self.spawn_y = checkpoint.y
        active_zones = [zone for zone in self.level["interactions"] if zone.kind not in self.completed_zones]
        self.current_zone = find_interaction(self.player, active_zones)
        self.camera.view_width = max(1, self.canvas.winfo_width())
        self.camera.update(self.player.x + self.player.width / 2)
        if monotonic() - self.last_progress > 30:
            self.message(self.state_manager.current_hint())
            self.last_progress = monotonic()

    def draw(self) -> None:
        """Redraw the level."""
        self.canvas.delete("all")
        view_h = max(1, self.canvas.winfo_height())
        offset = self.camera.offset_x
        width = self.canvas.winfo_width()
        self.canvas.create_rectangle(0, 0, width, view_h, fill="#9fddf0", outline="")
        self.canvas.create_rectangle(0, view_h * 0.55, width, view_h, fill="#d6ef9b", outline="")
        self.canvas.create_oval(width - 170, 62, width - 60, 172, fill="#f8d963", outline="")
        self.canvas.create_rectangle(-offset * 0.18, view_h - 280, width + 300, view_h - 90, fill="#78b957", outline="")
        self.canvas.create_rectangle(-offset * 0.35, view_h - 200, width + 420, view_h - 70, fill="#59943f", outline="")
        self.draw_decorations()
        for solid in self.level["solids"]:
            self._rect(solid, "#6f4b28" if solid.kind == "ground" else "#8a633a")
        for hazard in self.level["hazards"]:
            self._rect(hazard, "#4f2f1b")
        for zone in self.level["interactions"]:
            if zone.kind in self.completed_zones:
                continue
            color = "#1f66d1" if zone == self.current_zone else "#ffffff"
            self._rect(zone, color, outline="#102018", stipple="gray25")
            x, y = self.world_to_screen(zone.x, zone.y + zone.height + 8)
            self.canvas.create_text(x, y, text=zone.label, fill="#102018", anchor="sw", font=("Segoe UI", 10, "bold"))
        self.draw_crop()
        self.draw_player()
        nearby = f" | Nearby: {self.current_zone.label}" if self.current_zone else ""
        self.hud.config(text=f"Crop: {self.selected_crop} | Objective: {self.state_manager.current_objective()}{nearby}")
        self.stage_badge.config(text=f"Score: {self.state_manager.score_manager.total_score}/100")

    def draw_decorations(self) -> None:
        """Draw signs, houses, trees, and farm details for a richer prototype world."""
        for x in range(260, int(WORLD_WIDTH), 520):
            sx, sy = self.world_to_screen(x, GROUND_Y)
            self.canvas.create_rectangle(sx + 26, sy - 76, sx + 36, sy, fill="#7b5128", outline="")
            self.canvas.create_oval(sx, sy - 122, sx + 62, sy - 56, fill="#2f8f4b", outline="#1d6131")
        for x, label in [
            (120, "Welcome"),
            (1850, "Farm Plot"),
            (2860, "Water"),
            (4480, "Mill"),
            (4900, "Kitchen"),
            (5300, "Table"),
        ]:
            sx, sy = self.world_to_screen(x, GROUND_Y + 8)
            self.canvas.create_rectangle(sx, sy - 72, sx + 120, sy - 22, fill="#fff4bf", outline="#315241", width=2)
            self.canvas.create_text(sx + 60, sy - 47, text=label, fill="#143527", font=("Segoe UI", 10, "bold"))
            self.canvas.create_rectangle(sx + 55, sy - 22, sx + 65, sy + 25, fill="#7b5128", outline="")
        mill_x, mill_y = self.world_to_screen(4440, GROUND_Y + 10)
        self.canvas.create_rectangle(mill_x, mill_y - 130, mill_x + 170, mill_y, fill="#caa66a", outline="#51361f", width=2)
        self.canvas.create_polygon(mill_x - 12, mill_y - 130, mill_x + 85, mill_y - 190, mill_x + 182, mill_y - 130, fill="#8d4b33", outline="#51361f")
        kitchen_x, kitchen_y = self.world_to_screen(4860, GROUND_Y + 10)
        self.canvas.create_rectangle(kitchen_x, kitchen_y - 120, kitchen_x + 170, kitchen_y, fill="#f0f2e8", outline="#315241", width=2)
        self.canvas.create_polygon(kitchen_x - 12, kitchen_y - 120, kitchen_x + 85, kitchen_y - 176, kitchen_x + 182, kitchen_y - 120, fill="#4f8ea8", outline="#315241")

    def draw_crop(self) -> None:
        """Draw crop state at the field."""
        x, y = self.world_to_screen(2485, GROUND_Y + 20)
        stage = self.state_manager.crop_manager.stage
        if stage == "seed":
            self.canvas.create_oval(x, y, x + 14, y + 14, fill="#7d4c1c", outline="")
        elif stage == "growing":
            self.canvas.create_rectangle(x + 8, y - 48, x + 18, y, fill="#24913a", outline="")
            self.canvas.create_rectangle(x + 22, y - 36, x + 32, y, fill="#24913a", outline="")
        else:
            self.canvas.create_rectangle(x + 8, y - 66, x + 18, y, fill="#24813a", outline="")
            self.canvas.create_oval(x + 16, y - 58, x + 42, y - 22, fill="#e3c62d", outline="#7d6810")

    def draw_player(self) -> None:
        """Draw the selected avatar."""
        x, y = self.world_to_screen(self.player.x, self.player.y)
        color = "#e67349" if self.avatar_id == "sunrise" else "#389dce"
        self.canvas.create_rectangle(x, y - self.player.height, x + self.player.width, y, fill=color, outline="#111")
        self.canvas.create_oval(x + 6, y - self.player.height - 28, x + 42, y - self.player.height + 8, fill="#8f5d3f", outline="#111")

    def world_to_screen(self, x: float, y: float) -> tuple[float, float]:
        """Convert world bottom-left coordinates to Tk canvas coordinates."""
        return x - self.camera.offset_x, self.canvas.winfo_height() - y

    def _rect(self, rect: RectEntity, fill: str, outline: str = "", stipple: str = "") -> None:
        x1, y1 = self.world_to_screen(rect.x, rect.y + rect.height)
        x2, y2 = self.world_to_screen(rect.x + rect.width, rect.y)
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, stipple=stipple)

    def on_key_press(self, event: tk.Event) -> None:
        """Keyboard down handler."""
        key = event.keysym.lower() if len(event.keysym) == 1 else event.keysym
        self.keys.add(key)
        if key in {"space", "Up", "w"}:
            self.jump()
        elif key == "e":
            self.interact()
        elif key == "Escape":
            self.pause()

    def on_key_release(self, event: tk.Event) -> None:
        """Keyboard up handler."""
        key = event.keysym.lower() if len(event.keysym) == 1 else event.keysym
        self.keys.discard(key)

    def _tap_move(self, direction: int) -> None:
        self.player.x = max(0, min(WORLD_WIDTH - self.player.width, self.player.x + direction * 80))

    def jump(self) -> None:
        """Jump if grounded."""
        if self.player.on_ground:
            self.player.velocity_y = 860
            self.player.on_ground = False

    def interact(self) -> None:
        """Use the nearby station."""
        if self.current_zone is None:
            self.message("Move near a highlighted station first.")
            return
        kind = self.current_zone.kind
        if kind.startswith("question_"):
            self.show_question(kind)
            return
        if kind == "prepare_soil":
            self.repeat_action(kind, 3, "Press Interact to prepare soil", "Soil is prepared.")
            return
        if kind == "water_crop":
            self.repeat_action(kind, 3, "Hold steady. Water indicator filling", "Crop has enough water.")
            return
        if kind == "cook_meal":
            self.show_cooking()
            return
        result = self.state_manager.attempt_action(kind)
        self.message(result.message)
        if result.success:
            self.completed_zones.add(kind)
            self.last_progress = monotonic()
            self.stage_points(kind)
            if kind == "start_growth":
                messagebox.showinfo("Time Passing", "Growth is accelerated for this game. Real maize requires much more time and continued care.")
            if kind == "serve_meal":
                self.show_results()

    def repeat_action(self, kind: str, target: int, progress_text: str, done_text: str) -> None:
        """Complete a repeated interaction station."""
        count = self._repeat_counts.get(kind, 0) + 1
        self._repeat_counts[kind] = count
        if count < target:
            self.message(f"{progress_text}: {count}/{target}")
            return
        result = self.state_manager.attempt_action(kind)
        self.message(done_text if result.success else result.message)
        if result.success:
            self.completed_zones.add(kind)
            self.last_progress = monotonic()
            self.stage_points(kind)

    def show_question(self, question_id: str) -> None:
        """Ask a multiple-choice question."""
        question = self.state_manager.quiz_manager.get_question(question_id)
        dialog = tk.Toplevel(self.root)
        dialog.title("Agriculture Checkpoint")
        dialog.geometry("620x360")
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(dialog, text=question["prompt"], font=("Segoe UI", 17, "bold"), wraplength=560).pack(pady=24)

        def submit(index: int) -> None:
            result = self.state_manager.submit_question(question_id, index)
            prefix = "Correct. " if result["correct"] else "Not quite. "
            messagebox.showinfo("Feedback", prefix + str(result["feedback"]), parent=dialog)
            if result["correct"]:
                self.completed_zones.add(question_id)
                self.last_progress = monotonic()
                self.stage_points(question_id)
                dialog.destroy()

        for index, choice in enumerate(question["choices"]):
            tk.Button(dialog, text=str(choice), font=("Segoe UI", 13), command=lambda i=index: submit(i), width=48).pack(pady=6)

    def show_cooking(self) -> None:
        """Show cooking step choices."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Cooking")
        dialog.geometry("540x330")
        dialog.transient(self.root)
        dialog.grab_set()
        status = tk.Label(dialog, text="", font=("Segoe UI", 15, "bold"))
        status.pack(pady=18)

        def refresh() -> None:
            status.config(text=f"Next step: {self.state_manager.cooking_manager.current_step.title()}")

        def choose(step: str) -> None:
            if self.state_manager.cooking_manager.submit_step(step):
                if self.state_manager.cooking_manager.is_complete():
                    result = self.state_manager.attempt_action("cook_meal")
                    self.message(result.message)
                    self.completed_zones.add("cook_meal")
                    self.last_progress = monotonic()
                    self.stage_points("cook_meal")
                    dialog.destroy()
                else:
                    refresh()
            else:
                self.state_manager.score_manager.record_mistake()
                self.message("That cooking step is out of order.")

        refresh()
        for step in ["heat pot", "add flour", "stir"]:
            tk.Button(dialog, text=step.title(), font=("Segoe UI", 13), command=lambda s=step: choose(s), width=24).pack(pady=8)

    def pause(self) -> None:
        """Pause with a simple modal."""
        if not self.running:
            return
        self.running = False
        if messagebox.askyesno("Paused", "Resume the game?"):
            self.running = True
            self.last_frame = monotonic()
            self.game_loop()
        else:
            self.show_title()

    def message(self, text: str) -> None:
        """Display a short status line."""
        if hasattr(self, "hud"):
            self.hud.config(text=text)

    def stage_points(self, _kind: str) -> None:
        """Show a short celebratory point moment."""
        if not hasattr(self, "canvas"):
            return
        total = self.state_manager.score_manager.total_score
        pop = self.canvas.create_text(
            self.canvas.winfo_width() / 2,
            104,
            text=f"Stage complete! Score {total}/100",
            fill="#143527",
            font=("Segoe UI", 24, "bold"),
        )
        box = self.canvas.create_rectangle(
            self.canvas.winfo_width() / 2 - 230,
            72,
            self.canvas.winfo_width() / 2 + 230,
            136,
            fill="#f7d34d",
            outline="#143527",
            width=2,
        )
        self.canvas.tag_raise(pop, box)
        self.root.after(1100, lambda: self.canvas.delete(pop, box))

    def show_results(self) -> None:
        """Display final results."""
        self.running = False
        results = self.state_manager.results()
        seconds = int(float(results["completion_time"]))
        minutes, seconds = divmod(seconds, 60)
        self.clear_screen()
        text = (
            f"Final Score: {results['total_score']}/100\n"
            f"Knowledge: {results['knowledge_score']}  Accuracy: {results['accuracy_score']}  Completion: {results['completion_score']}\n"
            f"Completion Time: {minutes:02d}:{seconds:02d}\n\n"
            f"{results['process_summary']}\n\n"
            f"Virtual Reward: {results['reward']}"
        )
        tk.Label(self.screen, text="Journey Complete", font=("Segoe UI", 34, "bold"), bg="#eef7df", fg="#183024").pack(pady=(70, 20))
        tk.Label(self.screen, text=text, font=("Segoe UI", 17), bg="#eef7df", fg="#183024", justify="center").pack(pady=16)
        tk.Button(self.screen, text="Restart", font=("Segoe UI", 16, "bold"), command=self.show_avatar_selection, width=18).pack(pady=8)
        tk.Button(self.screen, text="Return to Title", font=("Segoe UI", 14), command=self.show_title, width=18).pack(pady=8)

    def staff_reset(self) -> None:
        """Clear all runtime state."""
        self.state_manager.reset()
        self.completed_zones.clear()
        self._repeat_counts.clear()
        self.show_title()
