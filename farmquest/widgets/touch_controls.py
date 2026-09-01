"""On-screen touch controls for mobile testing."""

from __future__ import annotations

from typing import Callable

from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


class TouchControls(AnchorLayout):
    """Large touch buttons for movement and actions."""

    def __init__(
        self,
        on_left: Callable[[bool], None],
        on_right: Callable[[bool], None],
        on_jump: Callable[[], None],
        on_interact: Callable[[], None],
        on_pause: Callable[[], None],
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.anchor_x = "center"
        self.anchor_y = "bottom"
        container = BoxLayout(
            orientation="horizontal",
            spacing=dp(20),
            padding=(dp(24), dp(18), dp(24), dp(18)),
            size_hint=(1, None),
            height=dp(120),
        )

        move_box = BoxLayout(size_hint=(0.45, 1), spacing=dp(12))
        left_button = Button(text="Left", font_size="20sp")
        right_button = Button(text="Right", font_size="20sp")
        left_button.bind(on_press=lambda *_: on_left(True), on_release=lambda *_: on_left(False))
        right_button.bind(on_press=lambda *_: on_right(True), on_release=lambda *_: on_right(False))
        move_box.add_widget(left_button)
        move_box.add_widget(right_button)

        action_box = BoxLayout(size_hint=(0.55, 1), spacing=dp(12))
        jump_button = Button(text="Jump", font_size="20sp")
        interact_button = Button(text="Interact", font_size="20sp")
        pause_button = Button(text="Pause", font_size="20sp")
        jump_button.bind(on_release=lambda *_: on_jump())
        interact_button.bind(on_release=lambda *_: on_interact())
        pause_button.bind(on_release=lambda *_: on_pause())
        action_box.add_widget(jump_button)
        action_box.add_widget(interact_button)
        action_box.add_widget(pause_button)

        container.add_widget(move_box)
        container.add_widget(action_box)
        self.add_widget(container)
