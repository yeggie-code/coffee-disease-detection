from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.core.window import Window
from db import get_connection
from login import LoginScreen
from register import RegisterScreen
from recovery import RecoveryScreen
from dashboard import DashboardScreen
from history import HistoryScreen
from detection import DetectionScreen
from user_profile import ProfileScreen
from selling import SellingScreen
from statistics import StatisticsScreen
from weather import WeatherScreen

class MyApp(MDApp):
    def build(self):
        # Set window size for better desktop experience
        Window.size = (400, 700)

        Builder.load_file("main.kv")
        # Enhanced agricultural theme with modern colors
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.primary_hue = "800"  # Rich green
        self.theme_cls.accent_palette = "Brown"
        self.theme_cls.accent_hue = "700"  # Warm brown
        self.theme_cls.theme_style = "Dark"

        # Modern font styling
        self.theme_cls.font_name = "Roboto"

        # Store ScreenManager as an attribute
        self.sm = ScreenManager()
        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(RegisterScreen(name="register"))
        self.sm.add_widget(RecoveryScreen(name="recovery"))
        self.sm.add_widget(DashboardScreen(name="dashboard"))
        self.sm.add_widget(HistoryScreen(name="history"))
        self.sm.add_widget(DetectionScreen(name="detection"))
        self.sm.add_widget(ProfileScreen(name="profile"))
        self.sm.add_widget(SellingScreen(name="selling"))
        self.sm.add_widget(StatisticsScreen(name="statistics"))
        self.sm.add_widget(WeatherScreen(name="weather"))
        self.sm.current = "login"

        return self.sm

if __name__ == '__main__':
    MyApp().run()
