import pygame

class Button:
    def __init__(self, text, font, colour, x, y, width, height, action=None):
        self.text = text
        self.font = font
        self.colour = colour
        self.rect = pygame.Rect(x, y, width, height)
        self.surface = pygame.Surface((width, height))
        self.create_button_surface()
        self.action = action

    def create_button_surface(self):
        self.surface.fill(self.colour)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
        self.surface.blit(text_surf, text_rect)

    def draw(self, screen):
        screen.blit(self.surface, self.rect.topleft)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def perform_action(self):
        if self.action:
            self.action()

class BackButton(Button):
    def __init__(self, state_manager, x=500, y=525, width=250, height=70):
        from states.state_manager import StateManager  # Absolute import
        super().__init__('Back to Menu', state_manager.main_font, (175, 0, 200), x, y, width, height, action=state_manager.pop_state)
        self.state_manager = state_manager
