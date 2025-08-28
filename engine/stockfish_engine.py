import chess
import chess.engine
import platform
import os
from typing import Optional, TYPE_CHECKING

# Этот импорт нужен только для аннотаций типов, чтобы избежать циклической зависимости.
if TYPE_CHECKING:
    from Board import Board

class StockfishEngine:
    """
    Обертка для движка Stockfish. Автоматически находит исполняемый файл
    для текущей ОС и управляет взаимодействием с ним.
    """
    def __init__(self, skill_level: int = 10, search_time: float = 1.0):
        self.engine_path = self._get_stockfish_path()
        if not self.engine_path:
            # Выбрасываем стандартную ошибку. Game класс её поймает и локализует.
            raise FileNotFoundError("Stockfish executable not found in engine directory.")
        
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        except chess.engine.EngineError as e:
            # То же самое - стандартная ошибка для перехвата.
            raise RuntimeError(f"Failed to start Stockfish. Is it executable? Original error: {e}")

        self.engine.configure({"Skill Level": min(max(skill_level, 0), 20)})
        self.search_time = search_time

    def _get_stockfish_path(self) -> Optional[str]:
        """Находит путь к исполняемому файлу Stockfish в этой же папке."""
        system_name = platform.system()
        # Папка, в которой находится этот скрипт
        current_dir = os.path.dirname(__file__)

        if system_name == "Darwin": # macOS
            path = os.path.join(current_dir, "stockfish_macos")
        elif system_name == "Linux":
            path = os.path.join(current_dir, "stockfish_linux")
        elif system_name == "Windows":
            path = os.path.join(current_dir, "stockfish_windows.exe")
        else:
            return None
            
        return path if os.path.exists(path) else None

    def find_best_move_from_fen(self, fen: str) -> chess.Move:
        """Находит лучший ход для позиции, представленной в виде FEN-строки."""
        lib_board = chess.Board(fen)
        result = self.engine.play(lib_board, chess.engine.Limit(time=self.search_time))
        return result.move

    def close(self):
        """Корректно завершает работу движка."""
        self.engine.quit()