import pygame
from .state import State
from .button import BackButton

class Instructions(State):
    def __init__(self, state_manager):
        super().__init__(state_manager)
        
        self.back_button = BackButton(state_manager)

    def draw(self, screen):
        screen.fill((175, 0, 52))
        instruction_text = self.wrap_text(
            "Here's the rules:\n"
            " A 3x3 square grid is lined up with F1 teams, nations and achievements.\n"
            " Place your marker, an X or O, in one of the squares if you can name an F1 driver that matches the criteria across the top row and left hand side.\n"
            " The driver can be current or former and can be used more than once a game.\n"
            " The first to get three in a row, vertically, horizontally or diagonally, is the winner.\n"
            " Good luck!", self.state_manager.main_font_instructions, 1000
        )
        y = 250
        for line in instruction_text:
            text_surf = self.state_manager.main_font_instructions.render(line, True, (255, 255, 255))
            screen.blit(text_surf, (100, y))
            y += text_surf.get_height() + 5  # Adds some vertical spacing between lines
        
        self.back_button.draw(screen)
        
        pygame.display.update()

    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = ''

        for word in words:
            # Construct a test line to see if adding the new word exceeds the max width
            test_line = current_line + (word + ' ')
            test_surface = font.render(test_line, True, (255, 255, 255))
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + ' '

        if current_line:
            lines.append(current_line)

        return lines

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button.is_clicked(event.pos):
                self.back_button.perform_action()
        super().handle_events(event)
