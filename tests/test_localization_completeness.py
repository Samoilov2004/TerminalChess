import unittest
import os
import re
import json
import sys


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC_DIR = os.path.join(ROOT_DIR, 'src')
LOCALES_DIR = os.path.join(ROOT_DIR, 'locales')

sys.path.insert(0, SRC_DIR)

class TestLocalizationCompleteness(unittest.TestCase):

    def _find_localization_keys_in_code(self) -> set:
        """
        Сканирует все .py файлы в папке src и ищет вызовы localizer.get("...").
        Возвращает множество всех найденных ключей.
        """
        # Регулярное выражение для поиска ключей.
        key_pattern = re.compile(r"""
            localizer\.get\(\s*    
            ['"](.*?)['"]          
            [\s,)]                 
        """, re.VERBOSE)
        
        found_keys = set()
        
        for subdir, _, files in os.walk(SRC_DIR):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(subdir, file)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = key_pattern.findall(content)
                        for key in matches:
                            if '{' not in key:
                                found_keys.add(key)
                                
        return found_keys

    def test_all_keys_are_present_in_all_locale_files(self):
        """
        Главный тест: проверяет, что все ключи из кода есть во всех файлах локализации.
        """
        code_keys = self._find_localization_keys_in_code()
        self.assertGreater(len(code_keys), 0, "Не найдено ни одного ключа локализации в коде. Проверьте сканер.")

        locale_files = [f for f in os.listdir(LOCALES_DIR) if f.endswith('.json')]
        self.assertGreater(len(locale_files), 0, "Не найдено ни одного файла локализации в папке locales.")
        
        all_errors = []

        for filename in locale_files:
            filepath = os.path.join(LOCALES_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    locale_data = json.load(f)
                    locale_keys = set(locale_data.keys())
                    
                    # Находим ключи, которые есть в коде, но отсутствуют в этом файле локализации
                    missing_keys = code_keys - locale_keys
                    if missing_keys:
                        error_msg = f"\nВ файле '{filename}' отсутствуют ключи: {sorted(list(missing_keys))}"
                        all_errors.append(error_msg)
                
                except json.JSONDecodeError:
                    error_msg = f"\nФайл '{filename}' содержит невалидный JSON."
                    all_errors.append(error_msg)

        if all_errors:
            self.fail("\n--- Обнаружены проблемы с локализацией ---\n" + "\n".join(all_errors))
        else:
            print(f"\nПроверка локализации успешна. Проверено {len(code_keys)} ключей в {len(locale_files)} файлах.")
