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

    def get_analysis(self, fen_string, num_lines=3, time_limit=1.0):
        """
        Анализирует позицию и возвращает несколько лучших ходов с оценкой.
        :param fen_string: Позиция в формате FEN.
        :param num_lines: Количество лучших ходов для возврата.
        :param time_limit: Время на анализ.
        :return: Список словарей [{'move': 'e2e4', 'score': 0.25}, ...], или None.
        """
        if not self.engine:
            return None
        
        try:
            board = chess.Board(fen_string)
            # multipv - это "multiple principal variations", т.е. несколько лучших линий
            analysis = self.engine.analyse(board, chess.engine.Limit(time=time_limit), multipv=num_lines)
            
            top_moves = []
            for info in analysis:
                score_obj = info.get("score")
                if score_obj is not None:
                    # Преобразуем оценку в понятный формат (в пешках)
                    # PovScore(cp=25, WHITE) -> 0.25
                    # PovScore(cp=-50, BLACK) -> -0.50 (с точки зрения черных)
                    # PovScore(Mate(2), WHITE) -> Мат в 2 хода
                    
                    if score_obj.is_mate():
                        score_text = f"Мат в {score_obj.white().mate()}"
                    else:
                        # Приводим оценку к точке зрения белых
                        score_val = score_obj.white().score() / 100.0
                        score_text = f"{'+' if score_val > 0 else ''}{score_val:.2f}"
                else:
                    score_text = "N/A"
                    
                top_moves.append({
                    "move": info.get("pv")[0].uci(),
                    "score": score_text
                })
            return top_moves
        except Exception as e:
            print(f"Ошибка при анализе позиции: {e}")
            return None

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