"""Title screen."""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen


class TitleScreen(Screen):
    """Initial title screen."""

    def __init__(self, app_controller, **kwargs) -> None:
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=48, spacing=24)
        layout.add_widget(Label(text="FarmQuest", font_size="42sp", bold=True))
        layout.add_widget(
            Label(
                text="A short maize farm-to-table learning adventure",
                font_size="22sp",
            )
        )
        start_button = Button(text="Start Adventure", size_hint=(1, 0.18), font_size="24sp")
        settings_button = Button(text="Settings", size_hint=(1, 0.16), font_size="20sp")
        start_button.bind(on_release=lambda *_: app_controller.show_avatar_selection())
        settings_button.bind(on_release=lambda *_: app_controller.show_settings())
        layout.add_widget(start_button)
        layout.add_widget(settings_button)
        self.add_widget(layout)
