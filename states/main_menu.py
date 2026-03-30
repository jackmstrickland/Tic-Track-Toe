import pygame
from states.state import State
from states.button import Button
from states.play_ai import PlayAI
from states.play_friend import PlayFriend #change
from states.instructions import Instructions
from states.player_stats import PlayerStats
from states.leaderboard import Leaderboard
from states.select_difficulty import SelectDifficulty

class MainMenu(State):
    def __init__(self, state_manager):
        super().__init__(state_manager)

        # Load car image
        self.car_image = pygame.image.load('Images/f1icon.png').convert_alpha()
        self.car_image_rect = self.car_image.get_rect(center=(600, 300))

        # Create game name
        self.game_name = state_manager.bold_font.render('Tic Track Toe', False, (255, 255, 238))
        self.game_name_rect = self.game_name.get_rect(center=(600, 100))

        # Create menu buttons horizontally
        button_width = 215
        button_height = 60
        spacing = 20  # Space between buttons
        start_x = (1200 - (5 * button_width + 4 * spacing)) // 2  # Centering the buttons
        #(self, text, font, colour, x, y, width, height, action=None)
        self.buttons.append(Button('Play AI', state_manager.main_font, (255, 30, 0), start_x, 450, button_width, button_height, 
                                   action=self.play_ai))
        self.buttons.append(Button('Play Friend', state_manager.main_font, (255, 30, 0), start_x + button_width + spacing, 450, button_width, button_height, 
                                   action=self.play_friend))
        self.buttons.append(Button('Instructions', state_manager.main_font, (255, 30, 0), start_x + 2 * (button_width + spacing), 450, button_width, button_height, 
                                   action=self.instructions))
        self.buttons.append(Button('Player Stats', state_manager.main_font, (255, 30, 0), start_x + 3 * (button_width + spacing), 450, button_width, button_height, 
                                   action=self.player_stats))
        self.buttons.append(Button('Leaderboard', state_manager.main_font, (255, 30, 0), start_x + 4 * (button_width + spacing), 450, button_width, button_height, 
                                   action=self.leaderboard))
        self.sign_out_button = Button('Sign Out', state_manager.main_font, (0, 0, 255),490,525,button_width,button_height, 
                                   action=self.sign_out)
    def play_ai(self):
        self.state_manager.push_state(SelectDifficulty(self.state_manager,self.state_manager.user_id))

    def play_friend(self):
        self.state_manager.push_state(PlayFriend(self.state_manager,self.state_manager.user_id))

    def instructions(self):
        self.state_manager.push_state(Instructions(self.state_manager))

    def player_stats(self):
        self.state_manager.push_state(PlayerStats(self.state_manager,self.state_manager.user_id))

    def leaderboard(self):
        self.state_manager.push_state(Leaderboard(self.state_manager))

    def sign_out(self):
        self.state_manager.pop_state()
        self.state_manager.pop_state()

    def handle_events(self, event):
        self.sign_out_button.is_clicked(pygame.mouse.get_pos())
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.buttons:
                if button.is_clicked(mouse_pos):
                    button.perform_action()
                elif self.sign_out_button.is_clicked(event.pos):
                    self.sign_out_button.perform_action()
            

    def draw(self, screen):
        super().draw(screen)
        screen.blit(self.car_image, self.car_image_rect)
        screen.blit(self.game_name, self.game_name_rect)
        self.sign_out_button.draw(screen)
