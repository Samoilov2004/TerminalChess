from typing import List, Tuple, TYPE_CHECKING
from .piece import Piece, WHITE, BLACK

if TYPE_CHECKING:
    from Board import Board

class Bishop(Piece):
    def __init__(self, color: str):
        super().__init__(color)
        self.symbol = 'B' if self.color == WHITE else 'b'

    def get_moves(self, board: 'Board', position: Tuple[int, int]) -> List[Tuple[int, int]]:
        moves = []
        # Направления движения: по диагоналям
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
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