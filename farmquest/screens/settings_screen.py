"""Settings screen."""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.slider import Slider


class SettingsScreen(Screen):
    """Adjusts simple audio settings."""

    def __init__(self, app_controller, **kwargs) -> None:
        super().__init__(**kwargs)
        settings = app_controller.settings_manager
        layout = BoxLayout(orientation="vertical", padding=36, spacing=18)
        layout.add_widget(Label(text="Settings", font_size="34sp", bold=True))

        layout.add_widget(Label(text="Music Volume", font_size="20sp"))
        music_slider = Slider(min=0, max=1, value=settings.music_volume)
        music_slider.bind(value=lambda *_args: setattr(settings, "music_volume", music_slider.value))
        layout.add_widget(music_slider)

        layout.add_widget(Label(text="Effects Volume", font_size="20sp"))
        effects_slider = Slider(min=0, max=1, value=settings.effects_volume)
        effects_slider.bind(value=lambda *_args: setattr(settings, "effects_volume", effects_slider.value))
        layout.add_widget(effects_slider)

        mute_button = Button(text="Toggle Mute", size_hint=(1, 0.18), font_size="22sp")
        mute_button.bind(on_release=lambda *_: settings.toggle_mute())
        layout.add_widget(mute_button)

        back_button = Button(text="Back", size_hint=(1, 0.18), font_size="22sp")
        back_button.bind(on_release=lambda *_: app_controller.show_title())
        layout.add_widget(back_button)
        self.add_widget(layout)
