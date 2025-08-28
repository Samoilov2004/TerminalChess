from base_test_case import BasePieceTestCase
from pieces import knight, rook
from Board import WHITE, BLACK

class TestKnight(BasePieceTestCase):
    def test_knight_from_center(self):
        k = knight.Knight(WHITE)
        self.board.set_piece_at((3, 3), k) # d5
        expected_moves = [
            (1, 2), (1, 4), (2, 1), (2, 5),
            (4, 1), (4, 5), (5, 2), (5, 4)
        ]
        self.assertMovesUnorderedEqual(expected_moves, k.get_moves(self.board, (3, 3)))

    def test_knight_from_corner(self):
        k = knight.Knight(WHITE)
        self.board.set_piece_at((7, 7), k) # h1
        expected_moves = [(5, 6), (6, 5)] # g3, f2
        self.assertMovesUnorderedEqual(expected_moves, k.get_moves(self.board, (7, 7)))

    def test_knight_blocked_by_friendly(self):
        k = knight.Knight(WHITE)
        blocker = rook.Rook(WHITE)
        self.board.set_piece_at((3, 3), k)
        self.board.set_piece_at((1, 2), blocker)
        # Все ходы, кроме одного заблокированного
        expected_moves = [
            (1, 4), (2, 1), (2, 5), (4, 1), 
            (4, 5), (5, 2), (5, 4)
        ]
        self.assertMovesUnorderedEqual(expected_moves, k.get_moves(self.board, (3, 3)))