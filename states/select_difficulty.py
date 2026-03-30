import pygame
from states.button import Button, BackButton
from states.state import State
from states.play_ai import PlayAI

class SelectDifficulty(State):

    def __init__(self, state_manager, userid):
        super().__init__(state_manager)
        self.difficulty = None
        self.userid = userid
        self.text = state_manager.bold_font.render('Select Difficulty:', False, (255, 255, 238))
        self.text_rect = self.text.get_rect(center=(600, 100))
        self.back_button = BackButton(state_manager)

        # Create menu buttons horizontally
        button_width = 215
        button_height = 60
        spacing = 20  # Space between buttons
        start_x = (1200 - (3 * button_width + 2 * spacing)) // 2  # Centering the buttons

        self.buttons.append(Button('Easy', state_manager.main_font, (255, 30, 0), start_x, 300, button_width, button_height, 
                                   action=self.easy_mode))
        self.buttons.append(Button('Medium', state_manager.main_font, (255, 30, 0), start_x + button_width + spacing, 300, button_width, button_height, 
                                   action=self.medium_mode))
        self.buttons.append(Button('Hard', state_manager.main_font, (255, 30, 0), start_x + 2 * (button_width + spacing), 300, button_width, button_height, 
                                   action=self.hard_mode))

    def easy_mode(self):
        self.difficulty = 'easy'
        self.state_manager.push_state(PlayAI(self.state_manager, self.userid, self.difficulty))

    def medium_mode(self):
        self.difficulty = 'medium'
        self.state_manager.push_state(PlayAI(self.state_manager, self.userid, self.difficulty))

    def hard_mode(self):
        self.difficulty = 'hard'
        self.state_manager.push_state(PlayAI(self.state_manager, self.userid, self.difficulty))

    def draw(self, screen):
        super().draw(screen)
        screen.blit(self.text, self.text_rect)
        self.back_button.draw(screen)
        
        pygame.display.update()

    
    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button.is_clicked(event.pos):
                self.back_button.perform_action()
        super().handle_events(event)