import chess
# Мы импортируем родительский класс, чтобы расширить его
from game_vs_stockfish import GameVsStockfish

class GameWithHints(GameVsStockfish):
    """
    Расширенная версия игры, которая наследуется от стандартной игры
     и добавляет команды 'undo' (отменить ход) и 'hint' (попросить подсказку).
    """
    def __init__(self, player_color: str, skill_level: int, lang: str = "ru"):
        # Вызываем конструктор родительского класса, чтобы он сделал всю базовую настройку
        super().__init__(player_color, skill_level, lang)
        # Немного изменим время поиска для режима подсказок, чтобы он был быстрым
        self.engine.search_time = 0.5 

    def _player_turn(self) -> bool:
        """
        Переопределяет родительский метод _player_turn.
        Эта версия обрабатывает дополнительные команды.
        Возвращает False, если игрок решил выйти из игры.
        """
        while True:
            try:
                # Используем специальную строку-приглашение для этого режима
                prompt = self.localizer.get("your_move_prompt_hints")
                user_input = input(prompt).strip().lower()

                # Команда выхода
                if user_input == self.localizer.get("exit_command"):
                    save_prompt = self.localizer.get("save_and_quit_prompt")
                    save_choice = input(save_prompt).lower()
                    if save_choice == self.localizer.get("confirm_yes"):
                        return False # Сигнал для выхода с сохранением
                    else:
                        self.board.halfmove_clock = 9999
                        return True
                
                # --- НОВАЯ ЛОГИКА ЗДЕСЬ ---
                # Команда отмены хода
                elif user_input == self.localizer.get("command_undo"):
                    if len(self.board.history) >= 2:
                        # Отменяем ход ИИ и ход игрока (всего два хода)
                        self.board.undo_move()
                        self.board.undo_move()
                        self.last_move = None # Сбрасываем подсветку
                        # Выходим из _player_turn, чтобы главный цикл перерисовал доску
                        return True 
                    else:
                        print("\nНедостаточно ходов для отмены.")
                        input() # Пауза, чтобы пользователь увидел сообщение
                        return True


                # Команда подсказки
                elif user_input == self.localizer.get("command_hint"):
                    self._show_hints()
                    # После подсказки мы остаемся в цикле, чтобы игрок мог сделать ход
                    continue # Пропускаем остаток цикла и снова запрашиваем ввод

                # Если это не команда, пытаемся обработать как обычный ход
                else:
                    move = self._parse_user_input(user_input)
                    if move in self.board.get_legal_moves():
                        self.board.make_move(move)
                        self.last_move = move
                        return True # Ход сделан, выходим из _player_turn
                    else:
                        print(self.localizer.get("illegal_move"))

            except ValueError as e:
                print(self.localizer.get("input_error", error=e))

    def _show_hints(self):
        """Запрашивает у движка и выводит 3 лучших хода."""
        print(self.localizer.get("ai_thinking"))
        # Используем FEN конвертер
        # Мы можем импортировать его прямо здесь, чтобы избежать циклических зависимостей на уровне модуля
        try:
            from main import board_to_fen
        except ImportError:
            # Если запускаем не из main, например в тестах, нужен запасной вариант
            from game_vs_stockfish import board_to_fen

        current_fen = board_to_fen(self.board)
        lib_board = chess.Board(current_fen)
        
        print("\n" + self.localizer.get("hint_header"))
        try:
            # --- ИСПРАВЛЕННАЯ ЛОГИКА ---
            # Устанавливаем multipv (количество вариантов) и лимит по времени
            # Метод .analyse() ждет завершения и возвращает список всех найденных вариантов
            info = self.engine.engine.analyse(
                lib_board, 
                chess.engine.Limit(time=self.engine.search_time), 
                multipv=3
            )

            # Теперь `info` - это список словарей, отсортированный по качеству хода
            if not info:
                print("  Не удалось получить варианты от движка.")
            
            # Выводим только первые 3 (или меньше, если движок нашел меньше)
            for i, move_info in enumerate(info):
                if "pv" in move_info and move_info["pv"]:
                    # Основной вариант (Principal Variation)
                    move = move_info["pv"][0] 
                    # Оценка позиции
                    score = move_info["score"].relative
                    # Преобразуем оценку в более понятный формат (сантипешки в очки)
                    score_points = score.score() / 100.0 if score.score() is not None else "Мат"
                    
                    print(f"  {i+1}. Ход: {move.uci()}, Оценка: {score_points:+.2f}")
                else:
                    break # Если вариантов больше нет, выходим

        except Exception as e:
            print(f"Не удалось получить подсказки: {e}")
            
        print("-" * 40)
        input(self.localizer.get("press_enter_to_continue"))