from kivy.uix.screenmanager import Screen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDIconButton, MDFabButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.utils import rgba
import json
from db import fetch_all, execute
from kivy.app import App
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
import io
import base64
from kivymd.uix.menu import MDDropdownMenu
from ui_theme import AppTheme

class StatisticsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Main container with background image
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

        # Top bar
        top_bar = MDBoxLayout(**AppTheme.get_top_bar_style())
        
        back_btn = MDIconButton(
            icon="arrow-left",
            **AppTheme.get_icon_button_style(),
            on_release=self.go_back
        )
        top_bar.add_widget(back_btn)
        
        title = MDLabel(
            text="Farmer's Diary",
            halign="center",
            size_hint_x=1,
            color=AppTheme.TEXT_PRIMARY,
            size_hint_y=None,
            height=dp(50)
        )
        top_bar.add_widget(title)
        
        filter_btn = MDButton(
            text="Filter",
            on_release=self.show_filter_menu,
            size_hint=(None, None),
            size=(dp(80), dp(40)),
            md_bg_color=AppTheme.SECONDARY_COLOR
        )
        top_bar.add_widget(filter_btn)
        self.layout.add_widget(top_bar)

        # Filter bar
        self.filter_layout = MDBoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=AppTheme.SPACING_MEDIUM,
            padding=AppTheme.SPACING_SMALL,
            md_bg_color=AppTheme.BACKGROUND_LIGHT
        )
        self.filter_label = MDLabel(
            text="All Activities",
            size_hint_x=0.7,
            color=AppTheme.TEXT_DARK
        )
        clear_btn = MDButton(
            text="Clear",
            on_release=self.clear_filters,
            size_hint_x=0.3,
            size_hint_y=None,
            height=dp(40),
            md_bg_color=AppTheme.ERROR_COLOR
        )
        self.filter_layout.add_widget(self.filter_label)
        self.filter_layout.add_widget(clear_btn)
        self.layout.add_widget(self.filter_layout)

        # Stats summary cards
        self.summary_layout = MDBoxLayout(
            size_hint_y=None,
            height=dp(130),
            spacing=AppTheme.SPACING_MEDIUM,
            padding=AppTheme.SPACING_SMALL
        )
        self.create_summary_cards()
        self.layout.add_widget(self.summary_layout)

        # Diary entries container
        scroll = ScrollView()
        self.diary_layout = MDBoxLayout(
            orientation='vertical',
            adaptive_height=True,
            spacing=AppTheme.SPACING_LARGE,
            padding=AppTheme.SPACING_MEDIUM
        )

        # Load and display diary entries
        self.load_diary_entries()

        scroll.add_widget(self.diary_layout)
        self.layout.add_widget(scroll)

        # Floating action button for adding new entries
        fab = MDFabButton(
            icon="plus",
            pos_hint={"center_x": 0.9, "center_y": 0.1},
            on_release=self.show_add_entry_dialog
        )
        self.layout.add_widget(fab)

        main_container.add_widget(self.layout)
        self.add_widget(main_container)

        # Initialize filter variables
        self.current_filter = "all"
        self.filter_menu = None

    def on_pre_enter(self):
        """Refresh data when entering the screen"""
        self.refresh_statistics()

    def refresh_statistics(self):
        """Refresh all statistics and diary entries"""
        # Clear existing summary cards and recreate
        self.summary_layout.clear_widgets()
        self.create_summary_cards()

        # Clear existing diary entries and reload
        self.diary_layout.clear_widgets()
        self.load_diary_entries()

    def go_back(self, instance):
        self.manager.current = "dashboard"
    
    def _update_bg(self, instance, value):
        """Update background rectangle position and size"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = instance.pos
            self.bg_rect.size = instance.size

    def create_summary_cards(self):
        """Create summary cards showing farming statistics"""
        try:
            app = App.get_running_app()
            email = getattr(app, 'current_user_email', None)

            if not email:
                # Show login required message
                login_card = MDCard(orientation='vertical', padding=dp(15), radius=[15, 15, 15, 15], elevation=4, size_hint_y=None, height=dp(100), md_bg_color=rgba("#FFE6E6"))
                login_card.add_widget(MDLabel(text="Please login to view your farming diary", theme_text_color="Error", halign="center"))
                self.summary_layout.add_widget(login_card)
                return

            # Initialize database tables if they don't exist
            self.initialize_farming_tables()

            # Get summary statistics
            total_plantings = self.get_total_plantings(email)
            total_harvests = self.get_total_harvests(email)
            total_expenses = self.get_total_expenses(email)
            total_profits = self.get_total_profits(email)

            # Create summary cards
            planting_card = MDCard(orientation='vertical', padding=dp(10), radius=[10, 10, 10, 10], elevation=2, md_bg_color=rgba("#E6F3FF"))
            planting_card.add_widget(MDLabel(text="Total Plantings", theme_text_color="Primary"))
            planting_card.add_widget(MDLabel(text=f"{total_plantings}", theme_text_color="Secondary"))
            self.summary_layout.add_widget(planting_card)

            harvest_card = MDCard(orientation='vertical', padding=dp(10), radius=[10, 10, 10, 10], elevation=2, md_bg_color=rgba("#E6FFE6"))
            harvest_card.add_widget(MDLabel(text="Total Harvests", theme_text_color="Primary"))
            harvest_card.add_widget(MDLabel(text=f"{total_harvests} kg", theme_text_color="Secondary"))
            self.summary_layout.add_widget(harvest_card)

            expense_card = MDCard(orientation='vertical', padding=dp(10), radius=[10, 10, 10, 10], elevation=2, md_bg_color=rgba("#FFE6E6"))
            expense_card.add_widget(MDLabel(text="Total Expenses", theme_text_color="Primary"))
            expense_card.add_widget(MDLabel(text=f"KSh {total_expenses}", theme_text_color="Secondary"))
            self.summary_layout.add_widget(expense_card)

            profit_card = MDCard(orientation='vertical', padding=dp(10), radius=[10, 10, 10, 10], elevation=2, md_bg_color=rgba("#FFF5E6"))
            profit_card.add_widget(MDLabel(text="Net Profit", theme_text_color="Primary"))
            profit_card.add_widget(MDLabel(text=f"KSh {total_profits}", theme_text_color="Secondary"))
            self.summary_layout.add_widget(profit_card)

        except Exception as e:
            print(f"Summary cards error: {e}")
            error_card = MDCard(orientation='vertical', padding=dp(15), radius=[15, 15, 15, 15], elevation=4, md_bg_color=rgba("#FFE6E6"))
            error_card.add_widget(MDLabel(text="Error loading farming statistics", theme_text_color="Error"))
            self.summary_layout.add_widget(error_card)

    def create_stats_cards(self, disease_counts, monthly_stats, weekly_stats, total_detections):
        """Create statistics display cards - REMOVED: This is now a farmer's diary"""
        pass  # This method is no longer used - statistics screen is now a farmer's diary

    def show_trends_chart(self, instance):
        """Show a detailed trends chart using matplotlib"""
        try:
            app = App.get_running_app()
            email = getattr(app, 'current_user_email', None)
            if not email:
                popup = Popup(title='Login Required', content=Label(text='Please log in to view charts.'), size_hint=(0.6, 0.3))
                popup.open()
                return

            # Fetch data for the last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)

            query = """
            SELECT DATE(created_at) as date, disease, COUNT(*) as count
            FROM history
            WHERE email = %s AND created_at >= %s AND created_at <= %s
            GROUP BY DATE(created_at), disease
            ORDER BY date
            """
            data = fetch_all(query, (email, start_date, end_date))

            if not data:
                popup = Popup(title='No Data', content=Label(text='No detection data available for the last 30 days.'), size_hint=(0.6, 0.3))
                popup.open()
                return

            # Process data for plotting
            dates = []
            diseases = {}
            current_date = start_date.date()

            while current_date <= end_date.date():
                dates.append(current_date)
                current_date += timedelta(days=1)

            # Initialize disease counts
            for row in data:
                disease = row['disease']
                if disease not in diseases:
                    diseases[disease] = [0] * len(dates)

            # Fill in the counts
            date_to_index = {date: i for i, date in enumerate(dates)}
            for row in data:
                date_str = row['date']
                if isinstance(date_str, str):
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                else:
                    date_obj = date_str
                if date_obj in date_to_index:
                    idx = date_to_index[date_obj]
                    diseases[row['disease']][idx] = row['count']

            # Create the plot
            plt.figure(figsize=(12, 8))
            plt.style.use('seaborn-v0_8')

            colors = ['#8B4513', '#228B22', '#FF6347', '#4169E1', '#FFD700']
            for i, (disease, counts) in enumerate(diseases.items()):
                color = colors[i % len(colors)]
                plt.plot(dates, counts, label=disease.title(), color=color, linewidth=2, marker='o', markersize=4)

            plt.xlabel('Date', fontsize=12)
            plt.ylabel('Number of Detections', fontsize=12)
            plt.title('Disease Detection Trends (Last 30 Days)', fontsize=14, fontweight='bold')
            plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()

            # Convert plot to image for display
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            plt.close()

            # Create popup with the chart
            chart_image = Image()
            chart_image.texture = CoreImage(buf, ext='png').texture

            popup = Popup(title='Detection Trends Chart', content=chart_image, size_hint=(0.9, 0.8))
            popup.open()

        except Exception as e:
            popup = Popup(title='Chart Error', content=Label(text=f'Could not generate chart: {e}'), size_hint=(0.6, 0.3))
            popup.open()

    def export_statistics(self, instance):
        """Export statistics report to file"""
        try:
            app = App.get_running_app()
            email = getattr(app, 'current_user_email', None)
            if not email:
                popup = Popup(title='Login Required', content=Label(text='Please log in to export statistics.'), size_hint=(0.6, 0.3))
                popup.open()
                return

            # Fetch all user data
            query = "SELECT * FROM history WHERE email = %s ORDER BY created_at DESC"
            data = fetch_all(query, (email,))

            if not data:
                popup = Popup(title='No Data', content=Label(text='No detection data available to export.'), size_hint=(0.6, 0.3))
                popup.open()
                return

            # Generate report content
            report_content = f"""Coffee Disease Detection Statistics Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
User: {email}

SUMMARY STATISTICS
==================

Total Detections: {len(data)}

Disease Breakdown:
"""

            # Calculate disease counts
            disease_counts = {}
            for row in data:
                disease = row['disease']
                disease_counts[disease] = disease_counts.get(disease, 0) + 1

            for disease, count in sorted(disease_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(data)) * 100
                report_content += f"• {disease.title()}: {count} detections ({percentage:.1f}%)\n"

            # Health score
            healthy_count = disease_counts.get('nodisease', 0)
            health_score = (healthy_count / len(data)) * 100 if data else 0
            report_content += f"\nCrop Health Score: {health_score:.1f}%\n"

            # Recent activity
            report_content += "\n\nRECENT ACTIVITY\n===============\n"
            for row in data[:10]:  # Last 10 detections
                report_content += f"{row['created_at'].strftime('%Y-%m-%d %H:%M')}: {row['disease'].title()}\n"

            # Save to file
            from plyer import filechooser
            file_path = filechooser.save_file(title="Save Statistics Report", filters=[("Text files", "*.txt")])
            if file_path:
                with open(file_path[0], 'w') as f:
                    f.write(report_content)

                popup = Popup(title='Export Success', content=Label(text=f'Statistics report saved to: {file_path[0]}'), size_hint=(0.6, 0.3))
                popup.open()

        except Exception as e:
            popup = Popup(title='Export Error', content=Label(text=f'Could not export statistics: {e}'), size_hint=(0.6, 0.3))
            popup.open()

    def show_no_data_message(self):
        """Show message when no diary entries are available"""
        no_data_card = MDCard(orientation='vertical', padding=dp(15), radius=[15, 15, 15, 15], elevation=4, size_hint_y=None, height=dp(100), md_bg_color=rgba("#F5F5DC"))
        no_data_card.add_widget(MDLabel(text="No Diary Entries", theme_text_color="Primary"))
        no_data_card.add_widget(MDLabel(text="Add your first farming activity to start your diary!", theme_text_color="Secondary"))
        self.diary_layout.add_widget(no_data_card)

    def show_login_required_message(self):
        """Show message when user needs to log in"""
        login_card = MDCard(orientation='vertical', padding=dp(15), radius=[15, 15, 15, 15], elevation=4, size_hint_y=None, height=dp(100), md_bg_color=rgba("#FFE6E6"))
        login_card.add_widget(MDLabel(text="Login Required", theme_text_color="Primary"))
        login_card.add_widget(MDLabel(text="Please log in to view your farming diary.", theme_text_color="Secondary"))
        self.diary_layout.add_widget(login_card)

    # ===== FARMING DIARY METHODS =====

    def initialize_farming_tables(self):
        """Create farming diary tables if they don't exist"""
        try:
            # Create farming_activities table
            execute("""
                CREATE TABLE IF NOT EXISTS farming_activities (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) NOT NULL,
                    activity_type ENUM('planting', 'harvesting', 'expense', 'income', 'treatment', 'other') NOT NULL,
                    crop_type VARCHAR(100),
                    quantity DECIMAL(10,2),
                    quantity_unit VARCHAR(20),
                    amount DECIMAL(10,2),
                    description TEXT,
                    notes TEXT,
                    activity_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_email (email),
                    INDEX idx_date (activity_date),
                    INDEX idx_type (activity_type)
                )
            """)
        except Exception as e:
            print(f"Error creating farming tables: {e}")

    def get_total_plantings(self, email):
        """Get total number of planting activities"""
        try:
            result = fetch_all("SELECT COUNT(*) as total FROM farming_activities WHERE email=%s AND activity_type='planting'", (email,))
            return result[0]['total'] if result else 0
        except:
            return 0

    def get_total_harvests(self, email):
        """Get total harvest quantity"""
        try:
            result = fetch_all("SELECT SUM(quantity) as total FROM farming_activities WHERE email=%s AND activity_type='harvesting'", (email,))
            return result[0]['total'] or 0
        except:
            return 0

    def get_total_expenses(self, email):
        """Get total expenses"""
        try:
            result = fetch_all("SELECT SUM(amount) as total FROM farming_activities WHERE email=%s AND activity_type IN ('expense', 'treatment')", (email,))
            return result[0]['total'] or 0
        except:
            return 0

    def get_total_profits(self, email):
        """Get net profit (income - expenses)"""
        try:
            income_result = fetch_all("SELECT SUM(amount) as total FROM farming_activities WHERE email=%s AND activity_type='income'", (email,))
            expense_result = fetch_all("SELECT SUM(amount) as total FROM farming_activities WHERE email=%s AND activity_type IN ('expense', 'treatment')", (email,))

            income = income_result[0]['total'] or 0
            expenses = expense_result[0]['total'] or 0
            return income - expenses
        except:
            return 0

    def load_diary_entries(self):
        """Load and display farming diary entries"""
        try:
            app = App.get_running_app()
            email = getattr(app, 'current_user_email', None)

            if not email:
                self.show_login_required_message()
                return

            # Build query based on current filter
            query = "SELECT * FROM farming_activities WHERE email=%s"
            params = [email]

            if self.current_filter != "all":
                query += " AND activity_type=%s"
                params.append(self.current_filter)

            query += " ORDER BY activity_date DESC, created_at DESC"

            entries = fetch_all(query, tuple(params))

            # Clear existing entries
            self.diary_layout.clear_widgets()

            if not entries:
                self.show_no_diary_entries()
                return

            # Create entry cards
            for entry in entries:
                self.create_diary_entry_card(entry)

        except Exception as e:
            print(f"Diary loading error: {e}")
            self.show_no_diary_entries()

    def create_diary_entry_card(self, entry):
        """Create a card for a diary entry"""
        card = MDCard(orientation='vertical', padding=dp(15), radius=[15, 15, 15, 15], elevation=3, size_hint_y=None, height=dp(150), md_bg_color=self.get_activity_color(entry['activity_type']))

        # Header with date and type
        header = MDBoxLayout(size_hint_y=None, height=dp(30))
        date_label = MDLabel(text=entry['activity_date'].strftime('%d %b %Y'), theme_text_color="Primary", size_hint_x=0.6)
        type_label = MDLabel(text=entry['activity_type'].title(), theme_text_color="Secondary", size_hint_x=0.4, halign="right")
        header.add_widget(date_label)
        header.add_widget(type_label)
        card.add_widget(header)

        # Main content
        if entry['crop_type']:
            crop_label = MDLabel(text=f"Crop: {entry['crop_type']}", theme_text_color="Secondary")
            card.add_widget(crop_label)

        if entry['quantity'] and entry['quantity_unit']:
            quantity_label = MDLabel(text=f"Quantity: {entry['quantity']} {entry['quantity_unit']}", theme_text_color="Secondary")
            card.add_widget(quantity_label)

        if entry['amount']:
            amount_label = MDLabel(text=f"Amount: KSh {entry['amount']}", theme_text_color="Secondary")
            card.add_widget(amount_label)

        if entry['description']:
            desc_label = MDLabel(text=entry['description'], theme_text_color="Secondary", max_lines=2)
            card.add_widget(desc_label)

        self.diary_layout.add_widget(card)

    def get_activity_color(self, activity_type):
        """Get color for different activity types"""
        colors = {
            'planting': rgba("#E6F3FF"),  # Light blue
            'harvesting': rgba("#E6FFE6"),  # Light green
            'expense': rgba("#FFE6E6"),  # Light red
            'income': rgba("#FFF5E6"),  # Light orange
            'treatment': rgba("#F0E6FF"),  # Light purple
            'other': rgba("#F5F5F5")  # Light gray
        }
        return colors.get(activity_type, rgba("#F5F5F5"))

    def show_no_diary_entries(self):
        """Show message when no diary entries exist"""
        no_entries_card = MDCard(orientation='vertical', padding=dp(15), radius=[15, 15, 15, 15], elevation=4, size_hint_y=None, height=dp(120), md_bg_color=rgba("#F5F5DC"))
        no_entries_card.add_widget(MDLabel(text="No Diary Entries", theme_text_color="Primary"))
        no_entries_card.add_widget(MDLabel(text="Tap the + button to add your first farming activity!", theme_text_color="Secondary"))
        self.diary_layout.add_widget(no_entries_card)

    def show_filter_menu(self, instance):
        """Show filter menu for activity types"""
        menu_items = [
            {"text": "All Activities", "viewclass": "OneLineListItem", "on_release": lambda: self.set_filter("all")},
            {"text": "Planting", "viewclass": "OneLineListItem", "on_release": lambda: self.set_filter("planting")},
            {"text": "Harvesting", "viewclass": "OneLineListItem", "on_release": lambda: self.set_filter("harvesting")},
            {"text": "Expenses", "viewclass": "OneLineListItem", "on_release": lambda: self.set_filter("expense")},
            {"text": "Income", "viewclass": "OneLineListItem", "on_release": lambda: self.set_filter("income")},
            {"text": "Treatment", "viewclass": "OneLineListItem", "on_release": lambda: self.set_filter("treatment")},
        ]

        self.filter_menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=4,
        )
        self.filter_menu.open()

    def set_filter(self, filter_type):
        """Set the current filter and reload entries"""
        self.current_filter = filter_type
        filter_names = {
            "all": "All Activities",
            "planting": "Planting Activities",
            "harvesting": "Harvesting Activities",
            "expense": "Expenses",
            "income": "Income",
            "treatment": "Treatments"
        }
        self.filter_label.text = filter_names.get(filter_type, "All Activities")
        self.load_diary_entries()
        if self.filter_menu:
            self.filter_menu.dismiss()

    def clear_filters(self, instance):
        """Clear all filters"""
        self.current_filter = "all"
        self.filter_label.text = "All Activities"
        self.load_diary_entries()

    def show_add_entry_dialog(self, instance):
        """Show dialog to add new diary entry"""
        # Create popup content
        content = MDBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20), size_hint_y=None, height=dp(500))

        # Activity type dropdown
        activity_layout = MDBoxLayout(size_hint_y=None, height=dp(50))
        self.activity_text = MDTextField(
            hint_text="Select Activity Type",
            readonly=True,
            size_hint_x=0.7
        )
        activity_btn = MDButton(
            on_release=self.show_activity_menu,
            size_hint_x=0.3
        )
        activity_btn.text = "Select"
        activity_btn.color = (1, 1, 1, 1)
        activity_btn.md_bg_color = (0.4, 0.6, 0.4, 1)
        activity_layout.add_widget(self.activity_text)
        activity_layout.add_widget(activity_btn)
        content.add_widget(activity_layout)

        # Date picker
        date_layout = MDBoxLayout(size_hint_y=None, height=dp(50))
        self.date_text = MDTextField(hint_text="Select Date", readonly=True, size_hint_x=0.7)
        date_btn = MDButton(on_release=self.show_date_picker, size_hint_x=0.3)
        date_btn.text = "Pick Date"
        date_btn.color = (1, 1, 1, 1)
        date_btn.md_bg_color = (0.4, 0.6, 0.8, 1)
        date_layout.add_widget(self.date_text)
        date_layout.add_widget(date_btn)
        content.add_widget(date_layout)

        # Crop type
        self.crop_text = MDTextField(hint_text="Crop Type (optional)")
        content.add_widget(self.crop_text)

        # Quantity
        quantity_layout = MDBoxLayout(size_hint_y=None, height=dp(50))
        self.quantity_text = MDTextField(hint_text="Quantity (optional)", input_filter="float", size_hint_x=0.6)
        self.unit_text = MDTextField(hint_text="Unit", readonly=True, size_hint_x=0.4)
        unit_btn = MDButton(on_release=self.show_unit_menu, size_hint_x=None, width=dp(60))
        unit_btn.text = "Unit"
        unit_btn.color = (1, 1, 1, 1)
        unit_btn.md_bg_color = (0.6, 0.4, 0.6, 1)
        quantity_layout.add_widget(self.quantity_text)
        quantity_layout.add_widget(self.unit_text)
        quantity_layout.add_widget(unit_btn)
        content.add_widget(quantity_layout)

        # Amount
        self.amount_text = MDTextField(hint_text="Amount in KSh (optional)", input_filter="float")
        content.add_widget(self.amount_text)

        # Description
        self.description_text = MDTextField(hint_text="Description", multiline=True, max_height=dp(100))
        content.add_widget(self.description_text)

        # Buttons
        buttons_layout = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        cancel_btn = MDButton(on_release=lambda x: popup.dismiss())
        cancel_btn.text = "Cancel"
        cancel_btn.color = (1, 1, 1, 1)
        save_btn = MDButton(on_release=lambda x: self.save_diary_entry(x, popup), md_bg_color=rgba("#4CAF50"))
        save_btn.text = "Save"
        save_btn.color = (1, 1, 1, 1)
        buttons_layout.add_widget(cancel_btn)
        buttons_layout.add_widget(save_btn)
        content.add_widget(buttons_layout)

        popup = Popup(title="Add Farming Activity", content=content, size_hint=(0.9, 0.9))
        popup.open()

    def show_activity_menu(self, instance):
        """Show activity type selection menu"""
        menu_items = [
            {
                "text": "Planting",
                "on_release": lambda x="planting": self.set_activity_type(x),
            },
            {
                "text": "Harvesting",
                "on_release": lambda x="harvesting": self.set_activity_type(x),
            },
            {
                "text": "Expense",
                "on_release": lambda x="expense": self.set_activity_type(x),
            },
            {
                "text": "Income",
                "on_release": lambda x="income": self.set_activity_type(x),
            },
            {
                "text": "Treatment",
                "on_release": lambda x="treatment": self.set_activity_type(x),
            },
            {
                "text": "Other",
                "on_release": lambda x="other": self.set_activity_type(x),
            },
        ]

        MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=4,
        ).open()

    def set_activity_type(self, activity_type):
        """Set the selected activity type"""
        self.activity_text.text = activity_type.title()

    def show_unit_menu(self, instance):
        """Show unit type selection menu"""
        menu_items = [
            {
                "text": "kg",
                "on_release": lambda x="kg": self.set_unit_type(x),
            },
            {
                "text": "tons",
                "on_release": lambda x="tons": self.set_unit_type(x),
            },
            {
                "text": "liters",
                "on_release": lambda x="liters": self.set_unit_type(x),
            },
            {
                "text": "bags",
                "on_release": lambda x="bags": self.set_unit_type(x),
            },
            {
                "text": "plants",
                "on_release": lambda x="plants": self.set_unit_type(x),
            },
            {
                "text": "acres",
                "on_release": lambda x="acres": self.set_unit_type(x),
            },
        ]

        MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=4,
        ).open()

    def set_unit_type(self, unit_type):
        """Set the selected unit type"""
        self.unit_text.text = unit_type

    def show_date_picker(self, instance):
        """Show simple date input dialog"""
        content = MDBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20), size_hint_y=None, height=dp(200))

        # Year, Month, Day inputs
        inputs_layout = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        self.year_input = MDTextField(hint_text="Year (2024)", input_filter="int", size_hint_x=0.3)
        self.month_input = MDTextField(hint_text="Month (01-12)", input_filter="int", size_hint_x=0.35)
        self.day_input = MDTextField(hint_text="Day (01-31)", input_filter="int", size_hint_x=0.35)

        # Set default to today
        today = datetime.now()
        self.year_input.text = str(today.year)
        self.month_input.text = f"{today.month:02d}"
        self.day_input.text = f"{today.day:02d}"

        inputs_layout.add_widget(self.year_input)
        inputs_layout.add_widget(self.month_input)
        inputs_layout.add_widget(self.day_input)
        content.add_widget(inputs_layout)

        # Buttons
        buttons_layout = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        cancel_btn = MDButton(on_release=lambda x: date_popup.dismiss())
        cancel_btn.text = "Cancel"
        cancel_btn.color = (1, 1, 1, 1)
        ok_btn = MDButton(on_release=lambda x: self.set_date_from_inputs(x, date_popup), md_bg_color=rgba("#4CAF50"))
        ok_btn.text = "OK"
        ok_btn.color = (1, 1, 1, 1)
        buttons_layout.add_widget(cancel_btn)
        buttons_layout.add_widget(ok_btn)
        content.add_widget(buttons_layout)

        date_popup = Popup(title="Select Date", content=content, size_hint=(0.8, 0.5))
        date_popup.open()

    def set_date_from_inputs(self, instance, popup):
        """Set date from input fields"""
        try:
            year = int(self.year_input.text)
            month = int(self.month_input.text)
            day = int(self.day_input.text)

            # Validate date
            if not (1 <= month <= 12):
                raise ValueError("Invalid month")
            if not (1 <= day <= 31):
                raise ValueError("Invalid day")
            if not (2020 <= year <= 2030):
                raise ValueError("Invalid year")

            date_str = f"{year}-{month:02d}-{day:02d}"
            self.date_text.text = date_str
            popup.dismiss()  # Close popup

        except ValueError as e:
            error_popup = Popup(title="Invalid Date", content=Label(text=f"Please enter valid date values.\n{str(e)}"), size_hint=(0.6, 0.3))
            error_popup.open()

    def save_diary_entry(self, instance, popup):
        """Save new diary entry to database"""
        try:
            app = App.get_running_app()
            email = getattr(app, 'current_user_email', None)

            if not email:
                return

            # Validate required fields
            if not self.activity_text.text or self.activity_text.text == "Select Activity Type":
                return

            if not self.date_text.text:
                self.date_text.text = datetime.now().strftime('%Y-%m-%d')

            # Prepare data
            data = {
                'email': email,
                'activity_type': self.activity_text.text,
                'crop_type': self.crop_text.text.strip() or None,
                'quantity': float(self.quantity_text.text) if self.quantity_text.text else None,
                'quantity_unit': self.unit_text.text if self.unit_text.text else None,
                'amount': float(self.amount_text.text) if self.amount_text.text else None,
                'description': self.description_text.text.strip() or None,
                'activity_date': self.date_text.text
            }

            # Insert into database
            execute("""
                INSERT INTO farming_activities
                (email, activity_type, crop_type, quantity, quantity_unit, amount, description, activity_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['email'], data['activity_type'], data['crop_type'], data['quantity'],
                data['quantity_unit'], data['amount'], data['description'], data['activity_date']
            ))

            # Close popup and refresh
            popup.dismiss()  # Close the popup
            self.load_diary_entries()  # Refresh the diary entries
            self.create_summary_cards()  # Refresh summary cards

        except Exception as e:
            print(f"Error saving diary entry: {e}")
            # Show error popup
            error_popup = Popup(title="Error", content=Label(text=f"Could not save entry: {e}"), size_hint=(0.6, 0.3))
            error_popup.open()
