from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from db import get_connection

class RegisterScreen(Screen):
    def register_user(self):
        fname = self.ids.fname.text
        lname = self.ids.lname.text
        email = self.ids.email.text
        password = self.ids.password.text
        confpass = self.ids.confpass.text

        if not fname or not email or not password or not confpass:
            self.show_popup("Error", "All fields are required")
        elif password != confpass:
            self.show_popup("Error", "Passwords do not match")
        else:
            try:
                conn = get_connection()
                my_cursor = conn.cursor()

                my_cursor.execute("SELECT * FROM register WHERE email=%s", (email,))
                row = my_cursor.fetchone()

                if row:
                    self.show_popup("Error", "User already exists")
                else:
                    my_cursor.execute(
                        "INSERT INTO register (fname, lname, email, password) VALUES (%s,%s,%s,%s)",
                        (fname, lname, email, password)
                    )
                    conn.commit()
                    self.show_popup("Success", "Registered successfully!")
                conn.close()
            except Exception as es:
                self.show_popup("Error", f"Due To: {str(es)}")

    def show_popup(self, title, msg):
        popup = Popup(title=title, content=Label(text=msg), size_hint=(0.6, 0.4))
        popup.open()

    def go_back(self):
        self.manager.current = "login"
