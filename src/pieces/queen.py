from typing import List, Tuple, TYPE_CHECKING
from .piece import Piece, WHITE, BLACK

if TYPE_CHECKING:
    from Board import Board

class Queen(Piece):
    def __init__(self, color: str):
        super().__init__(color)
        self.symbol = 'Q' if self.color == WHITE else 'q'

    def get_moves(self, board: 'Board', position: Tuple[int, int]) -> List[Tuple[int, int]]:
        moves = []
        # Все 8 направлений: как у ладьи + как у слона
        directions = [
            (0, 1), (0, -1), (1, 0), (-1, 0),  # Прямые
            (1, 1), (1, -1), (-1, 1), (-1, -1)   # Диагонали
        ]
        
        for dr, dc in directions:
            current_row, current_col = position
            while True:
                current_row += dr
                current_col += dc
                pos = (current_row, current_col)

                if not board.is_on_board(pos):
                    break

                target_piece = board.get_piece_at(pos)
                if target_piece is None:
                    moves.append(pos)
                elif target_piece.color != self.color:
                    moves.append(pos)
                    break
                else:
                    break
        
        return moves