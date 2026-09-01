from farmquest.managers.localization_manager import LocalizationManager


def test_localization_falls_back_to_english() -> None:
    manager = LocalizationManager(language="fr")
    assert manager.translate("title") == "FarmQuest"
    assert manager.translate("nonexistent_key") == "nonexistent_key"
