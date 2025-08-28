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
        """
        self.clear_screen()
        print(self.localizer.get("app_title"))

        # Определяем, нужно ли переворачивать доску
        flip = self.config.get('flip_board', False) and board.color_to_move != WHITE
        
        rows = range(8) if not flip else range(7, -1, -1)
        cols = range(8) if not flip else range(7, -1, -1)
        
        col_headers = "  a b c d e f g h"
        if flip:
            col_headers = "  h g f e d c b a"
        print(col_headers)
        
        for r in rows:
            row_header = 8 - r
            print(f"{row_header} ", end="")
            
            for c in cols:
                piece = board.get_piece_at((r, c))
                symbol = self._get_piece_symbol(piece)
                
                # Логика подсветки
                is_last_move = (last_move and ((r, c) == last_move[0] or (r, c) == last_move[1]))
                
                if is_last_move:
                    print(f"\033[44m{symbol}\033[0m ", end="") # Синий фон для подсветки
                else:
                    print(f"{symbol} ", end="")
            
            print(f" {row_header}")
        
        print(col_headers)
        print("-" * 25)
        
        # Вывод информации о состоянии игры
        status = board.get_game_status()
        if status == 'checkmate':
            winner_color_key = "black" if board.color_to_move == WHITE else "white"
            winner_name = self.localizer.get(f"player_{winner_color_key}")
            print(self.localizer.get("game_over_checkmate", winner=winner_name))
        elif status == 'stalemate':
            print(self.localizer.get("game_over_stalemate"))
        elif status == 'draw':
            print(self.localizer.get("game_over_draw"))
        else:
            player_color_key = "white" if board.color_to_move == WHITE else "black"
            player_name = self.localizer.get(f"player_{player_color_key}")
            print(self.localizer.get("turn_prompt", player=player_name))
            if board.is_in_check(board.color_to_move):
                print(f"\033[91m{self.localizer.get('check_warning')}\033[0m")
        print("-" * 25)