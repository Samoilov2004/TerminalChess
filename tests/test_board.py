import unittest
from src.board import ChessBoard 

class TestChessBoard(unittest.TestCase):

    def setUp(self):
        self.board = ChessBoard()

    def test_initial_position(self):
        self.assertEqual(self.board.get_piece_at(self._parse("e1")), 'K', "Белый король на e1")
        self.assertEqual(self.board.get_piece_at(self._parse("d8")), 'q', "Черный ферзь на d8")
        self.assertEqual(self.board.get_piece_at(self._parse("e2")), 'P', "Белая пешка на e2")
        self.assertEqual(self.board.turn, 'white', "В начале ход белых")

    def test_make_legal_move(self):
        move_made = self.board.make_move("e2e4")
        self.assertTrue(move_made, "Ход e2e4 должен быть выполнен")
        self.assertEqual(self.board.get_piece_at(self._parse("e4")), 'P', "Пешка должна быть на e4")
        self.assertEqual(self.board.get_piece_at(self._parse("e2")), '.', "Клетка e2 должна быть пустой")
        self.assertEqual(self.board.turn, 'black', "Ход должен перейти к черным")

    def test_make_illegal_move(self):
        initial_board_state = [row[:] for row in self.board.board]
        move_made = self.board.make_move("e2e5") # Нелегальный ход пешки
        self.assertFalse(move_made, "Нелегальный ход не должен быть выполнен")
        self.assertEqual(self.board.board, initial_board_state, "Состояние доски не должно измениться")
        self.assertEqual(self.board.turn, 'white', "Очередность хода не должна измениться")

    def test_check_and_checkmate(self):
        """Тестирует постановку мата (Детский мат)."""
        self.assertTrue(self.board.make_move("e2e4"))
        self.assertTrue(self.board.make_move("e7e5"))
        self.assertTrue(self.board.make_move("f1c4"))
        self.assertTrue(self.board.make_move("b8c6"))
        self.assertTrue(self.board.make_move("d1h5"))
        self.assertTrue(self.board.make_move("g8f6"))
        
        self.assertFalse(self.board.is_in_check('black'), "Черный король еще не под шахом до матующего хода")
        
        self.assertTrue(self.board.make_move("h5f7"))

        self.assertTrue(self.board.is_in_check('black'), "Черный король должен быть под шахом")
        self.assertEqual(self.board.is_game_over(), "checkmate", "Игра должна закончиться матом")
    
    def _parse(self, pos_str):
        col = ord(pos_str[0]) - ord('a')
        row = 8 - int(pos_str[1])
        return (row, col)

if __name__ == '__main__':
    unittest.main()

