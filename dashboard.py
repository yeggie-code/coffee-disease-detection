from kivy.uix.screenmanager import Screen

class DashboardScreen(Screen):
    def go_to_detection(self, instance=None):
        self.manager.current = "detection"

    def go_to_history(self, instance=None):
        self.manager.current = "history"

    def go_to_selling(self, instance=None):
        self.manager.current = "selling"

    def go_to_profile(self, instance=None):
        self.manager.current = "profile"

    def go_to_statistics(self, instance=None):
        self.manager.current = "statistics"

    def go_to_weather(self, instance=None):
        self.manager.current = "weather"

    def logout(self, instance=None):
        # Clear user session data
        app = self.manager.parent
        if hasattr(app, 'current_user_email'):
            app.current_user_email = None
        # Navigate back to login screen
        self.manager.current = "login"
