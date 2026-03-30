import pygame, sqlite3 , bcrypt
from .textbox import TextBox
from .state import State
from .button import Button

class Register(State):
    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.font = state_manager.main_font_instructions
        self.username_box = TextBox(self.font, 515, 200, 550, 60)
        self.password_box = TextBox(self.font, 515, 300, 550, 60, is_password=True)
        self.message = ''
        self.register_name = state_manager.bold_font.render('Press enter to create account', False, (255, 255, 238))
        self.register_name_rect = self.register_name.get_rect(center=(600, 100))
        self.username_text = state_manager.bold_font_login.render('New Username - ', False, (255, 255, 238))
        self.username_text_rect = self.username_text.get_rect(midright=(450, 225))
        self.password_text = state_manager.bold_font_login.render('New Password - ', False, (255, 255, 238))
        self.password_text_rect = self.password_text.get_rect(midright=(450, 325))

        # Button for returning to the login page
        self.back_to_login_button = Button(
            "Press for Login page",
            self.font,
            (0, 0, 255),
            515, 400, 550, 60,
            self.return_to_login
        )

    def is_valid_input(self, text):
        # Check if text is not empty and contains only alphanumeric characters
        return text.isalnum()

    def register_user(self, username, password):
        db_path = 'Database/game.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            # Hash the password before storing it
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) #Add salt to password to encrypt

            cursor.execute('INSERT INTO userinfo (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()

            # Fetch the userId of the new user
            cursor.execute('SELECT userId FROM userinfo WHERE username=?', (username,))
            user_id = cursor.fetchone()[0]

            # Insert into userstats table
            cursor.execute('INSERT INTO userstats (userId) VALUES (?)', (user_id,))
            conn.commit()
            self.message = "Registration successful!"
        except sqlite3.IntegrityError:
            self.message = "Username already taken."
        finally:
            conn.close()

    def handle_events(self, event):
        self.username_box.handle_event(event)
        self.password_box.handle_event(event)
        self.back_to_login_button.is_clicked(pygame.mouse.get_pos())

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_to_login_button.is_clicked(event.pos):
                self.back_to_login_button.perform_action()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            username = self.username_box.get_text()
            password = self.password_box.get_text()
            if username and password:
                # Validate input
                if self.is_valid_input(username) and self.is_valid_input(password):
                    self.register_user(username, password)
                else:
                    self.message = "Only alphanumeric characters are allowed."

    def draw(self, screen):
        super().draw(screen)  
        self.username_box.draw(screen)
        self.password_box.draw(screen)
        self.back_to_login_button.draw(screen)
        message_surface = self.font.render(self.message, True, (255, 255, 255))
        screen.blit(message_surface, (515, 500)) 
        screen.blit(self.register_name, self.register_name_rect)
        screen.blit(self.username_text, self.username_text_rect)
        screen.blit(self.password_text, self.password_text_rect)
        pygame.display.flip()

    def update(self):
        pass

    def return_to_login(self):
        from .login import Login
        self.state_manager.pop_state()
        self.state_manager.push_state(Login(self.state_manager))


