"""Main gameplay screen."""

from __future__ import annotations

from time import monotonic

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

from farmquest.entities.level import RectEntity
from farmquest.managers.game_state_manager import GameStateManager
from farmquest.widgets.game_world import GameWorld
from farmquest.widgets.touch_controls import TouchControls


class GameController:
    """Coordinates UI interactions with the pure game logic."""

    def __init__(self, state_manager: GameStateManager, game_screen: "GameScreen") -> None:
        self.state_manager = state_manager
        self.game_screen = game_screen
        self.watering_progress = 0
        self.soil_progress = 0

    def handle_interaction(self, zone: RectEntity) -> None:
        """Route interaction zones to quizzes or actions."""
        kind = zone.kind
        if kind.startswith("question_"):
            self.game_screen.show_question(kind)
            return
        if kind == "prepare_soil":
            self.soil_progress += 1
            if self.soil_progress < 3:
                self.game_screen.flash_message(f"Soil prep progress: {self.soil_progress}/3")
                return
        if kind == "water_crop":
            self.watering_progress += 1
            if self.watering_progress < 3:
                self.game_screen.flash_message(f"Water indicator filling: {self.watering_progress}/3")
                return

        if kind == "start_growth":
            result = self.state_manager.attempt_action("start_growth")
            self.game_screen.flash_message(result.message)
            if result.success:
                self.game_screen.world.crop_stage = self.state_manager.crop_manager.stage
                self.game_screen.show_growth_overlay()
                self.game_screen.on_successful_action(kind)
            return

        if kind == "mature_crop":
            result = self.state_manager.attempt_action("mature_crop")
            self.game_screen.flash_message(result.message)
            if result.success:
                self.game_screen.world.crop_stage = self.state_manager.crop_manager.stage
                self.game_screen.on_successful_action(kind)
                self.game_screen.refresh_hud()
            return

        if kind == "cook_meal":
            self.game_screen.show_cooking_popup()
            return

        result = self.state_manager.attempt_action(kind)
        self.game_screen.flash_message(result.message)
        if result.success:
            self.game_screen.on_successful_action(kind)


