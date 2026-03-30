import pygame
import sqlite3
from .state import State
from .button import Button, BackButton

class Leaderboard(State):
    def __init__(self, state_manager):
        super().__init__(state_manager)

        button_width = 200
        button_height = 30
        start_x = 50
        spacing = 250
        self.font = pygame.font.Font('Fonts/Formula1-Bold.otf', 13)

        self.buttons.append(Button("Sort by Wins", self.font, (175, 0, 200), start_x, 10, button_width, button_height, self.sort_by_wins))
        self.buttons.append(Button("Sort by Games Played", self.font, (175, 0, 200), start_x + button_width + spacing, 10, button_width, button_height, self.sort_by_games_played))
        self.buttons.append(Button("Sort by Win Ratio", self.font, (175, 0, 200), start_x + 2 * (button_width + spacing), 10, button_width, button_height, self.sort_by_win_ratio))

        self.buttons.append(BackButton(state_manager))

        self.current_sort_method = self.sort_by_wins

    def get_user_stats(self, order_by="gamesWon DESC, gamesPlayed ASC"):
        db_path = 'Database/game.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(f'''
            SELECT userinfo.username, userstats.gamesPlayed, userstats.gamesWon, userstats.gamesDrawn, userstats.gamesLoss
            FROM userstats
            INNER JOIN userinfo ON userstats.userId = userinfo.userId
            WHERE userstats.gamesPlayed > 0
            ORDER BY {order_by}
            LIMIT 8;
        ''')

        rows = cursor.fetchall()
        conn.close()

        ranked_data = []
        rank = 1
        for row in rows:
            username, games_played, games_won, games_drawn, games_lost = row
            ranked_row = (rank, username, games_played, games_won, games_drawn, games_lost)
            ranked_data.append(ranked_row)
            rank += 1

        return ranked_data

    def sort_by_wins(self):
        self.current_sort_method = self.sort_by_wins
        self.draw(self.state_manager.screen)

    def sort_by_games_played(self):
        self.current_sort_method = self.sort_by_games_played
        self.draw(self.state_manager.screen)

    def sort_by_win_ratio(self):
        self.current_sort_method = self.sort_by_win_ratio
        self.draw(self.state_manager.screen)

    def draw_table(self, window, data):
        font = self.state_manager.main_font_instructions
        table_top_left = (50, 50)
        cell_width = 200
        cell_height = 50
        padding = 14

        column_headers = ["Rank", "Username", "Games Played", "Games Won", "Games Drawn", "Games Lost"]

        x_pos = table_top_left[0]
        y_pos = table_top_left[1]

        for header in column_headers:
            text = font.render(header, True, (255, 255, 255))
            window.blit(text, (x_pos + padding, y_pos + padding))
            x_pos += cell_width

        y_pos += cell_height

        for row in data:
            x_pos = table_top_left[0]
            for cell in row:
                text = font.render(str(cell), True, (255, 255, 255))
                window.blit(text, (x_pos + padding, y_pos + padding))
                x_pos += cell_width
            y_pos += cell_height

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.buttons:
                if button.is_clicked(mouse_pos):
                    button.perform_action()

    def draw(self, screen):
        screen.fill((175, 0, 52))

        if self.current_sort_method == self.sort_by_games_played:
            user_stats = self.get_user_stats(order_by="gamesPlayed DESC")
        elif self.current_sort_method == self.sort_by_win_ratio:
            user_stats = self.get_user_stats(order_by="(gamesWon * 1.0 / gamesPlayed) DESC, gamesPlayed ASC")
        else:
            user_stats = self.get_user_stats(order_by="gamesWon DESC, gamesPlayed DESC")

        self.draw_table(screen, user_stats)

        for button in self.buttons:
            button.draw(screen)

        pygame.display.update()

