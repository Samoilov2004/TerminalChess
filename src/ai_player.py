import chess
import chess.engine
import platform

import chess
import chess.engine
import platform
import os

class AIPlayer:
    def __init__(self, skill_level=10):
        """
        Инициализирует ИИ-игрока и запускает правильную версию Stockfish.
        """
        # --- НАЧАЛО ИСПРАВЛЕНИЙ ---
        
        system = platform.system()
        if system == "Windows":
            engine_name = "stockfish_windows.exe" # Предполагаем, что так называется файл для Windows
        elif system == "Darwin": # Darwin - это официальное название ядра macOS
            engine_name = "stockfish_macos"
        elif system == "Linux":
            engine_name = "stockfish_linux"
        else:
            print(f"ОШИБКА: Неподдерживаемая операционная система: {system}")
            self.engine = None
            return

        # Формируем полный путь к движку
        self.engine_path = os.path.join("engine", engine_name)
        
        # --- КОНЕЦ ИСПРАВЛЕНИЙ ---

        # На macOS и Linux нужно выдать файлу права на исполнение
        if system != "Windows" and os.path.exists(self.engine_path):
            try:
                os.chmod(self.engine_path, 0o755)
            except OSError as e:
                print(f"Предупреждение: не удалось изменить права для файла движка: {e}")

        try:
            # Запускаем движок как подпроцесс
            self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
            # Устанавливаем уровень сложности (0-20), который поддерживается Stockfish
            self.engine.configure({"Skill Level": skill_level})
            print("Движок Stockfish успешно запущен.")
        except FileNotFoundError:
            print(f"ОШИБКА: Движок Stockfish не найден по пути: {self.engine_path}")
            print("Убедитесь, что файл существует и правильно назван для вашей ОС.")
            self.engine = None
        except Exception as e:
            print(f"Произошла ошибка при запуске Stockfish: {e}")
            self.engine = None

    def get_best_move(self, fen_string, time_limit=1.0):
        """
        Анализирует позицию и возвращает лучший ход в формате UCI ('e2e4').
        
        :param fen_string: Позиция в формате FEN.
        :param time_limit: Время на размышление в секундах.
        :return: Строка с ходом 'e2e4' или None, если движок не работает.
        """
        if not self.engine:
            return None
            
        try:
            board = chess.Board(fen_string)
            # Просим движок проанализировать позицию и найти лучший ход
            result = self.engine.play(board, chess.engine.Limit(time=time_limit))
            # .uci() возвращает ход в нужном нам формате 'e2e4'
            return result.move.uci()
        except Exception as e:
            print(f"Ошибка при получении хода от Stockfish: {e}")
            return None


    def quit(self):
        """Корректно завершает работу движка, закрывая процесс."""
        if self.engine:
            print("Завершение работы движка Stockfish...")
            self.engine.quit()