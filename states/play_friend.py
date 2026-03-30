import random, time, sqlite3, pygame
import pandas as pd
import pandasql as psql
from states.state import State
from states.textbox import TextBox
from states.button import Button


class PlayFriend(State):
    def __init__(self, state_manager, user_id):
        super().__init__(state_manager)
        self.user_id = user_id
        self.start_time = time.time()
        self.moves_count = 0
        self.board = self.create_board()
        self.current_player = "X"
        self.game_over = False
        self.screen_width, self.screen_height = 1200, 600
        self.board_size = 300
        self.grid_colour = pygame.Color('black')
        self.x_colour = pygame.Color('white')
        self.o_colour = pygame.Color('red')
        self.bg_colour = pygame.Color((175, 0, 52))
        self.text_colour = pygame.Color('white')
        self.line_width = 10
        self.board_x = (self.screen_width - self.board_size) // 2
        self.board_y = (self.screen_height - self.board_size) // 2
        self.font = pygame.font.Font('Fonts/Formula1-Bold.otf', 13)

        # Load database tables
        table_names = {
            'drivers': 'drivers',
            'constructors': 'constructors',
            'results': 'results',
            'driver_standings': 'driver_standings',
            'qualifying': 'qualifying',
            'races': 'races'
        }
        conn = sqlite3.connect(r"F1_data\stats.db")
        self.drivers = pd.read_sql(f"SELECT * FROM {table_names['drivers']}", conn)
        self.constructors = pd.read_sql(f"SELECT * FROM {table_names['constructors']}", conn)
        self.results = pd.read_sql(f"SELECT * FROM {table_names['results']}", conn)
        self.driver_standings = pd.read_sql(f"SELECT * FROM {table_names['driver_standings']}", conn)
        self.qualifying = pd.read_sql(f"SELECT * FROM {table_names['qualifying']}", conn)
        self.races = pd.read_sql(f"SELECT * FROM {table_names['races']}", conn)

        conn.close()

        # Game condition dictionaries
        self.teams = {
            1: 'Ferrari',
            2: 'McLaren',
            3: 'Renault + Alpine',
            4: 'Red Bull Teams + Jaguar',
            5: 'Williams'
        }

        self.nationalities = {
            1: 'French',
            2: 'British',
            3: 'Spanish',
            4: 'German',
           }

        self.achievements = {
            1: 'Race Winner',
            2: 'World Champion',
            3: 'Pole Position',
            4: 'Podium Finish',
            5: 'Fastest Lap',
            6: 'South American'
        }

        # Ensure unique selection for teams and criteria (nationalities and achievements)
        teams_list = list(self.teams.values())
        criteria_list = list(self.nationalities.values()) + list(self.achievements.values())
        random.shuffle(teams_list)
        random.shuffle(criteria_list)

        # Select unique row and column labels
        self.row_labels = teams_list[:3]
        self.col_labels = criteria_list[:3]

        # Set up input for user guesses
        self.input_box = TextBox(self.font, 20, 165, 300, 40, colour=(255, 255, 255), text_colour=(0, 0, 0), border_colour=(0, 0, 0), max_characters=30)
        self.question_text = 'Click on a square to start the game. The signed in player is X and guest is O'
        self.result_text = ''
        self.current_cell = None
        self.answer_text = ''

        # Red Bull and associated teams
        self.south_american_countries = ["Argentine", "Brazilian", "Chilean", "Colombian","Uruguayan", "Venezuelan"]


        
        self.skip_go_button = Button('Skip Go', self.font, (0, 128, 0), 1000, 200, 150, 50, self.skip_go)
        self.end_as_draw_button = Button('End as Draw', self.font, (128, 0, 0), 1000, 100, 150, 50, self.end_as_draw)

        #(hidden initially)
        self.return_home_button = Button('Return to Homepage', self.font, (0, 0, 128), 20, 515 , 250, 50, self.return_home)
        self.return_home_button.visible = False

        
        self.placeholder_text = "Tic Track Toe"
        self.answer_text = ""
        self.timer_start = 20
        self.time_left = self.timer_start
        self.timer_running = True
        self.last_tick = pygame.time.get_ticks()

    def create_board(self):
        return [
            ["", "", ""],
            ["", "", ""],
            ["", "", ""]
        ]

    def draw_board(self, screen):
        screen.fill(self.bg_colour)
        for line_num in range(1, 3):
            horizontal_start_pos = (self.board_x, self.board_y + line_num * self.board_size // 3)
            horizontal_end_pos = (self.board_x + self.board_size, self.board_y + line_num * self.board_size // 3)
            pygame.draw.line(screen, self.grid_colour, horizontal_start_pos, horizontal_end_pos, self.line_width)
            vertical_start_pos = (self.board_x + line_num * self.board_size // 3, self.board_y)
            vertical_end_pos = (self.board_x + line_num * self.board_size // 3, self.board_y + self.board_size)
            pygame.draw.line(screen, self.grid_colour, vertical_start_pos, vertical_end_pos, self.line_width)
        self.draw_labels(screen)

    def draw_marks(self, screen):
        font = pygame.font.Font(None, 144)
        for row in range(3):
            for col in range(3):
                mark = self.board[row][col]
                if mark != "":
                    x_pos = self.board_x + col * self.board_size // 3 + self.board_size // 6
                    y_pos = self.board_y + row * self.board_size // 3 + self.board_size // 6
                    if mark == "X":
                        colour = self.x_colour
                    else:
                        colour = self.o_colour
                    text = font.render(mark, True, colour)
                    text_rect = text.get_rect(center=(x_pos, y_pos))
                    screen.blit(text, text_rect)


    def draw_labels(self, screen):
        row_label_x_offset = 100  # Offset for row labels
        col_label_y_offset = 40  # Offset for column labels

        for row in range(len(self.row_labels)):
            label = self.row_labels[row]
            if label == 'Red Bull Teams + Jaguar':
                formatted_label = 'Red Bull Teams\n+ Jaguar'
                lines = formatted_label.split('\n')
            elif label == 'Renault + Alpine':
                formatted_label = 'Renault\n+ Alpine'
                lines = formatted_label.split('\n')
            else:
                lines = [label]

            for line_idx in range(len(lines)):
                line = lines[line_idx]
                if len(line) > 10:  # If the label is long, use a smaller font
                    row_label_font = pygame.font.Font('Fonts/Formula1-Bold.otf', 12)
                else:
                    row_label_font = self.font

                row_label = row_label_font.render(line, True, self.text_colour)
                label_x = self.board_x - row_label_x_offset  # Adjusted position for row labels
                label_y = self.board_y + row * self.board_size // 3 + self.board_size // 6 - row_label.get_height() // 2 + line_idx * row_label.get_height()
                screen.blit(row_label, (label_x, label_y))

        for col in range(len(self.col_labels)):
            label = self.col_labels[col]
            if len(label) > 10:  # If the label is long, use a smaller font
                col_label_font = pygame.font.Font('Fonts/Formula1-Bold.otf', 10)
                label_y_adjustment = col_label_y_offset
            else:
                col_label_font = self.font
                label_y_adjustment = col_label_y_offset

            col_label = col_label_font.render(label, True, self.text_colour)
            label_x = self.board_x + col * self.board_size // 3 + self.board_size // 6 - col_label.get_width() // 2
            label_y = self.board_y - label_y_adjustment  
            screen.blit(col_label, (label_x, label_y))



    def check_winner(self):
        for row in range(3):
            if self.board[row][0] == self.board[row][1] == self.board[row][2] != "":
                return self.board[row][0]
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != "":
                return self.board[0][col]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != "":
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != "":
            return self.board[0][2]
        return None

    def check_draw(self):
        for row in self.board:
            for cell in row:
                if cell == "":
                    return False
        return True

    def reset_board(self):
        self.board = self.create_board()
        self.current_player = "X"
        self.game_over = False
        self.question_text = 'Click on a square to start the game. The signed in player is X and guest is O'
        self.result_text = ''
        self.placeholder_text = "Tic Track Toe"
        self.answer_text = ''
        self.start_time = time.time()  # Reset the start time
        self.moves_count = 0  


    def handle_events(self, event):
        super().handle_events(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.skip_go_button.is_clicked(mouse_pos):
                self.skip_go_button.perform_action()
            elif self.end_as_draw_button.is_clicked(mouse_pos):
                self.end_as_draw_button.perform_action()
            elif self.return_home_button.visible and self.return_home_button.is_clicked(mouse_pos):
                self.return_home_button.perform_action()
            else:
                self.handle_click(mouse_pos)
                
        self.input_box.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.check_input()
        

    def handle_click(self, pos):
        if self.game_over:
            return
        if self.board_x <= pos[0] <= self.board_x + self.board_size and self.board_y <= pos[1] <= self.board_y + self.board_size:
            col = (pos[0] - self.board_x) // (self.board_size // 3)
            row = (pos[1] - self.board_y) // (self.board_size // 3)
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
            driver_guess = self.input_box.get_text().strip().title() #Get the user's input and update it to fix database format

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

            #Execute the query with the correct context
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
                    self.current_player = "O" if self.current_player == "X" else "X"
                self.result_text = f"Correct! {driver_guess} has met the criteria."
            else:
                self.moves_count += 1 
                self.result_text = f"Incorrect. {driver_guess} does not meet the criteria."
                self.current_player = "O" if self.current_player == "X" else "X"
                #answer = result['surname'].values
                #self.answer_text = "Possible answers:\n" + "\n".join(str(ans) for ans in answer[:3])



            self.input_box.text = ''
            self.input_box.active = False
            self.current_cell = None

            if not self.game_over:
                self.question_text = f"Click on a square to make a move."
                self.reset_timer()
            else:
                self.return_home_button.visible = True


    def save_game_result(self, result):
        game_duration = int(time.time() - self.start_time)
        conn = sqlite3.connect('Database/game.db')
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO gamesaves (userId, gameResult, gameDuration, movesCount)
            VALUES (?, ?, ?, ?)
        """, (self.user_id, result, game_duration, self.moves_count))

        conn.commit()
        conn.close()

    def update_user_stats(self, won=False, lost=False, draw=False):
            conn = sqlite3.connect('Database/game.db')
            cursor = conn.cursor()

            cursor.execute("""
                SELECT gamesPlayed, gamesWon, gamesLoss, gamesDrawn FROM userstats WHERE userId = ?
            """, (self.user_id,))
            stats = cursor.fetchone()

            if stats:
                games_played, games_won, games_lost, games_drawn = stats
                games_played += 1
                if won:
                    games_won += 1
                if lost:
                    games_lost += 1
                if draw:
                    games_drawn += 1

                cursor.execute("""
                    UPDATE userstats
                    SET gamesPlayed = ?, gamesWon = ?, gamesLoss = ?, gamesDrawn = ?
                    WHERE userId = ?
                """, (games_played, games_won, games_lost, games_drawn, self.user_id))
            else:
                games_played = 1
                games_won = 1 if won else 0
                games_lost = 1 if lost else 0
                games_drawn = 1 if draw else 0

                cursor.execute("""
                    INSERT INTO userstats (userId, gamesPlayed, gamesWon, gamesLoss, gamesDrawn)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.user_id, games_played, games_won, games_lost, games_drawn))

            conn.commit()
            conn.close()



    def skip_go(self):
        if not self.game_over:
            self.current_player = "O" if self.current_player == "X" else "X"
            self.result_text = f"{self.current_player}'s turn has been skipped. Click on a square to make a move."
            self.reset_timer()

    def end_as_draw(self):
        if not self.game_over:
            self.game_over = True
            self.result_text = "The game has been ended as a draw."
            self.placeholder_text = "The game ended as a draw."
            self.update_user_stats(draw=True)
            self.save_game_result('draw')
            self.return_home_button.visible = True
            self.timer_running = False

    def draw_current_player(self, screen):
        current_player_text = f"Player {self.current_player}'s Go"
        font = pygame.font.Font('Fonts/Formula1-Bold.otf', 24)
        text_surface = font.render(current_player_text, True, self.text_colour)
        text_rect = text_surface.get_rect(topright=(self.screen_width - 20, 20))
        screen.blit(text_surface, text_rect)

    def draw_placeholder_text(self, screen):
        font = pygame.font.Font('Fonts/Formula1-Bold.otf', 40)
        text_surface = font.render(self.placeholder_text, True, self.text_colour)
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 60))
        screen.blit(text_surface, text_rect)

    def update_timer(self):
        if self.timer_running and not self.game_over:
            current_time = pygame.time.get_ticks()
            elapsed_time = (current_time - self.last_tick) / 1000  # Convert milliseconds to seconds
            
            if elapsed_time >= 1:  # One second has passed
                self.time_left -= 1
                self.last_tick = current_time
            
            if self.time_left <= 0:
                self.skip_go() 
                self.reset_timer()

    def reset_timer(self):
        self.time_left = self.timer_start
        self.last_tick = pygame.time.get_ticks()

    def draw_timer(self, screen):
        if not self.game_over:
            font = pygame.font.Font('Fonts/Formula1-Regular.otf', 36)
            timer_text = f"Time Left : {self.time_left}s"
            text_surface = font.render(timer_text, True, self.text_colour)
            text_rect = text_surface.get_rect(bottomleft=(20, self.screen_height - 60))
            screen.blit(text_surface, text_rect)

    def draw(self, screen):
        super().draw(screen)
        self.draw_board(screen)
        self.draw_marks(screen)
        question_surface = self.font.render(self.question_text, True, self.text_colour)
        screen.blit(question_surface, (20, 20))
        result_surface = self.font.render(self.result_text, True, self.text_colour)
        screen.blit(result_surface, (20, 60))
        answer_surface = self.font.render(self.answer_text, True, self.text_colour)
        screen.blit(answer_surface, (20,250))
        label_font = pygame.font.Font('Fonts/Formula1-Regular.otf', 24)
        label_surface = label_font.render('Driver Surname:', True, self.text_colour)
        screen.blit(label_surface, (20, 110)) 
        #answer_surface = self.font.render(self.answer_text, True, self.text_colour)
        #screen.blit(answer_surface, (20,20))
        
        self.input_box.draw(screen)
        
        self.skip_go_button.draw(screen)
        self.end_as_draw_button.draw(screen)

        self.draw_current_player(screen)

        self.draw_placeholder_text(screen)

        if self.game_over:
            self.return_home_button.draw(screen)

        self.draw_timer(screen)
    
    def return_home(self):
        self.state_manager.pop_state()
    


    