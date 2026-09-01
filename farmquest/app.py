"""Kivy application bootstrap."""

from __future__ import annotations

import utils.session
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import FadeTransition, ScreenManager

from farmquest.config import REFERENCE_HEIGHT, REFERENCE_WIDTH
from farmquest.managers.audio_manager import AudioManager
from farmquest.managers.localization_manager import LocalizationManager
from farmquest.managers.settings_manager import SettingsManager
from farmquest.screens.avatar_selection_screen import AvatarSelectionScreen
from farmquest.screens.game_screen import GameScreen
from farmquest.screens.results_screen import ResultsScreen
from farmquest.screens.settings_screen import SettingsScreen
from farmquest.screens.title_screen import TitleScreen


class GameApp(App):
    """FarmQuest application controller."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.settings_manager = SettingsManager()
        self.localization = LocalizationManager(language="en")
        self.audio_manager = AudioManager(settings=self.settings_manager)
        self.screen_manager: ScreenManager | None = None
        self.game_screen: GameScreen | None = None
        self.results_screen: ResultsScreen | None = None

    def build(self) -> ScreenManager:
        """Construct screens and initialize app settings."""
        Window.size = (REFERENCE_WIDTH, REFERENCE_HEIGHT)
        Window.clearcolor = (0.09, 0.11, 0.14, 1.0)
        self.audio_manager.load()
        self.screen_manager = ScreenManager(transition=FadeTransition())
        self.screen_manager.add_widget(TitleScreen(name="title", app_controller=self))
        self.screen_manager.add_widget(AvatarSelectionScreen(name="avatar_selection", app_controller=self))
        self.game_screen = GameScreen(name="game", app_controller=self)
        self.results_screen = ResultsScreen(name="results", app_controller=self)
        self.screen_manager.add_widget(self.game_screen)
        self.screen_manager.add_widget(self.results_screen)
        self.screen_manager.add_widget(SettingsScreen(name="settings", app_controller=self))
        self.audio_manager.play_theme()
        return self.screen_manager

    def show_title(self) -> None:
        """Navigate to the title screen."""
        self.screen_manager.current = "title"

    def show_avatar_selection(self) -> None:
        """Navigate to avatar selection."""
        self.screen_manager.current = "avatar_selection"

    def show_settings(self) -> None:
        """Navigate to settings."""
        self.screen_manager.current = "settings"

    def start_new_game(self, avatar_id: str) -> None:
        """Reset and start gameplay with the selected avatar."""
        self.game_screen.start_session(avatar_id)
        self.screen_manager.current = "game"

    def show_results(self, results: dict[str, object]) -> None:
        """Display the final results screen."""
        self.results_screen.update_results(results)
        self.screen_manager.current = "results"

    def staff_reset(self) -> None:
        """Clear the active session and return to the title screen."""
        self.game_screen.reset_to_clean_title_state()
        self.show_title()
