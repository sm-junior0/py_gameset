"""Avatar selection screen."""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget


class AvatarSelectionScreen(Screen):
    """Lets the player choose between two placeholder avatars."""

    def __init__(self, app_controller, **kwargs) -> None:
        super().__init__(**kwargs)
        self.app_controller = app_controller
        root = BoxLayout(orientation="vertical", padding=36, spacing=20)
        root.add_widget(Label(text="Choose Your Explorer", font_size="34sp", bold=True))
        root.add_widget(Label(text="Two original placeholder appearances for the prototype.", font_size="20sp"))
        options = BoxLayout(spacing=20)
        options.add_widget(self._build_card("sunrise", "Sunrise Explorer", "Warm orange outfit"))
        options.add_widget(self._build_card("river", "River Explorer", "Cool blue outfit"))
        root.add_widget(options)
        self.add_widget(root)

    def _build_card(self, avatar_id: str, title: str, subtitle: str) -> BoxLayout:
        card = BoxLayout(orientation="vertical", padding=20, spacing=16)
        card.add_widget(Label(text=title, font_size="24sp", bold=True))
        card.add_widget(Label(text=subtitle, font_size="18sp"))
        card.add_widget(Widget())
        button = Button(text="Select", size_hint=(1, 0.25), font_size="22sp")
        button.bind(on_release=lambda *_: self.app_controller.start_new_game(avatar_id))
        card.add_widget(button)
        return card
