import pygame
import sqlite3
from .button import BackButton
from .state import State

class PlayerStats(State):
    def __init__(self, state_manager, user_id):
        super().__init__(state_manager)
        self.user_id = user_id  # Store the logged-in user's ID
        self.font = state_manager.main_font_instructions  # Use the main instructions font from the state manager
        self.title_font = state_manager.bold_font_title

        # Add a back button
        self.back_button = BackButton(state_manager)

    def get_user_stats(self):
        db_path = 'Database/game.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT userinfo.username, userstats.gamesPlayed, userstats.gamesWon, userstats.gamesLoss, userstats.gamesDrawn
            FROM userstats
            INNER JOIN userinfo ON userstats.userId = userinfo.userId
            WHERE userinfo.userId = ?
        ''', (self.user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return row

    def get_user_game_saves(self):
        db_path = 'Database/game.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT gameResult, gameDuration, movesCount
            FROM gamesaves
            WHERE userId = ?
            ORDER BY saveId DESC
            LIMIT 1
        ''', (self.user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return [row] if row else []

    def draw_table(self, window, data, top_left, column_headers):
        font = self.font
        cell_width = 230
        cell_height = 50
        padding = 10
        x_start, y_start = top_left

        # Draw column headers
        column_index = 0
        for header in column_headers:
            header_text = font.render(header, True, (255, 255, 255))
            header_x = x_start + column_index * cell_width + padding
            header_y = y_start + padding
            window.blit(header_text, (header_x, header_y))
            column_index += 1
        
        # Draw rows of data
        row_index = 0
        for row_data in data:
            column_index = 0
            for cell_data in row_data:
                cell_text = font.render(str(cell_data), True, (255, 255, 255))
                cell_x = x_start + column_index * cell_width + padding
                cell_y = y_start + (row_index + 1) * cell_height + padding
                window.blit(cell_text, (cell_x, cell_y))
                column_index += 1
            row_index += 1


    def draw(self, screen):
        screen.fill((175, 0, 52))  

        # Fetch user stats and draw the table
        user_stats = self.get_user_stats()
        if user_stats:
            title = self.title_font.render("User Stats", True, (255, 255, 255))
            screen.blit(title, (50, 20))
            self.draw_table(screen, [user_stats], (50, 70), ["Username", "Games Played", "Games Won", "Games Lost", "Games Drawn"])
        else:
            error_message = self.font.render("No stats available.", True, (255, 255, 255))
            screen.blit(error_message, (50, 50))

        # Fetch user game saves and draw the table
        user_game_saves = self.get_user_game_saves()
        if user_game_saves:
            title = self.title_font.render("Most Recent Game", True, (255, 255, 255))
            screen.blit(title, (50, 180))
            self.draw_table(screen, user_game_saves, (50, 240), ["Game Result", "Duration (s)", "Moves Count"])
        else:
            error_message = self.font.render("No game saves available.", True, (255, 255, 255))
            screen.blit(error_message, (50, 210))

        # Draw the back button
        self.back_button.draw(screen)
        
        pygame.display.update()

    def update(self):
        pass

    def handle_events(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button.is_clicked(event.pos):
                self.back_button.perform_action()
