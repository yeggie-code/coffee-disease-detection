from kivy.uix.screenmanager import Screen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.utils import rgba
from kivy.app import App
import random
from datetime import datetime
import requests
import json
from ui_theme import AppTheme

# GPS import handled in methods to avoid module-level import errors
GPS_AVAILABLE = False

try:
    from config import OPENWEATHERMAP_API_KEY
except ImportError:
    OPENWEATHERMAP_API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"

class WeatherScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Main container with background
        from kivy.uix.image import Image
        
        main_container = MDBoxLayout(orientation='vertical')
        
        # Background image
        with main_container.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(source='../assets/0db150166098c8e1bb1392a6904e63e3.jpg', pos=main_container.pos, size=main_container.size)
            main_container.bind(pos=self._update_bg, size=self._update_bg)
        
        self.layout = MDBoxLayout(
            orientation='vertical',
            spacing=AppTheme.SPACING_MEDIUM,
            padding=AppTheme.PADDING_STANDARD
        )

        # Store weather data
        self.current_weather = None
        self.location = None
        
        # Default coordinates (can be set to a default location like Nairobi, Kenya)
        self.current_lat = -1.2864  # Nairobi latitude
        self.current_lon = 36.8172  # Nairobi longitude
        
        # GPS timeout handling
        self.gps_timeout = None

        # Top bar
        top_bar = MDBoxLayout(**AppTheme.get_top_bar_style())
        
        back_btn = MDIconButton(
            icon="arrow-left",
            **AppTheme.get_icon_button_style(),
            on_release=self.go_back
        )
        top_bar.add_widget(back_btn)
        
        title = MDLabel(
            text="Weather & Disease Risk",
            halign="center",
            size_hint_x=1,
            color=AppTheme.TEXT_PRIMARY,
            size_hint_y=None,
            height=dp(50)
        )
        top_bar.add_widget(title)
        
        refresh_btn = MDButton(
            text="↻",
            on_release=self.refresh_weather,
            size_hint=(None, None),
            size=(dp(50), dp(50)),
            md_bg_color=AppTheme.SUCCESS_COLOR
        )
        top_bar.add_widget(refresh_btn)
        
        location_btn = MDButton(
            text="📍",
            on_release=self.show_gps_info,
            size_hint=(None, None),
            size=(dp(50), dp(50)),
            md_bg_color=AppTheme.ACCENT_COLOR
        )
        top_bar.add_widget(location_btn)
        self.layout.add_widget(top_bar)

        # Weather cards container
        scroll = ScrollView()
        self.weather_layout = MDBoxLayout(
            orientation='vertical',
            adaptive_height=True,
            spacing=AppTheme.SPACING_LARGE,
            padding=AppTheme.SPACING_MEDIUM
        )

        # Load weather data
        self.load_weather_data()

        scroll.add_widget(self.weather_layout)
        self.layout.add_widget(scroll)

        main_container.add_widget(self.layout)
        self.add_widget(main_container)

    def go_back(self, instance):
        self.manager.current = "dashboard"
    
    def _update_bg(self, instance, value):
        """Update background rectangle position and size"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = instance.pos
            self.bg_rect.size = instance.size

    def show_gps_info(self, instance):
        """Show GPS information for desktop platforms"""
        popup = Popup(title='GPS Information', 
                     content=Label(text='GPS location detection is designed for mobile devices.\n\nOn desktop platforms like Windows, GPS is not available.\n\nThe app uses default location (Nairobi, Kenya) for weather data.\n\nFor mobile apps, GPS will work automatically when deployed.'), 
                     size_hint=(0.8, 0.5))
        popup.open()

    def update_location(self, instance):
        """Update location using GPS"""
        import platform
        
        # Check if we're on a platform that supports GPS
        system = platform.system().lower()
        if system not in ['android', 'ios', 'darwin']:  # GPS typically only works on mobile platforms
            popup = Popup(title='GPS Not Supported', 
                         content=Label(text='GPS location detection is not supported\non desktop platforms like Windows.\n\nUsing default location (Nairobi, Kenya).\n\nFor mobile devices, GPS will work automatically.'), 
                         size_hint=(0.7, 0.4))
            popup.open()
            return

        try:
            from plyer import gps
        except ImportError:
            popup = Popup(title='GPS Not Available', 
                         content=Label(text='GPS functionality is not available on this device.\nUsing default location.'), 
                         size_hint=(0.6, 0.3))
            popup.open()
            return

        try:
            gps.configure(on_location=self.on_location, on_status=self.on_status)
            gps.start(minTime=1000, minDistance=1)
            
            # Store popup reference to close it later
            self.location_popup = Popup(title='Getting Location', 
                                       content=Label(text='Retrieving your location...\nPlease wait...'), 
                                       size_hint=(0.6, 0.3))
            self.location_popup.open()
            
            # Set a timeout for GPS detection (15 seconds)
            from kivy.clock import Clock
            self.gps_timeout = Clock.schedule_once(self.on_gps_timeout, 15)
            
        except Exception as e:
            popup = Popup(title='GPS Error', 
                         content=Label(text=f'Could not access GPS: {str(e)}\n\nUsing default location.'), 
                         size_hint=(0.6, 0.3))
            popup.open()

    def on_location(self, **kwargs):
        """GPS location callback"""
        # Cancel the timeout if location is received
        if self.gps_timeout:
            from kivy.clock import Clock
            Clock.unschedule(self.gps_timeout)
            self.gps_timeout = None
            
        self.location = {
            'latitude': kwargs.get('lat'),
            'longitude': kwargs.get('lon')
        }
        # Set current coordinates for weather API
        self.current_lat = kwargs.get('lat')
        self.current_lon = kwargs.get('lon')
        
        try:
            from plyer import gps
            gps.stop()
        except ImportError:
            pass
        
        # Close the location popup if it exists
        if hasattr(self, 'location_popup'):
            self.location_popup.dismiss()
        
        # Show success popup
        popup = Popup(title='Location Found', 
                     content=Label(text=f'Location: {self.current_lat:.4f}, {self.current_lon:.4f}\nFetching weather data...'), 
                     size_hint=(0.6, 0.3))
        popup.open()
        
        # Refresh weather with new location
        self.refresh_weather(None)

    def on_status(self, stype, status):
        """GPS status callback"""
        if status == 'provider-enabled':
            # GPS is working
            pass
        elif status == 'provider-disabled':
            # GPS is disabled
            if self.gps_timeout:
                from kivy.clock import Clock
                Clock.unschedule(self.gps_timeout)
                self.gps_timeout = None
            if hasattr(self, 'location_popup'):
                self.location_popup.dismiss()
            popup = Popup(title='GPS Disabled', 
                         content=Label(text='GPS is disabled on this device.\nPlease enable GPS and try again.\n\nUsing default location.'), 
                         size_hint=(0.6, 0.3))
            popup.open()
        elif status == 'gps-not-available':
            # GPS not available
            if self.gps_timeout:
                from kivy.clock import Clock
                Clock.unschedule(self.gps_timeout)
                self.gps_timeout = None
            if hasattr(self, 'location_popup'):
                self.location_popup.dismiss()
            popup = Popup(title='GPS Unavailable', 
                         content=Label(text='GPS is not available on this device.\nUsing default location.'), 
                         size_hint=(0.6, 0.3))
            popup.open()

    def on_gps_timeout(self, dt):
        """Handle GPS timeout"""
        self.gps_timeout = None
        try:
            from plyer import gps
            gps.stop()
        except ImportError:
            pass
            
        if hasattr(self, 'location_popup'):
            self.location_popup.dismiss()
            
        popup = Popup(title='GPS Timeout', 
                     content=Label(text='GPS location detection timed out.\n\nThis may happen on desktop platforms\nor when GPS signal is weak.\n\nUsing default location (Nairobi, Kenya).'), 
                     size_hint=(0.7, 0.4))
        popup.open()

    def refresh_weather(self, instance):
        """Refresh weather data"""
        # Clear existing cards
        self.weather_layout.clear_widgets()
        # Reload data
        self.load_weather_data()

    def load_weather_data(self):
        """Load weather data and disease risk analysis"""
        # Try to get real weather data, fallback to mock data
        weather_data = self.get_real_weather_data()
        if not weather_data:
            weather_data = self.get_mock_weather_data()

        # Check if user is logged in for personalized data
        try:
            app = App.get_running_app()
            user_logged_in = hasattr(app, 'current_user_email') and app.current_user_email
        except:
            user_logged_in = False

        # Current conditions card
        current_card = MDCard(orientation='vertical', padding=dp(15), radius=[15, 15, 15, 15], elevation=4, size_hint_y=None, height=dp(180), md_bg_color=rgba("#E6F3FF"))
        current_card.add_widget(MDLabel(text="Current Conditions", theme_text_color="Primary"))

        if weather_data.get('location'):
            current_card.add_widget(MDLabel(text=f"Location: {weather_data['location']}", theme_text_color="Secondary"))

        current_card.add_widget(MDLabel(text=f"Temperature: {weather_data['temperature']}°C", theme_text_color="Secondary"))
        current_card.add_widget(MDLabel(text=f"Humidity: {weather_data['humidity']}%", theme_text_color="Secondary"))
        current_card.add_widget(MDLabel(text=f"Rainfall: {weather_data.get('rainfall', 'N/A')}mm", theme_text_color="Secondary"))
        current_card.add_widget(MDLabel(text=f"Wind: {weather_data['wind']} km/h", theme_text_color="Secondary"))
        current_card.add_widget(MDLabel(text=f"Condition: {weather_data.get('condition', 'N/A')}", theme_text_color="Secondary"))
        self.weather_layout.add_widget(current_card)

        # Disease risk assessment
        risk_card = MDCard(orientation='vertical', padding=dp(15), radius=[15, 15, 15, 15], elevation=4, size_hint_y=None, height=dp(200), md_bg_color=rgba("#FFF5E6"))
        risk_card.add_widget(MDLabel(text="Disease Risk Assessment", theme_text_color="Primary"))

        risk_level, risk_color, recommendations = self.assess_disease_risk(weather_data)

        risk_card.add_widget(MDLabel(text=f"Risk Level: {risk_level}", theme_text_color="Secondary", bold=True))
        risk_card.add_widget(MDLabel(text=f"Conditions: {recommendations}", theme_text_color="Hint", halign='left'))

        self.weather_layout.add_widget(risk_card)

        # Forecast card
        forecast_card = MDCard(orientation='vertical', padding=dp(15), radius=[15, 15, 15, 15], elevation=4, size_hint_y=None, height=dp(180), md_bg_color=rgba("#F0FFF0"))
        forecast_card.add_widget(MDLabel(text="3-Day Forecast", theme_text_color="Primary"))

        forecast_text = ""
        for i, day_data in enumerate(weather_data['forecast'], 1):
            forecast_text += f"Day {i}: {day_data['temp']}°C, {day_data['humidity']}%, {day_data['condition']}\n"

        forecast_card.add_widget(MDLabel(text=forecast_text.strip(), theme_text_color="Secondary", halign='left'))
        self.weather_layout.add_widget(forecast_card)

        # Prevention tips card
        tips_card = MDCard(orientation='vertical', padding=dp(15), radius=[15, 15, 15, 15], elevation=4, size_hint_y=None, height=dp(150), md_bg_color=rgba("#FFF0F5"))
        tips_card.add_widget(MDLabel(text="Prevention Tips", theme_text_color="Primary"))

        tips = self.get_prevention_tips(weather_data)
        tips_text = "\n".join(f"• {tip}" for tip in tips)
        tips_card.add_widget(MDLabel(text=tips_text, theme_text_color="Secondary", halign='left'))

        self.weather_layout.add_widget(tips_card)

    def get_mock_weather_data(self):
        """Generate mock weather data"""
        return {
            'temperature': random.randint(20, 35),
            'humidity': random.randint(40, 90),
            'rainfall': random.uniform(0, 10),
            'wind': random.randint(5, 25),
            'forecast': [
                {
                    'temp': random.randint(20, 35),
                    'humidity': random.randint(40, 90),
                    'condition': random.choice(['Sunny', 'Cloudy', 'Rainy', 'Humid'])
                } for _ in range(3)
            ]
        }

    def get_real_weather_data(self):
        """Fetch real weather data from OpenWeatherMap API"""
        try:
            # Get current location
            if not hasattr(self, 'current_lat') or not hasattr(self, 'current_lon'):
                return None

            # OpenWeatherMap API key (you'll need to get your own free API key)
            api_key = OPENWEATHERMAP_API_KEY

            if api_key == "YOUR_OPENWEATHERMAP_API_KEY":
                return None  # No API key configured

            # API endpoint for current weather
            current_url = f"http://api.openweathermap.org/data/2.5/weather?lat={self.current_lat}&lon={self.current_lon}&appid={api_key}&units=metric"

            response = requests.get(current_url, timeout=10)
            response.raise_for_status()

            current_data = response.json()

            # API endpoint for 3-day forecast
            forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={self.current_lat}&lon={self.current_lon}&appid={api_key}&units=metric"

            forecast_response = requests.get(forecast_url, timeout=10)
            forecast_response.raise_for_status()

            forecast_data = forecast_response.json()

            # Extract current weather data
            weather_data = {
                'location': current_data.get('name', 'Unknown Location'),
                'temperature': round(current_data['main']['temp']),
                'humidity': current_data['main']['humidity'],
                'wind': round(current_data['wind']['speed'] * 3.6),  # Convert m/s to km/h
                'condition': current_data['weather'][0]['description'].title() if current_data['weather'] else 'Unknown',
                'rainfall': current_data.get('rain', {}).get('1h', 0),  # Rainfall in last hour
                'forecast': []
            }

            # Extract 3-day forecast (one reading per day)
            daily_forecasts = {}
            for item in forecast_data['list']:
                date = item['dt_txt'].split(' ')[0]  # Get date part
                if date not in daily_forecasts and len(daily_forecasts) < 3:
                    daily_forecasts[date] = {
                        'temp': round(item['main']['temp']),
                        'humidity': item['main']['humidity'],
                        'condition': item['weather'][0]['description'].title() if item['weather'] else 'Unknown'
                    }

            weather_data['forecast'] = list(daily_forecasts.values())

            return weather_data

        except requests.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None
        except KeyError as e:
            print(f"Error parsing weather data: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in weather fetch: {e}")
            return None

    def assess_disease_risk(self, weather_data):
        """Assess disease risk based on weather conditions"""
        temp = weather_data['temperature']
        humidity = weather_data['humidity']
        rainfall = weather_data['rainfall']

        risk_score = 0

        # Temperature factor (optimal for fungal diseases: 20-30°C)
        if 20 <= temp <= 30:
            risk_score += 3
        elif 15 <= temp <= 35:
            risk_score += 2
        else:
            risk_score += 1

        # Humidity factor (high humidity increases fungal risk)
        if humidity > 80:
            risk_score += 3
        elif humidity > 60:
            risk_score += 2
        else:
            risk_score += 1

        # Rainfall factor
        if rainfall > 5:
            risk_score += 3
        elif rainfall > 2:
            risk_score += 2
        else:
            risk_score += 1

        if risk_score >= 7:
            risk_level = "HIGH"
            risk_color = rgba("#FF4444")
            recommendations = "High risk conditions detected. Monitor crops closely and consider preventive treatments."
        elif risk_score >= 5:
            risk_level = "MODERATE"
            risk_color = rgba("#FFAA00")
            recommendations = "Moderate risk. Regular monitoring recommended."
        else:
            risk_level = "LOW"
            risk_color = rgba("#44AA44")
            recommendations = "Low risk conditions. Maintain regular care routine."

        return risk_level, risk_color, recommendations

    def get_prevention_tips(self, weather_data):
        """Get weather-specific prevention tips"""
        tips = []

        if weather_data['humidity'] > 70:
            tips.append("Increase air circulation between plants")
            tips.append("Avoid overhead watering to reduce humidity")

        if weather_data['temperature'] > 30:
            tips.append("Provide shade during peak heat")
            tips.append("Ensure adequate watering to prevent stress")

        if weather_data['rainfall'] > 3:
            tips.append("Improve drainage to prevent waterlogging")
            tips.append("Monitor for fungal growth after rain")

        if weather_data['wind'] > 15:
            tips.append("Protect young plants from strong winds")
            tips.append("Secure loose leaves and branches")

        # Default tips if conditions are good
        if not tips:
            tips = [
                "Maintain proper plant spacing",
                "Regular pruning to improve air flow",
                "Monitor plants weekly for early signs",
                "Keep tools clean and disinfected"
            ]

        return tips[:4]  # Return max 4 tips
