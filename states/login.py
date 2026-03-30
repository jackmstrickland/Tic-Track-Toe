import bcrypt
import sqlite3
import pygame
from .state import State
from .textbox import TextBox
from .button import Button
from .main_menu import MainMenu
from .register import Register

class Login(State):
    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.font = state_manager.main_font_instructions
        self.username_box = TextBox(self.font, 515, 200, 550, 60)
        self.password_box = TextBox(self.font, 515, 300, 550, 60, is_password=True)
        self.password_box.text_colour = (0,0,0)
        self.password_box.base_colour = (255,255,255)
        self.password_box.active_colour = (200, 200, 255)
        self.message = ''
        self.login_name = state_manager.bold_font.render('Login Page - Press enter to sign in', False, (255, 255, 238))
        self.login_name_rect = self.login_name.get_rect(center=(600, 100))
        self.username_text = state_manager.bold_font_login.render('Username - ', False, (255, 255, 238))
        self.username_text_rect = self.username_text.get_rect(midright=(450,225))
        self.password_text = state_manager.bold_font_login.render('Password - ', False, (255, 255, 238))
        self.password_text_rect = self.password_text.get_rect(midright=(450,325))

        self.register_button = Button(
            "Press for register page",
            self.font,
            (0, 0, 255),
            515, 425, 550, 60,
            self.go_to_register
        )

    def check_credentials(self, username, password):
        db_path = 'Database/game.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM userinfo WHERE username=?', (username,))
        result = cursor.fetchone()
        conn.close()
        if result:
            hashed_password = result[0]
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
        return False

    def handle_events(self, event):
        self.username_box.handle_event(event)
        self.password_box.handle_event(event)
        self.register_button.is_clicked(pygame.mouse.get_pos())

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.register_button.is_clicked(event.pos):
                self.register_button.perform_action()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            username = self.username_box.get_text()
            password = self.password_box.get_text()

            if username and password:
                if self.check_credentials(username, password):
                    self.message = "Login successful!"
                    self.state_manager.user_id = self.get_user_id(username)
                    self.state_manager.push_state(MainMenu(self.state_manager))
                else:
                    self.message = "Invalid credentials"

    def get_user_id(self, username):
        db_path = 'Database/game.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT userId FROM userinfo WHERE username=?', (username,))
        user_id = cursor.fetchone()[0]
        conn.close()
        return user_id

    def draw(self, screen):
        super().draw(screen)
        self.username_box.draw(screen)
        self.password_box.draw(screen)
        self.register_button.draw(screen)
        message_surface = self.font.render(self.message, True, (255, 255, 255))
        screen.blit(message_surface, (510, 370)) 
        screen.blit(self.login_name, self.login_name_rect)
        screen.blit(self.username_text, self.username_text_rect)
        screen.blit(self.password_text, self.password_text_rect)
        pygame.display.flip()

    def update(self):
        pass

    def go_to_register(self):
        self.state_manager.push_state(Register(self.state_manager))
