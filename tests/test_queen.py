from base_test_case import BasePieceTestCase
from pieces import queen
from Board import WHITE

class TestQueen(BasePieceTestCase):
    def test_queen_empty_board(self):
        q = queen.Queen(WHITE)
        self.board.set_piece_at((3, 3), q)
        # Ходы ладьи + ходы слона
        expected_moves = [
            (3, 0), (3, 1), (3, 2), (3, 4), (3, 5), (3, 6), (3, 7),
            (0, 3), (1, 3), (2, 3), (4, 3), (5, 3), (6, 3), (7, 3),
            (0, 0), (1, 1), (2, 2), (4, 4), (5, 5), (6, 6), (7, 7),
            (0, 6), (1, 5), (2, 4), (4, 2), (5, 1), (6, 0)
        ]
        self.assertMovesUnorderedEqual(expected_moves, q.get_moves(self.board, (3, 3)))