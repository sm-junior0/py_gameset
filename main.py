"""Desktop entry point for FarmQuest."""

from __future__ import annotations

import sys
from collections.abc import Callable


def main(app_factory: Callable[[], object] | None = None) -> int:
    """Launch the best available FarmQuest edition."""
    if app_factory is None:
        try:
            from farmquest.panda_app import FarmQuest3DApp
        except ModuleNotFoundError as exc:
            if exc.name in {"direct", "panda3d"}:
                print("Panda3D is not installed, so FarmQuest is starting the built-in desktop edition.")
                print("For the long-term 3D build, install: python -m pip install -r requirements-3d.txt")
                from farmquest.tk_app import TkFarmQuestApp

                app_factory = TkFarmQuestApp
            else:
                raise
        else:
            app_factory = FarmQuest3DApp

    app = app_factory()
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
