import os
import sys
from pathlib import Path


def save_secret_key(key: str) -> str:
    """
    Saves the secret key to the .env file.
    """
    env_file_path = _get_env_file_path()

    print("Secret key does not exist; saving to", env_file_path, file=sys.stderr)
    with env_file_path.open("a", encoding="UTF-8") as env_file:
        env_file.write(f"SECRET_KEY={key}\n")

    return key


def _get_env_file_path() -> Path:
    """
    Return the path to the .env file at the root of the repository
    """
    if "FST_API_ENV_FILE_PATH" in os.environ:
        return Path(os.environ["FST_API_ENV_FILE_PATH"])

    path = Path(__file__)
    while path != path.parent and not (path / "Pipfile").is_file():
        path = path.parent

    assert (path / "Pipfile").is_file()

    base_dir = path
    return base_dir / "docker" / ".env"
