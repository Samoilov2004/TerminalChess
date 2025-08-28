from base_test_case import BasePieceTestCase
from pieces import pawn, rook
from Board import WHITE, BLACK

class TestPawn(BasePieceTestCase):
    def test_white_pawn_initial_move(self):
        p = pawn.Pawn(WHITE)
        self.board.set_piece_at((6, 4), p) # e2
        expected_moves = [(5, 4), (4, 4)] # e3, e4
        self.assertMovesUnorderedEqual(expected_moves, p.get_moves(self.board, (6, 4)))

    def test_white_pawn_blocked(self):
        p = pawn.Pawn(WHITE)
        blocker = rook.Rook(BLACK)
        self.board.set_piece_at((6, 4), p) # e2
        self.board.set_piece_at((5, 4), blocker) # e3
        # Двойной ход невозможен, т.к. путь блокирован
        self.assertMovesUnorderedEqual([], p.get_moves(self.board, (6, 4)))

    def test_white_pawn_capture(self):
        p = pawn.Pawn(WHITE)
        enemy1 = rook.Rook(BLACK)
        enemy2 = rook.Rook(BLACK)
        friendly = rook.Rook(WHITE)
        p.has_moved = True # Чтобы не было двойного хода
        self.board.set_piece_at((3, 4), p) # e5
        self.board.set_piece_at((2, 3), enemy1) # d6
        self.board.set_piece_at((2, 5), enemy2) # f6
        self.board.set_piece_at((2, 4), friendly) # e6 (блокирует ход вперед)
        expected_moves = [(2, 3), (2, 5)] # Взятия на d6 и f6
        self.assertMovesUnorderedEqual(expected_moves, p.get_moves(self.board, (3, 4)))
    
    def test_black_pawn_initial_move(self):
        p = pawn.Pawn(BLACK)
        self.board.set_piece_at((1, 4), p) # e7
        expected_moves = [(2, 4), (3, 4)] # e6, e5
        self.assertMovesUnorderedEqual(expected_moves, p.get_moves(self.board, (1, 4)))

    def test_en_passant(self):
        # Ставим белую пешку на e5
        white_pawn = pawn.Pawn(WHITE)
        white_pawn.has_moved = True
        self.board.set_piece_at((3, 4), white_pawn) # e5
        
        # Симулируем двойной ход черной пешки с d7 на d5
        black_pawn_start = (1, 3) # d7
        black_pawn_end = (3, 3) # d5
        
        # --->> ВОТ ИСПРАВЛЕНИЕ: Ставим черную пешку на доску <<---
        black_pawn = pawn.Pawn(BLACK)
        self.board.set_piece_at(black_pawn_start, black_pawn)

        # Теперь ход будет выполнен корректно
        self.board.make_move((black_pawn_start, black_pawn_end))
        
        # Теперь en_passant_target должен быть (2, 3) - поле d6
        self.assertEqual(self.board.en_passant_target, (2, 3))
        
        # Проверяем ходы белой пешки. Она должна уметь бить на d6
        expected_moves = [
            (2, 4), #Обычный ход вперед на e6
            (2, 3)  #Взятие на проходе на d6
        ]
        self.assertMovesUnorderedEqual(expected_moves, white_pawn.get_moves(self.board, (3, 4)))