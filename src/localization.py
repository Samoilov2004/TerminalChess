import json
import os
from typing import Dict, Any

class LocalizationManager:
    """
    Простой менеджер локализации для загрузки и предоставления строк.
    """
    def __init__(self, lang: str = "ru", locales_dir: str = "locales"):
        self.lang = lang
        self.strings: Dict[str, Any] = {}
        self._load_strings(locales_dir)

    def _load_strings(self, locales_dir: str):
        filepath = os.path.join(locales_dir, f"{self.lang}.json")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.strings = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Localization file not found for language '{self.lang}'.")
            if self.lang != 'en':
                self.lang = 'en'
                self._load_strings(locales_dir)

    def get(self, key: str, **kwargs) -> str:
        """
        Возвращает локализованную строку по ключу.
        Поддерживает форматирование с помощью .format(**kwargs).
        """
        string_template = self.strings.get(key, f"_{key}_")
        return string_template.format(**kwargs)