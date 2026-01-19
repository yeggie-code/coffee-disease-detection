from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.utils import rgba

from kivymd.uix.card import MDCard
from kivymd.uix.button import MDButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.appbar import MDTopAppBar

from db import get_connection
from ui_theme import AppTheme
import json

Builder.load_string("""
<HistoryScreen>:
    MDBoxLayout:
        orientation: "vertical"

        # Top bar with back button
        MDBoxLayout:
            size_hint_y: None
            height: dp(50)
            md_bg_color: rgba("#4CAF50")
            padding: dp(8)
            spacing: dp(8)

            MDIconButton:
                icon: "arrow-left"
                icon_size: "28sp"
                on_release: root.go_back()

            MDLabel:
                text: "Scan History"
                halign: "left"
                valign: "center"
                color: rgba("#FFFFFF")
                size_hint_y: None
                height: dp(50)

        ScrollView:
            MDBoxLayout:
                id: history_container
                orientation: "vertical"
                adaptive_height: True
                spacing: dp(12)
                padding: dp(12)
                md_bg_color: rgba("#F5F5F5")
""")

class HistoryScreen(Screen):

    # -----------------------
    # Navigation
    # -----------------------
    def go_back(self):
        if self.manager:
            self.manager.current = "dashboard"

    # -----------------------
    # Image Preview Popup
    # -----------------------
    def show_full_image(self, image_path):
        Popup(
            title="Image Preview",
            size_hint=(0.9, 0.9),
            content=Image(source=image_path, allow_stretch=True, keep_ratio=True)
        ).open()

    # -----------------------
    # Load History
    # -----------------------
    def on_pre_enter(self, *args):
        container = self.ids.history_container
        container.clear_widgets()

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """SELECT id, disease, advice, image_path, created_at, conversations
                   FROM history WHERE email=%s ORDER BY created_at DESC""",
                (App.get_running_app().current_user_email,)
            )
            rows = cur.fetchall()
            conn.close()

            if not rows:
                container.add_widget(
                    MDLabel(
                        text="No scan history found.\nStart scanning coffee leaves.",
                        halign="center",
                        size_hint_y=None,
                        height=dp(140)
                    )
                )
                return

            for rid, disease, advice, image_path, created_at, conversations in rows:
                container.add_widget(
                    self.build_card(rid, disease, advice, image_path, created_at, conversations)
                )

        except Exception as e:
            container.add_widget(
                MDLabel(
                    text=f"Error loading history:\n{e}",
                    halign="center",
                    text_color=(1, 0.4, 0.4, 1),
                    size_hint_y=None,
                    height=dp(80)
                )
            )

    # -----------------------
    # History Card
    # -----------------------
    def build_card(self, rid, disease, advice, image_path, created_at, conversations):

        card = MDCard(
            orientation="vertical",
            padding=dp(12),
            radius=[16, 16, 16, 16],
            elevation=3,
            size_hint_y=None,
            height=dp(420),
            md_bg_color=rgba("#FFFFFF")
        )

        if image_path:
            img = Image(
                source=image_path,
                size_hint=(1, None),
                height=dp(150),
                allow_stretch=True
            )
            img.bind(on_touch_down=lambda i, t, p=image_path:
                     self.show_full_image(p) if i.collide_point(*t.pos) else None)
            card.add_widget(img)

        info = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(200)
        )

        created_label = MDLabel(
            text=str(created_at),
            size_hint_y=None,
            height=dp(45),
            text_size=(None, None),
            markup=False,
            color=AppTheme.TEXT_SECONDARY
        )
        info.add_widget(created_label)
        
        disease_label = MDLabel(
            text=f"Disease: {disease}",
            size_hint_y=None,
            height=dp(50),
            text_size=(None, None),
            markup=False,
            bold=True,
            color=AppTheme.TEXT_PRIMARY
        )
        info.add_widget(disease_label)
        
        advice_label = MDLabel(
            text=f"Advice: {advice}",
            size_hint_y=None,
            height=dp(80),
            text_size=(None, None),
            markup=False,
            color=AppTheme.TEXT_PRIMARY
        )
        info.add_widget(advice_label)

        if conversations:
            try:
                conv = json.loads(conversations)
                if conv:
                    last = conv[-1]
                    chat_label = MDLabel(
                        text=f"Chat: {last['sender']}: {last['message']}",
                        size_hint_y=None,
                        height=dp(50),
                        text_size=(None, None),
                        markup=False,
                        color=AppTheme.TEXT_SECONDARY
                    )
                    info.add_widget(chat_label)
            except:
                pass

        card.add_widget(info)

        btns = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10), padding=dp(5))

        btns.add_widget(
            MDButton(
                text="View",
                md_bg_color=rgba(AppTheme.PRIMARY_COLOR),
                on_release=lambda x, p=image_path: self.show_full_image(p),
            )
        )

        btns.add_widget(
            MDButton(
                text="Delete",
                md_bg_color=rgba("#E53935"),
                on_release=lambda x, r=rid: self.delete_single(r)
            )
        )

        card.add_widget(btns)
        return card

    # -----------------------
    # Delete
    # -----------------------
    def delete_single(self, rid):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM history WHERE id=%s", (rid,))
            conn.commit()
            conn.close()
            self.on_pre_enter()
        except Exception as e:
            print("Delete error:", e)
