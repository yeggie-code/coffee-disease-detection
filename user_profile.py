from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.lang import Builder
from db import execute, get_connection
import mysql.connector

# Explicitly load the KV file
Builder.load_file('profile.kv')

class ProfileScreen(Screen):

    def on_pre_enter(self):
        """Load user info from App object."""
        try:
            from kivy.app import App
            app = App.get_running_app()

            self.ids.name_label.text = f"Name: {app.current_user}"
            self.ids.email_label.text = f"Email: {app.current_user_email}"

            # Sync spinner language
            if hasattr(app, 'current_user_language'):
                self.ids.lang_spinner.text = app.current_user_language

        except Exception as e:
            print("Profile load error:", e)

    def go_back(self, *args):
        self.manager.current = "dashboard"

    def save_language(self, *args):
        try:
            from kivy.app import App
            app = App.get_running_app()

            selected = self.ids.lang_spinner.text
            setattr(app, "current_user_language", selected)

            email = app.current_user_email
            if email:
                # Update DB
                updated = execute(
                    "UPDATE register SET language=%s WHERE email=%s",
                    (selected, email)
                )

                if not updated:
                    # Try adding column then retry
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("ALTER TABLE register ADD COLUMN language VARCHAR(50) DEFAULT 'English'")
                    conn.commit()
                    conn.close()

                    execute("UPDATE register SET language=%s WHERE email=%s", (selected, email))

            Popup(title="Saved",
                  content=Label(text=f"Language saved: {selected}"),
                  size_hint=(0.6, 0.3)).open()

        except Exception as e:
            Popup(title="Error",
                  content=Label(text=str(e)),
                  size_hint=(0.6, 0.3)).open()