class GameScreen(Screen):
    """Playable side-scrolling game screen."""

    def __init__(self, app_controller, **kwargs) -> None:
        super().__init__(**kwargs)
        self.app_controller = app_controller
        self.state_manager = GameStateManager()
        self.game_controller = GameController(self.state_manager, self)
        self.last_progress_time = monotonic()
        self.active_hint_popup: Popup | None = None
        self.pause_popup: Popup | None = None
        self.paused = False

        self.root_layout = FloatLayout()
        self.world = GameWorld(
            on_zone_interaction=self.game_controller.handle_interaction,
            on_checkpoint=lambda zone: self.flash_message(f"Checkpoint reached: {zone.label}"),
            on_hazard=lambda: self.flash_message("You slipped into a hazard. Respawning at the latest checkpoint."),
            size_hint=(1, 1),
        )
        self.root_layout.add_widget(self.world)

        self.hud = BoxLayout(
            orientation="vertical",
            spacing=8,
            padding=(20, 18, 20, 18),
            size_hint=(1, None),
            height=140,
            pos_hint={"top": 1},
        )
        self.objective_label = Label(text="", font_size="22sp", halign="left", valign="middle")
        self.objective_label.bind(size=lambda *_: setattr(self.objective_label, "text_size", self.objective_label.size))
        self.message_label = Label(text="", font_size="20sp", halign="left", valign="middle")
        self.message_label.bind(size=lambda *_: setattr(self.message_label, "text_size", self.message_label.size))
        self.interaction_label = Label(text="", font_size="18sp")
        self.hud.add_widget(self.objective_label)
        self.hud.add_widget(self.message_label)
        self.hud.add_widget(self.interaction_label)
        self.root_layout.add_widget(self.hud)

        self.touch_controls = TouchControls(
            on_left=self._set_left,
            on_right=self._set_right,
            on_jump=self._jump,
            on_interact=self._interact,
            on_pause=self.toggle_pause,
            size_hint=(1, None),
            height=120,
        )
        self.root_layout.add_widget(self.touch_controls)
        self.add_widget(self.root_layout)

        Window.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
        Clock.schedule_interval(self._update_hud, 0.1)
        Clock.schedule_interval(self._check_stuck_hint, 1.0)

    def start_session(self, avatar_id: str) -> None:
        """Reset and begin a new game session."""
        self.state_manager.reset()
        self.state_manager.select_avatar(avatar_id)
        self.world.reset_session(avatar_id)
        self.game_controller.soil_progress = 0
        self.game_controller.watering_progress = 0
        self.state_manager.start_game()
        self.last_progress_time = monotonic()
        self.paused = False
        self.refresh_hud()
        self.flash_message("Tutorial: Move right, jump obstacles, and press E or Interact near markers.")

    def reset_to_clean_title_state(self) -> None:
        """Return the game screen to a neutral state for event staff reset."""
        self.state_manager.reset()
        self.world.reset_session("sunrise")
        self.game_controller.soil_progress = 0
        self.game_controller.watering_progress = 0
        self.last_progress_time = monotonic()
        self.paused = False
        self.pause_popup = None
        self.refresh_hud()
        self.flash_message("")

    def refresh_hud(self) -> None:
        """Update objective UI text."""
        self.objective_label.text = f"Objective: {self.state_manager.current_objective()}"
        prompt = self.world.nearby_label
        self.interaction_label.text = f"Nearby: {prompt}" if prompt else "Nearby: Keep exploring to the right."

    def _update_hud(self, _dt: float) -> None:
        self.refresh_hud()

    def flash_message(self, message: str) -> None:
        """Show a short on-screen message."""
        self.message_label.text = message

    def _check_stuck_hint(self, _dt: float) -> None:
        if self.manager.current != self.name or self.paused:
            return
        elapsed = monotonic() - self.last_progress_time
        if elapsed >= 30 and self.active_hint_popup is None:
            self.show_hint_popup()

    def show_hint_popup(self) -> None:
        """Display a contextual hint when the player is stalled."""
        direction = "right" if self._next_target_x() >= self.world.player.x else "left"
        text = f"{self.state_manager.current_hint()}\n\nTry moving {direction} toward the highlighted objective."
        self.active_hint_popup = Popup(
            title="Hint",
            content=Label(text=text, font_size="20sp"),
            size_hint=(0.7, 0.4),
        )
        self.active_hint_popup.bind(on_dismiss=lambda *_: setattr(self, "active_hint_popup", None))
        self.active_hint_popup.open()

    def _next_target_x(self) -> float:
        state = self.state_manager.state.value
        state_to_zone = {
            "EXPLORING": 520,
            "SEED_FOUND": 1880,
            "SOIL_PREPARED": 2460,
            "SEED_PLANTED": 2860,
            "CROP_WATERED": 3360,
            "CROP_PROTECTED": 3620,
            "CROP_GROWING": 3880,
            "CROP_MATURE": 4140,
            "CROP_HARVESTED": 4480,
            "MAIZE_PROCESSED": 4900,
            "MEAL_COOKED": 5300,
        }
        return float(state_to_zone.get(state, 520))

    def on_successful_action(self, kind: str) -> None:
        """Handle state-dependent UI after a successful world action."""
        self.last_progress_time = monotonic()
        self.world.mark_zone_completed(kind)
        self.world.crop_stage = self.state_manager.crop_manager.stage
        effect_map = {
            "collect_seed": "seed",
            "prepare_soil": "soil",
            "plant_seed": "plant",
            "water_crop": "water",
            "protect_crop": "growth",
            "start_growth": "growth",
            "mature_crop": "growth",
            "harvest_crop": "harvest",
            "process_maize": "mill",
            "serve_meal": "complete",
        }
        effect = effect_map.get(kind)
        if effect:
            self.app_controller.audio_manager.play_effect(effect)
        if kind == "serve_meal":
            self.app_controller.show_results(self.state_manager.results())
        self.refresh_hud()

    def show_question(self, question_id: str) -> None:
        """Open a multiple-choice quiz popup."""
        question = self.state_manager.quiz_manager.get_question(question_id)
        layout = BoxLayout(orientation="vertical", spacing=12, padding=16)
        layout.add_widget(Label(text=question["prompt"], font_size="22sp"))
        popup = Popup(title="Agriculture Checkpoint", content=layout, size_hint=(0.8, 0.7))

        def submit(index: int) -> None:
            result = self.state_manager.submit_question(question_id, index)
            text = "Correct. " if result["correct"] else "Not quite. "
            self.flash_message(text + str(result["feedback"]))
            if result["correct"]:
                self.last_progress_time = monotonic()
                self.world.mark_zone_completed(question_id)
                popup.dismiss()
                self.refresh_hud()

        for index, choice in enumerate(question["choices"]):
            button = Button(text=str(choice), size_hint=(1, None), height=60, font_size="20sp")
            button.bind(on_release=lambda _btn, idx=index: submit(idx))
            layout.add_widget(button)
        popup.open()

    def show_growth_overlay(self) -> None:
        """Display an accelerated-growth notice."""
        popup = Popup(
            title="Time Passing",
            content=Label(
                text="The crop is growing faster than real maize growth for gameplay clarity.",
                font_size="20sp",
            ),
            size_hint=(0.75, 0.35),
        )
        popup.open()
        Clock.schedule_once(lambda *_: popup.dismiss(), 2.0)

    def show_cooking_popup(self) -> None:
        """Run the cooking mini-game."""
        layout = BoxLayout(orientation="vertical", spacing=12, padding=16)
        info = Label(
            text=f"Select the steps in order.\nNext step: {self.state_manager.cooking_manager.current_step}",
            font_size="20sp",
        )
        layout.add_widget(info)
        popup = Popup(title="Cooking Mini-Game", content=layout, size_hint=(0.75, 0.65))

        def choose(step: str) -> None:
            success = self.state_manager.cooking_manager.submit_step(step)
            if success:
                if self.state_manager.cooking_manager.is_complete():
                    popup.dismiss()
                    result = self.state_manager.attempt_action("cook_meal")
                    self.flash_message(result.message)
                    if result.success:
                        self.last_progress_time = monotonic()
                        self.world.mark_zone_completed("cook_meal")
                        self.app_controller.audio_manager.play_effect("cook")
                        self.refresh_hud()
                else:
                    info.text = f"Great. Next step: {self.state_manager.cooking_manager.current_step}"
            else:
                self.state_manager.score_manager.record_mistake()
                self.flash_message("That step is out of order. Follow the cooking sequence.")

        for step in ["heat pot", "add flour", "stir"]:
            button = Button(text=step.title(), size_hint=(1, None), height=60, font_size="20sp")
            button.bind(on_release=lambda _btn, selected=step: choose(selected))
            layout.add_widget(button)
        popup.open()

    def _set_left(self, active: bool) -> None:
        self.world.input_state.left = active

    def _set_right(self, active: bool) -> None:
        self.world.input_state.right = active

    def _jump(self) -> None:
        self.world.trigger_jump()
        self.app_controller.audio_manager.play_effect("jump")

    def _interact(self) -> None:
        self.world.interact()

    def toggle_pause(self, *_args) -> None:
        """Pause or resume the gameplay loop."""
        if self.paused:
            self.resume_game()
        else:
            self.pause_game()

    def pause_game(self) -> None:
        """Show the pause overlay and stop world updates."""
        self.paused = True
        self.world.stop_updates()
        layout = BoxLayout(orientation="vertical", padding=20, spacing=14)
        layout.add_widget(Label(text="Paused", font_size="30sp", bold=True))
        resume_button = Button(text="Resume", size_hint=(1, None), height=58, font_size="22sp")
        settings_button = Button(text="Settings", size_hint=(1, None), height=58, font_size="22sp")
        title_button = Button(text="Return to Title", size_hint=(1, None), height=58, font_size="22sp")
        resume_button.bind(on_release=lambda *_: self.resume_game())
        settings_button.bind(on_release=lambda *_: self._leave_pause_for("settings"))
        title_button.bind(on_release=lambda *_: self._leave_pause_for("title"))
        layout.add_widget(resume_button)
        layout.add_widget(settings_button)
        layout.add_widget(title_button)
        self.pause_popup = Popup(title="Pause", content=layout, size_hint=(0.55, 0.62), auto_dismiss=False)
        self.pause_popup.open()

    def _leave_pause_for(self, screen_name: str) -> None:
        """Dismiss pause UI before navigating away."""
        if self.pause_popup is not None:
            self.pause_popup.dismiss()
            self.pause_popup = None
        if screen_name == "settings":
            self.app_controller.show_settings()
        else:
            self.app_controller.show_title()

    def resume_game(self) -> None:
        """Resume gameplay from the pause overlay."""
        self.paused = False
        if self.pause_popup is not None:
            self.pause_popup.dismiss()
            self.pause_popup = None
        self.world.start_updates()
        self.flash_message("Resumed.")

    def _on_key_down(self, _window, keycode, *_args) -> bool:
        if self.manager.current != self.name:
            return False
        if keycode in (276, 97):
            self._set_left(True)
        elif keycode in (275, 100):
            self._set_right(True)
        elif keycode in (273, 32):
            self._jump()
        elif keycode == 101:
            self._interact()
        elif keycode == 27:
            self.toggle_pause()
        return False

    def _on_key_up(self, _window, keycode, *_args) -> bool:
        if keycode in (276, 97):
            self._set_left(False)
        elif keycode in (275, 100):
            self._set_right(False)
        return False
