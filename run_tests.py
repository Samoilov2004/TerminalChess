import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

if __name__ == '__main__':
    # Автоматически находим все тесты в папке 'tests'
    loader = unittest.TestLoader()
    suite = loader.discover('tests')
    
    # Запускаем тесты с подробным выводом
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Выход с кодом 1, если были ошибки, для CI/CD систем
    if not result.wasSuccessful():
        sys.exit(1)