import pygame
from .state import State
from .button import Button

class Welcome_Screen(State):

    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.font = state_manager.main_font_instructions
        self.car_image = pygame.image.load('Images/f1icon.png').convert_alpha()
        self.car_image_rect = self.car_image.get_rect(center=(600, 300))
        self.game_name = state_manager.bold_font.render('Tic Track Toe', False, (255, 255, 238))
        self.game_name_rect = self.game_name.get_rect(center=(600, 100))

        self.go_to_login = Button(
                "Click here to Login Page",
                self.font,
                (0, 0, 255),
                620, 425, 420, 70,
                self.go_to_login
            )
        
        self.go_to_register = Button(
            "Click here to Register Page",
            self.font,
            (0, 0, 255),
            120, 425, 420, 70,
            self.go_to_register
        )

    def go_to_login(self):
        from .login import Login
        self.state_manager.push_state(Login(self.state_manager))

    def go_to_register(self):
            from .register import Register
            self.state_manager.pop_state()
            self.state_manager.push_state(Register(self.state_manager))

    def handle_events(self, event):
        self.go_to_login.is_clicked(pygame.mouse.get_pos())
        self.go_to_register.is_clicked(pygame.mouse.get_pos())

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.go_to_login.is_clicked(event.pos):
                self.go_to_login.perform_action()
            elif self.go_to_register.is_clicked(event.pos):
                self.go_to_register.perform_action()
        
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    
    def draw(self,screen):
        super().draw(screen)
        self.go_to_login.draw(screen)
        self.go_to_register.draw(screen)
        screen.blit(self.car_image, self.car_image_rect)
        screen.blit(self.game_name, self.game_name_rect)

