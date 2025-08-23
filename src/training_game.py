from src.game import Game
from src.ai_player import AIPlayer

class TrainingGame(Game):
    """
    Класс для тренировочной игры с подсказками и анализом.
    Наследуется от обычного класса Game.
    """
    def __init__(self, ai_skill_level=15):
        super().__init__()
        
        self.analyzer = AIPlayer(skill_level=ai_skill_level)
        if not self.analyzer.engine:
            self.analyzer = None

    def get_top_moves(self, num_moves=3):
        if not self.analyzer:
            return None
        
        current_fen = self.board.to_fen()
        return self.analyzer.get_analysis(current_fen, num_lines=num_moves, time_limit=1.0)
    
    def shutdown_analyzer(self):
        if self.analyzer:
            self.analyzer.quit()

