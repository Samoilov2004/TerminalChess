from src.game import Game
from src.ai_player import AIPlayer

class TrainingGame(Game):
    """
    Класс для тренировочной игры с подсказками и анализом.
    Наследуется от обычного класса Game.
    """
    def __init__(self, ai_skill_level=15):
        # --- НАЧАЛО ИСПРАВЛЕНИЯ ---
        
        # 1. Вызываем конструктор родительского класса Game.
        # Он создаст self.board, self.position_history и все остальные атрибуты.
        super().__init__()
        
        # --- КОНЕЦ ИСПРАВЛЕНИЯ ---
        
        # 2. Теперь добавляем свою, уникальную для TrainingGame логику.
        self.analyzer = AIPlayer(skill_level=ai_skill_level)
        if not self.analyzer.engine:
            self.analyzer = None

    def get_top_moves(self, num_moves=3):
        """Получает лучшие ходы для текущей позиции."""
        if not self.analyzer:
            return None
        
        current_fen = self.board.to_fen()
        analysis_result = self.analyzer.get_analysis(current_fen, num_lines=num_moves, time_limit=0.5)
        
        # Возвращаем результат анализа напрямую
        return analysis_result
    
    def shutdown_analyzer(self):
        """Корректно завершает работу движка."""
        if self.analyzer:
            self.analyzer.quit()