from kivy.uix.screenmanager import Screen
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.utils import rgba

from kivymd.uix.card import MDCard
from kivymd.uix.button import MDButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from ui_theme import AppTheme


class SellingScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Main container with background
        main_container = MDBoxLayout(orientation='vertical')
        
        # Background image
        with main_container.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(source='../assets/0db150166098c8e1bb1392a6904e63e3.jpg', pos=main_container.pos, size=main_container.size)
            main_container.bind(pos=self._update_bg, size=self._update_bg)

        root = MDBoxLayout(
            orientation="vertical",
            spacing=AppTheme.SPACING_MEDIUM,
            padding=AppTheme.PADDING_STANDARD
        )

        # --------------------------------------------------
        # TOP APP BAR WITH BACK BUTTON
        # --------------------------------------------------
        top_bar = MDBoxLayout(**AppTheme.get_top_bar_style())
        
        back_btn = MDIconButton(
            icon="arrow-left",
            **AppTheme.get_icon_button_style(),
            on_release=self.go_back
        )
        top_bar.add_widget(back_btn)
        
        title_label = MDLabel(
            text="Agricultural Products",
            halign="center",
            size_hint_x=1,
            color=AppTheme.TEXT_PRIMARY,
            size_hint_y=None,
            height=dp(50)
        )
        top_bar.add_widget(title_label)
        
        root.add_widget(top_bar)

        # --------------------------------------------------
        # SCROLLABLE PRODUCTS LIST
        # --------------------------------------------------
        scroll = ScrollView()

        products_layout = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(12),
            padding=dp(12)
        )

        # Sample products
        products = [
            {"name": "Organic Fertilizer", "price": "$25", "desc": "Boost your coffee plants."},
            {"name": "Pesticide Spray", "price": "$15", "desc": "Protects against pests."},
            {"name": "Pruning Tools", "price": "$40", "desc": "Essential crop tools."},
            {"name": "Irrigation System", "price": "$100", "desc": "Efficient watering solution."}
        ]

        for product in products:
            products_layout.add_widget(
                self.build_product_card(product)
            )

        scroll.add_widget(products_layout)
        root.add_widget(scroll)

        main_container.add_widget(root)
        self.add_widget(main_container)

    # --------------------------------------------------
    # PRODUCT CARD
    # --------------------------------------------------
    def build_product_card(self, product):

        card = MDCard(
            orientation="vertical",
            padding=dp(15),
            radius=[18, 18, 18, 18],
            elevation=3,
            size_hint_y=None,
            height=dp(150),
            md_bg_color=rgba("#F5F5DC")
        )

        card.add_widget(
            MDLabel(
                text=product["name"],
                halign="left",
                size_hint_y=None,
                height=dp(30)
            )
        )

        card.add_widget(
            MDLabel(
                text=product["desc"],
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(30)
            )
        )

        card.add_widget(
            MDLabel(
                text=f"Price: {product['price']}",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(25)
            )
        )

        buy_btn = MDButton(
            text="Buy Now",
            on_release=lambda x, p=product: self.buy_product(p),
            md_bg_color=rgba("#2196F3"),
            size_hint=(None, None),
            size=(dp(120), dp(40))
        )

        card.add_widget(buy_btn)

        return card

    # --------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------
    def go_back(self, instance=None):
        if self.manager:
            self.manager.current = "dashboard"
    
    def _update_bg(self, instance, value):
        """Update background rectangle position and size"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = instance.pos
            self.bg_rect.size = instance.size

    # --------------------------------------------------
    # BUY POPUP
    # --------------------------------------------------
    def buy_product(self, product):
        popup = Popup(
            title="Purchase",
            content=Label(
                text=f"Demo purchase for:\n\n{product['name']}",
                halign="center"
            ),
            size_hint=(0.7, 0.4)
        )
        popup.open()
