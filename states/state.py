import pygame

class State:
    def __init__(self, state_manager):
        self.buttons = []
        self.state_manager = state_manager

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.buttons:
                if button.is_clicked(mouse_pos):
                    button.perform_action()

    def draw(self, screen):
        screen.fill((175, 0, 52))  # Default background colour for the state
        for button in self.buttons:
            button.draw(screen)
