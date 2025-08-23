# tests/test_board.py

import unittest
from src.board import ChessBoard

class TestBoardMechanics(unittest.TestCase):

    def setUp(self):
        """Создает новую доску перед каждым тестом."""
        self.board = ChessBoard()

    def test_basic_legal_and_illegal_moves(self):
        """Тестирует простой легальный и нелегальный ход."""
        self.assertTrue(self.board.make_move("e2e4"), "Ход e2e4 должен быть легальным")
        self.assertEqual(self.board.get_piece_at((4, 4)), 'P', "Пешка должна оказаться на e4")
        self.assertEqual(self.board.turn, 'black', "Ход должен перейти к черным")

        self.assertFalse(self.board.make_move("d2d4"), "Черные не могут ходить белой пешкой")
        self.assertEqual(self.board.turn, 'black', "Ход не должен был смениться")

    def test_white_short_castling(self):
        """Проверяет логику белой короткой рокировки."""
        board = ChessBoard() # Создаем свежую доску
        board.board[7][5] = '.' # f1
        board.board[7][6] = '.' # g1
        self.assertTrue(board.make_move("e1g1"), "Белая короткая рокировка должна быть возможна")
        self.assertEqual(board.get_piece_at((7, 6)), 'K', "Король должен быть на g1")
        self.assertEqual(board.get_piece_at((7, 5)), 'R', "Ладья должна быть на f1")

    def test_white_long_castling(self):
        """Проверяет логику белой длинной рокировки."""
        board = ChessBoard() # Создаем свежую доску
        board.board[7][1] = '.' # b1
        board.board[7][2] = '.' # c1
        board.board[7][3] = '.' # d1
        self.assertTrue(board.make_move("e1c1"), "Белая длинная рокировка должна быть возможна")
        self.assertEqual(board.get_piece_at((7, 2)), 'K', "Король должен быть на c1")
        self.assertEqual(board.get_piece_at((7, 3)), 'R', "Ладья должна быть на d1")

        
    def test_en_passant_capture(self):
        """Проверяет механику взятия на проходе."""
        # 1. Создаем ситуацию для взятия на проходе
        self.board.make_move("e2e4") # W
        self.board.make_move("a7a6") # B (пустой ход)
        self.board.make_move("e4e5") # W
        self.board.make_move("d7d5") # B (черная пешка идет на d5, рядом с белой)

        # 2. Белые должны иметь возможность взять на d6
        self.assertTrue(self.board.make_move("e5d6"), "Взятие на проходе e5d6 должно быть легальным")

        # 3. Проверяем результат
        self.assertEqual(self.board.get_piece_at((2, 3)), 'P', "Белая пешка должна быть на d6")
        self.assertEqual(self.board.get_piece_at((3, 3)), '.', "Черная пешка на d5 должна быть съедена")
        self.assertEqual(self.board.get_piece_at((3, 4)), '.', "Клетка e5 должна быть пуста")

    def test_checkmate_scenario(self):
        """Проверяет постановку 'Детского мата'."""
        self.board.make_move("e2e4")
        self.board.make_move("e7e5")
        self.board.make_move("f1c4")
        self.board.make_move("b8c6")
        self.board.make_move("d1h5")
        self.board.make_move("g8f6")
        
        self.assertFalse(self.board.is_in_check('black'), "Черные еще не под шахом")
        
        # Матующий ход
        self.board.make_move("h5f7")
        
        self.assertTrue(self.board.is_in_check('black'), "Черные должны быть под шахом")
        self.assertEqual(self.board.is_game_over(), "checkmate", "Должен быть зафиксирован мат")

if __name__ == '__main__':
    unittest.main()