import random
import pygame
import pandas as pd
import pandasql as psql
from states.play_friend import PlayFriend

class PlayAI(PlayFriend):
    def __init__(self, state_manager, user_id, difficulty):
        super().__init__(state_manager, user_id)
        self.bot_player = "O"
        self.bot_active = False
        self.difficulty = difficulty 
   

    def handle_events(self, event):
        super().handle_events(event)
        if not self.game_over and self.current_player == self.bot_player and not self.bot_active:
            self.bot_active = True
            self.bot_move()
            self.bot_active = False

    def bot_move(self):
        available_moves = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]
        if available_moves:
            move = self.choose_move(available_moves)
            row, col = move
            self.board[row][col] = self.bot_player
            self.moves_count += 1  
            if self.check_winner():
                self.result_text = f"{self.bot_player} wins!"
                self.placeholder_text = f"Player {self.bot_player} has won!"
                self.game_over = True
                self.update_user_stats(lost=True)
                self.save_game_result('loss')
            elif self.check_draw():
                self.result_text = "It's a draw!"
                self.placeholder_text = "The game ended as a draw."
                self.game_over = True
                self.update_user_stats(draw=True)
                self.save_game_result('draw')
            else:
                self.current_player = "X"
            self.result_text = "Bot has made its move."
        
        
        if self.game_over:
            self.return_home_button.visible = True

    def choose_move(self, available_moves):
        if self.difficulty == 'easy':
            return self.easy_bot_move(available_moves)
        elif self.difficulty == 'medium':
            return self.medium_bot_move(available_moves)
        elif self.difficulty == 'hard':
            return self.hard_bot_move(available_moves)

    def easy_bot_move(self, available_moves):
        if random.random() < 0.4:  # 40% chance of making a correct move
            return self.find_best_move(available_moves)
        else:
            return random.choice(available_moves)

    def medium_bot_move(self, available_moves):
        if random.random() < 0.7:  # 70% chance of making a correct move
            return self.minimax(available_moves)
        else:
            return random.choice(available_moves)

    def hard_bot_move(self, available_moves):
        return self.minimax(available_moves)

    def find_best_move(self, available_moves):
        # Simplified move for easy bot
        for move in available_moves:
            row, col = move
            self.board[row][col] = self.bot_player
            if self.check_winner():
                self.board[row][col] = ""
                return move
            self.board[row][col] = ""
        for move in available_moves:
            row, col = move
            self.board[row][col] = "X"
            if self.check_winner():
                self.board[row][col] = ""
                return move
            self.board[row][col] = ""
        return random.choice(available_moves)

    def minimax(self, available_moves):
        best_score = -float('inf')
        best_move = None
        for move in available_moves:
            row, col = move
            self.board[row][col] = self.bot_player
            score = self.minimax_score(False)
            self.board[row][col] = ""
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def minimax_score(self, is_maximising):
        if self.check_winner() == self.bot_player:
            return 1
        elif self.check_winner() == "X":
            return -1
        elif self.check_draw():
            return 0

        if is_maximising:
            best_score = -float('inf')
            for move in [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]:
                row, col = move
                self.board[row][col] = self.bot_player
                score = self.minimax_score(False)
                self.board[row][col] = ""
                best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for move in [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]:
                row, col = move
                self.board[row][col] = "X"
                score = self.minimax_score(True)
                self.board[row][col] = ""
                best_score = min(score, best_score)
            return best_score

    def handle_click(self, pos):
        if self.game_over or self.current_player != "X":
            return

        # Calculate the cell that was clicked
        col = (pos[0] - self.board_x) // (self.board_size // 3)
        row = (pos[1] - self.board_y) // (self.board_size // 3)

        # Ensure the click is within the board boundaries
        if 0 <= row < 3 and 0 <= col < 3:
            if self.board[row][col] == "":
                self.current_cell = (row, col)
                constructor_name = self.row_labels[row]
                col_label = self.col_labels[col]
                if col_label in self.nationalities.values():
                    self.question_text = f'Please enter a {col_label} driver who has driven for {constructor_name}:'
                else:
                    self.question_text = f'Please enter a driver who is a {col_label.lower()} and has driven for {constructor_name}:'
                self.input_box.active = True

    def check_input(self):
        if self.current_cell is not None:
            row, col = self.current_cell
            constructor_name = self.row_labels[row]
            col_label = self.col_labels[col]
            driver_guess = self.input_box.get_text().strip().title()
            south_american_filter = " OR ".join([f"drivers.nationality = '{country}'" for country in self.south_american_countries])
            red_bull_teams_filter = " OR ".join([f"constructors.name = '{team}'" for team in ['Red Bull', 'Toro Rosso', 'AlphaTauri', 'Jaguar']])

            query = ""

            # Define conditions for various column labels
            driver_condition = ""
            if col_label in self.nationalities.values():
                driver_condition = f"drivers.nationality = '{col_label}'"
            elif col_label == 'Fastest Lap':
                driver_condition = "drivers.driverid IN (SELECT DISTINCT driverid FROM results WHERE rank = 1)"
            elif col_label == 'Pole Position':
                driver_condition = "drivers.driverid IN (SELECT DISTINCT driverid FROM qualifying WHERE position = 1)"
            elif col_label == 'Race Winner':
                driver_condition = "drivers.driverid IN (SELECT DISTINCT driverid FROM results WHERE position = 1)"
            elif col_label == 'Podium Finish':
                driver_condition = "drivers.driverid IN (SELECT DISTINCT driverid FROM results WHERE position BETWEEN 1 AND 3)"
            elif col_label == 'World Champion':
                driver_condition = """
                drivers.driverid IN (
                    SELECT final_standings.driverid
                    FROM driver_standings AS final_standings
                    INNER JOIN (
                        SELECT races.year, MAX(races.round) AS last_round
                        FROM races
                        GROUP BY races.year 
                    ) AS last_race_per_year
                    ON final_standings.raceid = (
                        SELECT raceid
                        FROM races
                        WHERE races.year = last_race_per_year.year AND races.round = last_race_per_year.last_round
                    )
                    WHERE final_standings.position = 1
                )
                """
            elif col_label == 'South American':
                driver_condition = f"({south_american_filter})"

            #base query
            query = f"""
            SELECT DISTINCT drivers.surname
            FROM results
            INNER JOIN drivers ON results.driverid = drivers.driverid
            INNER JOIN constructors ON results.constructorid = constructors.constructorid
            WHERE {driver_condition}
            AND constructors.name = '{constructor_name}';
            """

            # Special cases for constructor groups
            if constructor_name == 'Red Bull Teams + Jaguar':
                query = query.replace(f"constructors.name = '{constructor_name}'", f"({red_bull_teams_filter})")
            elif constructor_name == 'Renault + Alpine':
                # Replace with conditions specific to Renault and Alpine
                query = query.replace(
                    f"constructors.name = '{constructor_name}'",
                    f"""
                    (constructors.name = 'Renault' AND {driver_condition})
                    OR
                    (constructors.name = 'Alpine' AND {driver_condition})
                    """
                )

            # Execute the query with the correct context
            local_tables = {
                'drivers': self.drivers,
                'constructors': self.constructors,
                'results': self.results,
                'driver_standings': self.driver_standings,
                'qualifying': self.qualifying,
                'races': self.races
            }
            result = psql.sqldf(query, local_tables)

            if driver_guess in result['surname'].values:
                self.board[row][col] = self.current_player
                self.moves_count += 1  
                if self.check_winner():
                    self.result_text = f"{self.current_player} wins!"
                    self.placeholder_text = f"Player {self.current_player} has won!"
                    self.game_over = True
                    if self.current_player == "X":
                        self.update_user_stats(won=True)
                        self.save_game_result('win')
                    else:
                        self.update_user_stats(lost=True)
                        self.save_game_result('loss')
                elif self.check_draw():
                    self.result_text = "It's a draw!"
                    self.placeholder_text = "The game ended as a draw."
                    self.game_over = True
                    self.update_user_stats(draw=True)
                    self.save_game_result('draw')
                else:
                    self.current_player = self.bot_player
                self.result_text = f"Correct! {driver_guess} has met the criteria."
            else:
                self.result_text = f"Incorrect. {driver_guess} does not meet the criteria."
                self.current_player = self.bot_player

            self.input_box.text = ''
            self.input_box.active = False
            self.current_cell = None

            # Update the question text based on the new state of the game
            if not self.game_over:
                self.question_text = f"Click on a square to make a move."
            else:
                self.return_home_button.visible = True

    
    def draw(self, screen):
        super().draw(screen)
        self.draw_board(screen)
        self.draw_marks(screen)
        question_surface = self.font.render(self.question_text, True, self.text_colour)
        screen.blit(question_surface, (20, 20))
        result_surface = self.font.render(self.result_text, True, self.text_colour)
        screen.blit(result_surface, (20, 60))
        self.input_box.draw(screen)

        label_font = pygame.font.Font('Fonts/Formula1-Regular.otf', 24)
        label_surface = label_font.render('Driver Surname:', True, self.text_colour)
        screen.blit(label_surface, (20, 110)) 
        
        
        
        self.skip_go_button.draw(screen)
       
        self.draw_current_player(screen)

        self.draw_placeholder_text(screen)

        if self.game_over:
            self.return_home_button.draw(screen)
        
       
            
    def return_home(self):
        self.state_manager.pop_state()
        self.state_manager.pop_state()

    def update_timer(self):
        pass

    def draw_timer(self,screen):
        pass