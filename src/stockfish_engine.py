import chess
import chess.engine
import platform
import os
from typing import Optional, TYPE_CHECKING
from localization import LocalizationManager

if TYPE_CHECKING:
    from Board import Board

class StockfishEngine:
    """
    Класс-обертка для взаимодействия с движком Stockfish.
    """
    def __init__(self, localizer: LocalizationManager, skill_level: int = 10, search_time: float = 1.0):
        self.localizer = localizer # Сохраняем экземпляр локализатора
        
        self.engine_path = self._get_stockfish_path()
        if not self.engine_path:
            # Используем локализатор для сообщения об ошибке
            raise FileNotFoundError(self.localizer.get("stockfish_not_found"))
        
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        except chess.engine.EngineError as e:
            # Используем локализатор здесь тоже
            raise RuntimeError(self.localizer.get("stockfish_exec_error", error=e))

        self.engine.configure({"Skill Level": min(max(skill_level, 0), 20)})
        self.search_time = search_time

    def _get_stockfish_path(self) -> Optional[str]:
        system_name = platform.system()
        base_path = "engine" 
        if system_name == "Darwin":
            path = os.path.join(base_path, "stockfish_macos")
        elif system_name == "Linux":
            path = os.path.join(base_path, "stockfish_linux")
        elif system_name == "Windows":
            path = os.path.join(base_path, "stockfish_windows.exe")
        else:
            return None
        return path if os.path.exists(path) else None

    # Методы find_best_move, close, _convert_to_lib_board, _board_to_fen остаются без изменений
    def find_best_move(self, board: 'Board') -> chess.Move:
        lib_board = self._convert_to_lib_board(board)
        result = self.engine.play(lib_board, chess.engine.Limit(time=self.search_time))
        return result.move

    def close(self):
        self.engine.quit()

    def _convert_to_lib_board(self, our_board: 'Board') -> chess.Board:
        fen = self._board_to_fen(our_board)
        return chess.Board(fen)

    def _board_to_fen(self, b: 'Board') -> str:
        pieces_fen = ""
        for r in range(8):
            empty_count = 0
            for c in range(8):
                piece = b.get_piece_at((r, c))
                if piece:
                    if empty_count > 0: pieces_fen += str(empty_count)
                    empty_count = 0
                    pieces_fen += piece.symbol
                else: empty_count += 1
            if empty_count > 0: pieces_fen += str(empty_count)
            if r < 7: pieces_fen += '/'
        active_color = b.color_to_move
        castling_fen = str(b.castling_rights)
        en_passant_fen = "-"
        if b.en_passant_target:
            row, col = b.en_passant_target
            en_passant_fen = f"{'abcdefgh'[col]}{8 - row}"
        return f"{pieces_fen} {active_color} {castling_fen} {en_passant_fen} {b.halfmove_clock} {b.fullmove_number}"
