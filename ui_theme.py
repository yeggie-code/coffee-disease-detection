# Unified UI Theme for Coffee Disease Detection App
from kivy.utils import rgba
from kivy.metrics import dp

class AppTheme:
    """Centralized theme colors and styling for consistent UI across all screens"""
    
    # Primary Colors
    PRIMARY_COLOR = rgba("#4CAF50")  # Green
    PRIMARY_DARK = rgba("#388E3C")  # Dark Green
    PRIMARY_LIGHT = rgba("#C8E6C9")  # Light Green
    
    # Accent Colors
    ACCENT_COLOR = rgba("#FF9800")  # Orange
    ACCENT_LIGHT = rgba("#FFE0B2")  # Light Orange
    
    # Secondary Colors
    SECONDARY_COLOR = rgba("#2196F3")  # Blue
    SECONDARY_DARK = rgba("#1565C0")  # Dark Blue
    SECONDARY_LIGHT = rgba("#E3F2FD")  # Light Blue
    
    # Neutral Colors
    BACKGROUND_DARK = rgba("#1B1B1B")  # Dark background
    BACKGROUND_LIGHT = rgba("#F5F5F5")  # Light background
    CARD_BACKGROUND = rgba("#2E2E2E")  # Card background
    TEXT_PRIMARY = (1, 1, 1, 1)  # White text
    TEXT_SECONDARY = (0.7, 0.7, 0.7, 1)  # Gray text
    TEXT_DARK = (0.1, 0.1, 0.1, 1)  # Dark text
    
    # Error/Status Colors
    ERROR_COLOR = rgba("#F44336")  # Red
    SUCCESS_COLOR = rgba("#4CAF50")  # Green
    WARNING_COLOR = rgba("#FF9800")  # Orange
    
    # Sizes
    TOP_BAR_HEIGHT = dp(50)
    CARD_RADIUS = [15, 15, 15, 15]
    SPACING_SMALL = dp(8)
    SPACING_MEDIUM = dp(12)
    SPACING_LARGE = dp(20)
    PADDING_STANDARD = dp(15)
    
    # Button sizes
    BUTTON_HEIGHT = dp(45)
    ICON_BUTTON_SIZE = "28sp"
    
    # Font Sizes
    FONT_SIZE_TITLE = "24sp"          # Page titles
    FONT_SIZE_SUBTITLE = "18sp"       # Subtitles
    FONT_SIZE_HEADING = "16sp"        # Card headings
    FONT_SIZE_BODY = "14sp"           # Body text
    FONT_SIZE_CAPTION = "12sp"        # Small/caption text
    
    # Label Heights (for proper text sizing)
    LABEL_HEIGHT_TITLE = dp(50)       # Title labels
    LABEL_HEIGHT_HEADING = dp(45)     # Heading labels
    LABEL_HEIGHT_BODY = dp(40)        # Regular labels
    LABEL_HEIGHT_CAPTION = dp(30)     # Small labels
    
    @staticmethod
    def get_top_bar_style():
        """Returns standard top bar styling"""
        return {
            'size_hint_y': None,
            'height': AppTheme.TOP_BAR_HEIGHT,
            'padding': dp(10),
            'spacing': dp(10),
            'md_bg_color': AppTheme.PRIMARY_COLOR
        }
    
    @staticmethod
    def get_card_style():
        """Returns standard card styling"""
        return {
            'radius': AppTheme.CARD_RADIUS,
            'md_bg_color': AppTheme.CARD_BACKGROUND,
            'elevation': 4,
            'padding': AppTheme.PADDING_STANDARD,
            'size_hint_y': None,
        }
    
    @staticmethod
    def get_icon_button_style():
        """Returns standard icon button styling"""
        return {
            'icon_size': AppTheme.ICON_BUTTON_SIZE,
        }
