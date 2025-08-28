from typing import List, Tuple, TYPE_CHECKING
from .piece import Piece, WHITE, BLACK

if TYPE_CHECKING:
    from ..Board import Board

class Knight(Piece):
    def __init__(self, color: str):
        super().__init__(color)
        self.symbol = 'N' if self.color == WHITE else 'n'

    def get_moves(self, board: 'Board', position: Tuple[int, int]) -> List[Tuple[int, int]]:
        row, col = position
        moves = []
        # All 8 possible knight moves in the format (row offset, column offset)
        potential_moves = [
            (row - 2, col + 1), (row - 2, col - 1),
            (row - 1, col + 2), (row - 1, col - 2),
            (row + 1, col + 2), (row + 1, col - 2),
            (row + 2, col + 1), (row + 2, col - 1),
        ]

        for r, c in potential_moves:
            # 1. Check that the move is within the board
            if 0 <= r < 8 and 0 <= c < 8:
                target_piece = board.get_piece_at((r, c))
                # 2. If the cell is empty or occupied by an opponent's piece
                if target_piece is None or target_piece.color != self.color:
                    moves.append((r, c))
        
        return moves