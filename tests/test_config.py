
from backend.core.config import Settings


def test_default_settings():
    settings = Settings(_env_file=None)

    assert settings.app_name == "CyberMind"
    assert settings.app_version == "0.1.0"
    assert settings.debug is True


def test_custom_settings():
    settings = Settings(
        app_name="CyberMind Test",
        app_version="0.2.0",
        debug=False,
        _env_file=None,
    )

    assert settings.app_name == "CyberMind Test"
    assert settings.app_version == "0.2.0"
    assert settings.debug is False
