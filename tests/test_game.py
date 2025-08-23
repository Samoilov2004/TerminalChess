# tests/test_game.py

import unittest
from src.game import Game

class TestGameRules(unittest.TestCase):

    def setUp(self):
        """Создает новую игру перед каждым тестом."""
        self.game = Game()

    def test_initial_game_status(self):
        """Проверяет, что игра начинается в статусе 'ongoing'."""
        self.assertEqual(self.game.status, "ongoing")

    def test_threefold_repetition_draw(self):
        """
        Проверяет ничью из-за троекратного повторения позиции.
        Используем простую последовательность: Король ходит туда-сюда,
        пока второй король делает то же самое.
        """
        # 1. Сделаем несколько начальных ходов, чтобы уйти от стартовой позиции
        self.game.make_move("e2e4")
        self.game.make_move("e7e5")

        # 2. Теперь начинаем повторять ходы
        # Последовательность, приводящая к одной и той же позиции после 4 полуходов
        moves_to_repeat = ["e1e2", "e8e7", "e2e1", "e7e8"]

        # 1-й раз достигаем целевой позиции
        for move in moves_to_repeat:
            self.game.make_move(move)
        
        # Получаем хэш повторяемой позиции для отладки
        target_position_hash = self.game.board.get_position_hash()
        self.assertEqual(self.game.position_history[target_position_hash], 1, "Позиция должна встретиться 1 раз")
        self.assertEqual(self.game.status, "ongoing", "Игра должна продолжаться после 1-го повторения")

        # 2-й раз достигаем целевой позиции
        for move in moves_to_repeat:
            self.game.make_move(move)
            
        self.assertEqual(self.game.position_history[target_position_hash], 2, "Позиция должна встретиться 2 раза")
        self.assertEqual(self.game.status, "ongoing", "Игра должна продолжаться после 2-го повторения")

        # 3-й раз достигаем целевой позиции
        for move in moves_to_repeat:
            self.game.make_move(move)

        # После последнего хода 'e7e8' позиция повторилась в 3-й раз
        self.assertEqual(self.game.position_history[target_position_hash], 3, "Позиция должна встретиться 3 раза")
        # И статус игры должен измениться на ничью
        self.assertEqual(self.game.status, "draw_repetition", "Должна быть ничья по троекратному повторению")

    def test_50_move_rule_draw(self):
        """
        Проверяет ничью по правилу 50 ходов, двигая двух коней по разным углам доски.
        """
        self.game.board.board = [
            ['.', '.', '.', '.', 'k', '.', '.', '.'], # e8
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', 'n'], # h2
            ['.', 'N', '.', '.', 'K', '.', '.', '.']  # b1, e1
        ]
        self.game.board.halfmove_clock = 0
        self.game.position_history.clear()
        self.game.position_history[self.game.board.get_position_hash()] += 1

        for _ in range(49):
            self.assertTrue(self.game.make_move("b1c3"), "Ход белого коня должен быть успешен")
            self.assertTrue(self.game.make_move("h2g4"), "Ход черного коня должен быть успешен")
            self.assertTrue(self.game.make_move("c3b1"), "Ход белого коня назад должен быть успешен")
            self.assertTrue(self.game.make_move("g4h2"), "Ход черного коня назад должен быть успешен")
        
        self.setUp()
        
        for i in range(49):
            # Белые
            if i % 2 == 0: self.assertTrue(self.game.make_move("g1f3"))
            else: self.assertTrue(self.game.make_move("f3g1"))
            # Черные
            if i % 2 == 0: self.assertTrue(self.game.make_move("b8c6"))
            else: self.assertTrue(self.game.make_move("c6b8"))
            
        self.assertEqual(self.game.board.halfmove_clock, 98)
        self.assertEqual(self.game.status, "ongoing")

        # 99-й ход
        self.game.make_move("g1f3")
        self.assertEqual(self.game.board.halfmove_clock, 99)
        
        # 100-й ход - вызывает ничью
        self.game.make_move("b8c6")
        self.assertEqual(self.game.board.halfmove_clock, 100)
        self.assertEqual(self.game.status, "draw_50_moves")

    def test_insufficient_material_draw_scenarios(self):
        """Проверяет ничьи из-за недостаточного материала."""
        scenarios = {
            "K_vs_k": [
                ['.', '.', '.', '.', 'k', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', 'K', '.', '.', '.']
            ],
            "K_vs_kB": [
                ['.', '.', '.', '.', 'k', '.', 'b', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', 'K', '.', '.', '.']
            ],
            "K_vs_kN": [
                ['.', '.', 'n', '.', 'k', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', 'K', '.', '.', '.']
            ]
        }

        for name, board_layout in scenarios.items():
            with self.subTest(scenario=name):
                # Устанавливаем позицию вручную
                self.game.board.board = board_layout
                # Сбрасываем историю и делаем один ход, чтобы запустить проверку
                self.game.position_history.clear()
                self.game.status = "ongoing"
                self.game.make_move("e1d1") # Просто ход королем
                
                self.assertEqual(self.game.status, "draw_insufficient_material")
    
    def test_insufficient_material_draw_scenarios(self):
        """Проверяет ничьи из-за недостаточного материала."""
        scenarios = {
            "K_vs_k": [
                ['.', '.', '.', '.', 'k', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', 'K', '.', '.', '.']
            ],
            "K_vs_kB": [
                ['.', '.', '.', '.', 'k', '.', 'b', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', 'K', '.', '.', '.']
            ],
            "K_vs_kN": [
                ['.', '.', 'n', '.', 'k', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', 'K', '.', '.', '.']
            ]
        }

        for name, board_layout in scenarios.items():
            with self.subTest(scenario=name):
                # Устанавливаем позицию вручную
                self.game.board.board = board_layout
                # Сбрасываем историю и делаем один ход, чтобы запустить проверку
                self.game.position_history.clear()
                self.game.status = "ongoing"
                self.game.make_move("e1d1") # Просто ход королем
                
                self.assertEqual(self.game.status, "draw_insufficient_material")
    
    def test_sufficient_material_no_draw(self):
        """Проверяет, что игра продолжается, когда материала достаточно."""
        # Позиция: K+P vs k. Мат возможен.
        self.game.board.board = [
            ['.', '.', '.', '.', 'k', '.', '.', '.'],
            ['.', '.', '.', 'P', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', 'K', '.', '.', '.']
        ]
        self.game.make_move("e1d2")
        self.assertEqual(self.game.status, "ongoing")


if __name__ == '__main__':
    unittest.main()
