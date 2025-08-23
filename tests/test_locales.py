import unittest
import os
import json
import re

class TestLocalization(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """
        Этот метод выполняется один раз перед всеми тестами в классе.
        Он собирает всю необходимую информацию: ключи из кода и данные из файлов.
        """
        cls.locales_dir = 'locales'
        cls.main_py_path = 'main.py'
        
        # 1. Находим все ключи, используемые в T("...") в main.py
        cls.used_keys = cls._find_keys_in_code(cls.main_py_path)
        
        # 2. Загружаем все файлы локализации
        cls.locales_data = cls._load_all_locales(cls.locales_dir)
        
        print(f"\n[Locale Test] Найдено {len(cls.used_keys)} уникальных ключей локализации в коде.")
        print(f"[Locale Test] Загружено {len(cls.locales_data)} языковых файлов: {list(cls.locales_data.keys())}")

    @staticmethod
    def _find_keys_in_code(filepath):
        """Использует регулярное выражение для поиска всех ключей типа T('key') или T("key")."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            # Regex ищет T( потом ' или ", захватывает все символы до следующей ' или "
            found_keys = re.findall(r"T\(['\"](.*?)['\"]\)", content)
            return set(found_keys) # Используем set для получения только уникальных ключей
        except FileNotFoundError:
            return set()

    @staticmethod
    def _load_all_locales(locales_dir):
        """Загружает все .json файлы из указанной директории."""
        data = {}
        if not os.path.exists(locales_dir):
            return data
            
        for filename in os.listdir(locales_dir):
            if filename.endswith('.json'):
                lang_code = filename.split('.')[0]
                filepath = os.path.join(locales_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data[lang_code] = json.load(f)
        return data

    def test_all_keys_are_in_every_locale_file(self):
        """
        Главный тест: проверяет, что каждый ключ из кода существует в каждом файле локализации.
        """
        self.assertTrue(self.used_keys, "Не найдено ни одного ключа локализации в main.py. Тест не может быть выполнен.")
        self.assertTrue(self.locales_data, "Не найдено ни одного файла локализации в папке 'locales'.")

        for lang_code, lang_data in self.locales_data.items():
            for key in self.used_keys:
                with self.subTest(lang=lang_code, key=key):
                    self.assertIn(key, lang_data, 
                                  f"Ключ '{key}' отсутствует в файле '{lang_code}.json'")

if __name__ == '__main__':
    unittest.main()
