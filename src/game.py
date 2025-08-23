import collections
from src.board import ChessBoard

class Game:
    """
    Управляет течением шахматной партии.
    Хранит историю позиций и определяет результат игры.
    """
    def __init__(self):
        self.board = ChessBoard()
        # Используем Counter для удобного подсчета одинаковых позиций
        self.position_history = collections.Counter()
        self.status = "ongoing"
        self._update_history() # Записываем начальную позицию

    def _update_history(self):
        """Обновляет историю позиций для проверки на троекратное повторение."""
        pos_hash = self.board.get_position_hash()
        self.position_history[pos_hash] += 1

    def make_move(self, move_str):
        """
        Пытается сделать ход. Если успешно, обновляет историю и проверяет конец игры.
        """
        success = self.board.make_move(move_str)
        if success:
            self._update_history()
            self.check_game_over() # Обновляем статус игры после каждого хода
        return success

    def undo_move(self):
        """
        Отменяет последний ход, откатывая и доску, и историю позиций.
        """
        # Сначала уменьшаем счетчик текущей позиции
        current_hash = self.board.get_position_hash()
        if self.position_history[current_hash] > 0:
            self.position_history[current_hash] -= 1
        
        # Затем откатываем саму доску
        return self.board.undo_move()

    
    def check_game_over(self):
        """
        Проверяет все условия окончания игры, включая троекратное повторение.
        """
        # Сначала проверяем условия, которые знает сама доска (мат, пат, 50 ходов)
        board_status = self.board.is_game_over()
        if board_status != "ongoing":
            self.status = board_status
            return self.status

        # Теперь проверяем условие, которое знает только класс Game
        current_hash = self.board.get_position_hash()
        if self.position_history[current_hash] >= 3:
            self.status = "draw_repetition"
            return self.status
            
        self.status = "ongoing"
        return self.status