import os
from typing import Dict, Optional
from Board import Board, WHITE

class TerminalRenderer:
    """
    Класс для "красивого" вывода доски и информации об игре в терминал.
    """
    def __init__(self, config: Dict):
        # Конфиг может содержать настройки вида
        # {'flip_board': True, 'piece_set': 'unicode'}
        self.config = config

    def _get_piece_symbol(self, piece):
        if not piece:
            return '.'
        
        if self.config.get('piece_set') == 'unicode':
            # Unicode символы для фигур
            unicode_map = {
                'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔',
                'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚',
            }
            return unicode_map.get(piece.symbol, '?')
        else:
            # Стандартные символы
            return piece.symbol

    def clear_screen(self):
        """Очищает экран терминала."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def draw_board(self, board: Board, last_move: Optional[tuple] = None, legal_moves_for_piece: Dict = {}):
        """
        Основной метод отрисовки.
        - board: объект доски
        - last_move: подсветить последний ход
        - legal_moves_for_piece: подсветить возможные ходы для выбранной фигуры
        """
        self.clear_screen()
        print("    --- PyChess Terminal ---")

        # Определяем, нужно ли переворачивать доску
        flip = self.config.get('flip_board', False) and board.color_to_move != WHITE
        
        # Ряды и колонки для отрисовки
        rows = range(8) if not flip else range(7, -1, -1)
        cols = range(8) if not flip else range(7, -1, -1)
        
        # Заголовки колонок
        col_headers = "  a b c d e f g h"
        if flip:
            col_headers = "  h g f e d c b a"
        print(col_headers)
        
        for r in rows:
            # Номер ряда
            row_header = 8 - r
            print(f"{row_header} ", end="")
            
            for c in cols:
                piece = board.get_piece_at((r, c))
                symbol = self._get_piece_symbol(piece)
                
                # Логика подсветки
                is_last_move = (last_move and ((r, c) in last_move))
                is_legal_dest = ((r, c) in legal_moves_for_piece)
                
                # Пример простой подсветки цветом (может не работать во всех терминалах)
                if is_last_move:
                    print(f"\033[44m{symbol}\033[0m ", end="") # Синий фон
                elif is_legal_dest:
                    print(f"\033[42m{symbol}\033[0m ", end="") # Зеленый фон
                else:
                    print(f"{symbol} ", end="")
            
            print(f" {row_header}")
        
        print(col_headers)
        print("-" * 25)
        
        # Вывод информации о состоянии игры
        status = board.get_game_status()
        if status == 'checkmate':
            winner = "Черные" if board.color_to_move == WHITE else "Белые"
            print(f"Игра окончена. Мат! Победили {winner}.")
        elif status == 'stalemate':
            print("Игра окончена. Пат!")
        elif status == 'draw':
            print("Игра окончена. Ничья.")
        else:
            turn = 'Белые' if board.color_to_move == WHITE else 'Черные'
            print(f"Ход: {turn}")
            if board.is_in_check(board.color_to_move):
                print("\033[91mВнимание: ШАХ!\033[0m")
        print("-" * 25)

src/game.py (Основной класс игры)
Этот класс связывает всё вместе.

python
import chess
from core.board import Board, WHITE, BLACK
from engine.stockfish_engine import StockfishEngine
from io.renderer import TerminalRenderer

class Game:
    def __init__(self, player_color: str = WHITE, skill_level: int = 5):
        self.board = Board()
        self.engine = StockfishEngine(skill_level=skill_level)
        self.player_color = player_color
        
        # Настройки, которые можно менять
        self.config = {
            'flip_board': True,
            'piece_set': 'unicode' # 'ascii' или 'unicode'
        }
        self.renderer = TerminalRenderer(self.config)
        self.last_move = None

    def run(self):
        """Основной игровой цикл."""
        while self.board.get_game_status() == 'in_progress':
            self.renderer.draw_board(self.board, self.last_move)
            
            if self.board.color_to_move == self.player_color:
                # Ход игрока
                move_made = False
                while not move_made:
                    try:
                        user_input = input("Ваш ход (например, e2e4, или 'q' для выхода): ")
                        if user_input.lower() == 'q':
                            self.engine.close()
                            return
                        move = self._parse_user_input(user_input)
                        if move in self.board.get_legal_moves():
                            self.board.make_move(move)
                            self.last_move = move
                            move_made = True
                        else:
                            print("Нелегальный ход. Попробуйте снова.")
                    except ValueError as e:
                        print(f"Ошибка ввода: {e}. Формат: 'e2e4'.")
            else:
                # Ход компьютера
                print("Компьютер думает...")
                best_move_lib = self.engine.find_best_move(self.board)
                move = self._convert_lib_move_to_our(best_move_lib)
                
                # Проверка на превращение пешки
                promo_class = None
                if best_move_lib.promotion:
                    # chess.QUEEN = 5
                    if best_move_lib.promotion == chess.QUEEN:
                        from pieces.queen import Queen
                        promo_class = Queen
                    # ... (добавить другие фигуры при необходимости)
                
                self.board.make_move(move, promo_class)
                self.last_move = move

        # Конец игры
        self.renderer.draw_board(self.board)
        self.engine.close()

    def _parse_user_input(self, uci_move: str) -> tuple:
        """Конвертирует ход из нотации 'e2e4' в наши координаты ((6,4), (4,4))."""
        if len(uci_move) < 4:
            raise ValueError("Некорректная длина хода.")
        
        start_col = 'abcdefgh'.find(uci_move[0])
        start_row = 8 - int(uci_move[1])
        end_col = 'abcdefgh'.find(uci_move[2])
        end_row = 8 - int(uci_move[3])

        if -1 in [start_col, start_row, end_col, end_row]:
            raise ValueError("Некорректные координаты.")
        
        return ((start_row, start_col), (end_row, end_col))

    def _convert_lib_move_to_our(self, lib_move: chess.Move) -> tuple:
        uci = lib_move.uci()
        return self._parse_user_input(uci)

if __name__ == '__main__':
    color_choice = input("За какой цвет хотите играть? (w/b): ").lower()
    player_color = WHITE if color_choice == 'w' else BLACK
    
    skill = int(input("Выберите уровень сложности Stockfish (0-20): "))

    game = Game(player_color=player_color, skill_level=skill)
    game.run()