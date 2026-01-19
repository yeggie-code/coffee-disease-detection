from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from db import get_connection

class RecoveryScreen(Screen):
    def reset_password(self):
        email = self.ids.email.text
        newpass = self.ids.newpass.text

        if not email or not newpass:
            self.show_popup("Error", "All fields are required")
            return

        try:
            conn = get_connection()
            my_cursor = conn.cursor()
            my_cursor.execute("SELECT * FROM register WHERE email=%s", (email,))
            row = my_cursor.fetchone()

            if row:
                my_cursor.execute("UPDATE register SET password=%s WHERE email=%s", (newpass, email))
                conn.commit()
                self.show_popup("Success", "Password updated successfully!")
            else:
                self.show_popup("Error", "Email not found")

            conn.close()
        except Exception as es:
            self.show_popup("Error", f"Due To: {str(es)}")

    def show_popup(self, title, msg):
        popup = Popup(title=title, content=Label(text=msg), size_hint=(0.6, 0.4))
        popup.open()

    def go_back(self):
        self.manager.current = "login"
