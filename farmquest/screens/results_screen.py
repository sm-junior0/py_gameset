"""Results screen."""

from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen


class ResultsScreen(Screen):
    """Displays the final score and summary."""

    def __init__(self, app_controller, **kwargs) -> None:
        super().__init__(**kwargs)
        self.app_controller = app_controller
        self.summary_label = Label(text="", font_size="20sp", halign="left", valign="top")
        self.summary_label.bind(size=lambda *_: setattr(self.summary_label, "text_size", self.summary_label.size))
        layout = BoxLayout(orientation="vertical", padding=32, spacing=16)
        layout.add_widget(Label(text="Journey Complete", font_size="36sp", bold=True))
        layout.add_widget(self.summary_label)
        restart_button = Button(text="Restart", size_hint=(1, 0.16), font_size="22sp")
        title_button = Button(text="Return to Title", size_hint=(1, 0.16), font_size="22sp")
        reset_button = Button(text="Staff Reset", size_hint=(1, 0.16), font_size="22sp")
        restart_button.bind(on_release=lambda *_: app_controller.show_avatar_selection())
        title_button.bind(on_release=lambda *_: app_controller.show_title())
        reset_button.bind(on_release=lambda *_: app_controller.staff_reset())
        layout.add_widget(restart_button)
        layout.add_widget(title_button)
        layout.add_widget(reset_button)
        self.add_widget(layout)

    def update_results(self, results: dict[str, object]) -> None:
        """Refresh the displayed results."""
        time_seconds = int(float(results["completion_time"]))
        minutes, seconds = divmod(time_seconds, 60)
        self.summary_label.text = (
            f"Final Score: {results['total_score']}/100\n"
            f"Knowledge Score: {results['knowledge_score']}\n"
            f"Accuracy Score: {results['accuracy_score']}\n"
            f"Completion Score: {results['completion_score']}\n"
            f"Completion Time: {minutes:02d}:{seconds:02d}\n"
            f"Educational Summary: {results['process_summary']}\n"
            f"Virtual Reward: {results['reward']}"
        )
