from typing import List, Tuple, TYPE_CHECKING
from .piece import Piece, WHITE, BLACK

if TYPE_CHECKING:
    from Board import Board

class Rook(Piece):
    def __init__(self, color: str):
        super().__init__(color)
        self.symbol = 'R' if self.color == WHITE else 'r'

    def get_moves(self, board: 'Board', position: Tuple[int, int]) -> List[Tuple[int, int]]:
        moves = []
        # Направления движения: вверх, вниз, влево, вправо
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dr, dc in directions:
            current_row, current_col = position
            while True:
                current_row += dr
                current_col += dc
                pos = (current_row, current_col)

                if not board.is_on_board(pos):
                    break  # Вышли за пределы доски

                target_piece = board.get_piece_at(pos)
                if target_piece is None:
                    moves.append(pos)  # Пустое поле, добавляем и продолжаем скользить
                elif target_piece.color != self.color:
                    moves.append(pos)  # Фигура противника, бьем ее и останавливаемся
                    break
                else:
                    break   # Наша фигура, останавливаемся
        
        return moves