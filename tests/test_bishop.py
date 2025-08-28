from base_test_case import BasePieceTestCase
from pieces import bishop, rook
from Board import WHITE, BLACK

class TestBishop(BasePieceTestCase):
    def test_bishop_empty_board(self):
        b = bishop.Bishop(WHITE)
        self.board.set_piece_at((3, 3), b) # d5
        expected_moves = [
            (0, 0), (1, 1), (2, 2), (4, 4), (5, 5), (6, 6), (7, 7),
            (0, 6), (1, 5), (2, 4), (4, 2), (5, 1), (6, 0)
        ]
        self.assertMovesUnorderedEqual(expected_moves, b.get_moves(self.board, (3, 3)))

    def test_bishop_with_blockers(self):
        b = bishop.Bishop(WHITE)
        enemy = rook.Rook(BLACK)
        friendly = rook.Rook(WHITE)
        self.board.set_piece_at((3, 3), b)
        self.board.set_piece_at((1, 1), enemy)   
        self.board.set_piece_at((5, 5), friendly)
        expected_moves = [
            (2, 2), (1, 1), 
            (4, 4),         
            (0, 6), (1, 5), (2, 4), (4, 2), (5, 1), (6, 0)
        ]
        self.assertMovesUnorderedEqual(expected_moves, b.get_moves(self.board, (3, 3)))