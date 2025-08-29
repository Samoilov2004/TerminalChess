import os
from typing import Dict, Optional
from Board import Board, WHITE
from localization import LocalizationManager

class TerminalRenderer:
    """
    Класс для "красивого" вывода доски и информации об игре в терминал.
    """
    def __init__(self, config: Dict, localizer: LocalizationManager):
        self.config = config
        self.localizer = localizer

    def _get_piece_symbol(self, piece) -> str:
        """Возвращает символ фигуры в зависимости от настроек."""
        if not piece:
            return '.'
        
        if self.config.get('piece_set') == 'unicode':
            unicode_map = {
                'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔',
                'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚',
            }
            return unicode_map.get(piece.symbol, '?')
        else:
            return piece.symbol

    def clear_screen(self):
        """Очищает экран терминала."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def draw_board(self, board: Board, last_move: Optional[tuple] = None):
        """
        Основной метод отрисовки доски и статуса игры.
        Учитывает стиль доски из настроек.
        """
        self.clear_screen()
        print(self.localizer.get("app_title"))
        
        # Получаем стиль доски из конфига, по умолчанию 'classic'
        board_style = self.config.get('board_style', 'classic')
        
        flip = self.config.get('flip_board', False) and board.color_to_move != WHITE
        
        rows = range(8) if not flip else range(7, -1, -1)
        cols = range(8) if not flip else range(7, -1, -1)
        
        col_headers = "  a b c d e f g h"
        if flip:
            col_headers = "  h g f e d c b a"
        print(col_headers)

        if board_style == 'pretty':
            print("-------------------------")

        for r in rows:
            row_header = 8 - r
            print(f"{row_header} ", end="")
            
            for c in cols:
                piece = board.get_piece_at((r, c))
                symbol = self._get_piece_symbol(piece)
                
                is_highlight_enabled = self.config.get('highlighting', True)
                is_last_move = is_highlight_enabled and last_move and ((r, c) == last_move[0] or (r, c) == last_move[1])
                
                if is_last_move:
                    print(f"\033[44m{symbol}\033[0m ", end="")
                else:
                    print(f"{symbol} ", end="")
            
            print(f" {row_header}")

            if board_style == 'pretty' and r != (0 if not flip else 7):
                 print("-------------------------")
