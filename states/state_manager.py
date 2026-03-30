import pygame
from states.main_menu import MainMenu
from states.play_ai import PlayAI
from states.play_friend import PlayFriend
from states.instructions import Instructions
from states.player_stats import PlayerStats
from states.leaderboard import Leaderboard
from states.login import Login
from states.welcome_screen import Welcome_Screen

class StateManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 600))
        pygame.display.set_caption('Tic Track Toe')
        self.icon = pygame.image.load('Images/f1icon.png').convert_alpha()
        pygame.display.set_icon(self.icon)
        self.main_font = pygame.font.Font('Fonts/Formula1-Regular.otf', 30)
        self.bold_font = pygame.font.Font('Fonts/Formula1-Bold.otf', 60)
        self.main_font_instructions = pygame.font.Font('Fonts/Formula1-Bold.otf', 20)
        self.bold_font_login = pygame.font.Font('Fonts/Formula1-Bold.otf', 45)
        self.bold_font_title = pygame.font.Font('Fonts/Formula1-Bold.otf', 40)

        self.user_id = None
        self.state_stack = [Welcome_Screen(self)]

    def push_state(self, new_state):
        self.state_stack.append(new_state)

    def pop_state(self):
        if len(self.state_stack) > 1:
            self.state_stack.pop()

    def current_state(self):
        return self.state_stack[-1]

    def run(self):
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                self.current_state().handle_events(event)

            current_state = self.current_state()

            if hasattr(current_state, 'update_timer'):
                current_state.update_timer()

            self.screen.fill((0, 0, 0))
            current_state.draw(self.screen)

            pygame.display.update()

            clock.tick(60)