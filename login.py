from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from db import get_connection

class LoginScreen(Screen):
    def login_user(self):
        email = self.ids.email.text
        password = self.ids.password.text

        if not email or not password:
            self.show_popup("Error", "All fields required")
            return

        try:
            conn = get_connection()
            my_cursor = conn.cursor()
            my_cursor.execute("SELECT * FROM register WHERE email=%s AND password=%s", (email, password))
            row = my_cursor.fetchone()
            if row:
                App.get_running_app().current_user = row[1]  # fname
                App.get_running_app().current_user_email = row[3]  # email
                # Load language
                try:
                    my_cursor.execute("SELECT language FROM register WHERE email=%s", (email,))
                    lang_row = my_cursor.fetchone()
                    if lang_row and lang_row[0]:
                        App.get_running_app().current_user_language = lang_row[0]
                    else:
                        App.get_running_app().current_user_language = "English"
                except:
                    App.get_running_app().current_user_language = "English"
                self.manager.current = "dashboard"
            else:
                self.show_popup("Error", "Invalid credentials") 
            conn.close()
        except Exception as es:
            self.show_popup("Error", f"Due To: {str(es)}")

    def show_popup(self, title, msg):
        popup = Popup(title=title, content=Label(text=msg), size_hint=(0.6, 0.4))
        popup.open()
