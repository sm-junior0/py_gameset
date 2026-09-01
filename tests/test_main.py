import main


class FakeApp:
    def __init__(self) -> None:
        self.ran = False

    def run(self) -> None:
        self.ran = True


def test_main_can_launch_injected_app_without_importing_kivy() -> None:
    fake_app = FakeApp()
    assert main.main(app_factory=lambda: fake_app) == 0
    assert fake_app.ran is True
