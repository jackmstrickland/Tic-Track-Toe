import pygame

class TextBox:
    def __init__(self, font, x, y, width, height, colour=(255, 255, 255), text_colour=(0, 0, 0), border_colour=(0, 0, 0), max_characters=20, is_password=False):
        self.font = font
        self.text = ''
        self.colour = colour
        self.text_colour = text_colour
        self.border_colour = border_colour
        self.rect = pygame.Rect(x, y, width, height)
        self.active = False
        self.base_colour = colour
        self.active_colour = (200, 200, 255)  
        self.max_characters = max_characters  # Limit the number of characters
        self.is_password = is_password  # Flag to hide the password
        self.cursor_width = 2  # Width of the cursor line
        self.cursor_rect = pygame.Rect(self.rect.x + 5, self.rect.y + 5, self.cursor_width, height - 10)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                pass
            elif event.key == pygame.K_ESCAPE:
                self.active = False
            else:
                if event.unicode.isprintable():
                    if len(self.text) < self.max_characters:
                        self.text += event.unicode

    def get_text(self):
        return self.text  # Return the actual text

    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, self.active_colour, self.rect)
        else:
            pygame.draw.rect(screen, self.base_colour, self.rect)
        pygame.draw.rect(screen, self.border_colour, self.rect, 2)

        if self.is_password:
            text_surface = self.font.render('*' * len(self.text), True, self.text_colour)
        else:
            text_surface = self.font.render(self.text, True, self.text_colour)
        text_rect = text_surface.get_rect(topleft=(self.rect.x + 5, self.rect.y + 5))
        screen.blit(text_surface, text_rect)

        # Draw the cursor
        if self.active:
            self.cursor_rect.topleft = (text_rect.right, text_rect.top)
            pygame.draw.rect(screen, self.text_colour, self.cursor_rect)
