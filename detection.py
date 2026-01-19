from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.app import App
from plyer import filechooser
import numpy as np
import json
import os
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as kimage
from db import get_connection
from ui_theme import AppTheme

# Local translation dictionary for coffee disease remedies
REMEDY_TRANSLATIONS = {
    "Swahili": {
        "1. Remove affected leaves and burn them": "1. Ondoa majani yaliyoathiriwa na kuchemsha",
        "2. Apply fungicide (e.g., copper-based)": "2. Tumia kinga ya fungus (kwa mfano, iliyofanywa na shaba)",
        "3. Improve air circulation by pruning": "3. Boresha upepo kwa kupunguza matawi",
        "4. Avoid overhead watering": "4. Kuepuka kumwagilia kutoka juu",
        "Remove affected leaves": "Ondoa majani yaliyoathiriwa",
        "Apply fungicide spray": "Tumia kinga ya fungus",
        "Remove infected leaves immediately": "Ondoa majani yaliyoambukizwa haraka",
        "Use sulfur-based fungicides": "Tumia kinga ya fungus inayofanywa na sulfuri"
    },
    "Kamba": {
        "1. Remove affected leaves and burn them": "1. Tua mitwe iyata i na gweka moto",
        "2. Apply fungicide (e.g., copper-based)": "2. Asa akitune ngiti (komba)",
        "3. Improve air circulation by pruning": "3. Asa mpepo mwema kwa nguvu miti",
        "4. Avoid overhead watering": "4. Tika kumwagia maji itakua"
    },
    "Kikuyu": {
        "1. Remove affected leaves and burn them": "1. Thaai mahoya mabatukire na mahura",
        "2. Apply fungicide (e.g., copper-based)": "2. Hoya ndurume cia mahoya (ibuku)",
        "3. Improve air circulation by pruning": "3. Thikinira mwaki cia mahoya",
        "4. Avoid overhead watering": "4. Tikira gwatikie maji"
    },
    "Luo": {
        "1. Remove affected leaves and burn them": "1. Chiemo alode ma jothieth kendo picho",
        "2. Apply fungicide (e.g., copper-based)": "2. Joto rem mar jothieth",
        "3. Improve air circulation by pruning": "3. Ranyisi wich piyo",
        "4. Avoid overhead watering": "4. Tieko kumwagi mondo chip"
    }
}

# Load the KV file
Builder.load_file('detection.kv')

class DetectionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.selected_file = None

        # Paths
        self.saved_model_dir = r"C:\Users\Administrator\Desktop\project\saved_model\plant_disease_mobilenet"
        self.keras_h5_path = os.path.join(self.saved_model_dir, "best_model.h5")
        self.tflite_path = os.path.join(self.saved_model_dir, "model.tflite")
        self.labels_path = os.path.join(self.saved_model_dir, "labels.json")

        # Model and labels
        self.model = None
        self.tflite_interpreter = None
        self.class_names = ["miner", "nodisease", "other", "phoma", "rust"]

        # Conversation for chat
        self.conversation = []

        # Attempt to load model and labels
        self._load_model_and_labels()

    def go_back(self):
        """Navigate back to dashboard screen"""
        if self.manager:
            self.manager.current = "dashboard"
        else:
            popup = Popup(title='Navigation Error', content=Label(text='Screen manager not found.'), size_hint=(0.6, 0.3))
            popup.open()

    def take_photo(self):
        """Take a photo using device camera"""
        try:
            from plyer import camera
        except ImportError:
            camera = None

        if camera is not None:
            try:
                # Save to a temporary file
                import tempfile
                tmpfile = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                tmpfile.close()
                camera.take_picture(filename=tmpfile.name, on_complete=lambda path: self.on_photo_taken(path))
            except Exception as e:
                popup = Popup(title='Camera Error', content=Label(text=f'Camera error: {e}'), size_hint=(0.7, 0.3))
                popup.open()
        else:
            popup = Popup(title='Camera Not Available', content=Label(text='Camera functionality is not available on this platform.'), size_hint=(0.7, 0.3))
            popup.open()

    def on_photo_taken(self, path):
        """Handle photo taken callback"""
        if path and os.path.exists(path):
            self.selected_file = path
            self.ids.image_preview.source = self.selected_file
            self.ids.image_preview.reload()
            self.ids.result_label.text = "Photo taken. Ready to detect."
        else:
            popup = Popup(title='Photo Error', content=Label(text='Failed to take photo.'), size_hint=(0.7, 0.3))
            popup.open()

    def choose_file(self):
        """Open file chooser to select image"""
        file_path = filechooser.open_file(title="Pick an image", filters=[("Image files", "*.jpg;*.png")])
        if file_path:
            self.selected_file = file_path[0]
            self.ids.image_preview.source = self.selected_file
            self.ids.image_preview.reload()
            self.ids.result_label.text = "Image loaded. Ready to detect."

    def detect_disease(self):
        """Detect disease in selected image"""
        if not self.selected_file:
            self.ids.result_label.text = "Please upload an image first!"
            return

        # Load image for model
        img = kimage.load_img(self.selected_file, target_size=(224, 224))
        img_array = kimage.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0

        # Predict (Keras or TFLite)
        try:
            if self.model is not None:
                probs = self.model.predict(img_array)[0]
            elif self.tflite_interpreter is not None:
                input_details = self.tflite_interpreter.get_input_details()
                output_details = self.tflite_interpreter.get_output_details()
                # Prepare input according to interpreter dtype
                input_index = input_details[0]["index"]
                input_dtype = input_details[0]["dtype"]
                input_data = img_array.astype(input_dtype)
                self.tflite_interpreter.set_tensor(input_index, input_data)
                self.tflite_interpreter.invoke()
                probs = self.tflite_interpreter.get_tensor(output_details[0]["index"])[0]
            else:
                self.ids.result_label.text = "No model loaded. Check model files."
                return

        except Exception as e:
            self.ids.result_label.text = f"Prediction error: {e}"
            return

        # Get predicted class and confidence
        class_idx = int(np.argmax(probs))
        confidence = float(probs[class_idx])

        # Debug: print all probabilities
        print(f"Model predictions: {dict(zip(self.class_names, probs))}")
        print(f"Predicted class index: {class_idx}, confidence: {confidence:.4f}")

        # Ensure class_names length matches
        if class_idx < len(self.class_names):
            detected_class = self.class_names[class_idx]
        else:
            detected_class = f"class_{class_idx}"

        # Only show the best result, with special handling for 'other' class (class 4 or named 'other')
        if detected_class.lower() == "other" or class_idx == 4:
            self.ids.result_label.text = "The above photo cannot be recognized as a coffee leaf."
            self.ids.translate_button.disabled = True
            self.last_remedies = None
            # Save to history
            self.save_to_history(detected_class, "Image not recognized as coffee leaf", self.selected_file)
        elif detected_class.lower() == "nodisease":
            self.ids.result_label.text = "The leaf appears to be healthy with no visible disease."
            self.ids.translate_button.disabled = True
            self.last_remedies = None
            # Save to history
            self.save_to_history(detected_class, "No disease detected - leaf is healthy", self.selected_file)
        else:
            # Get remedies from Gemini API or local fallback
            remedies = self.get_remedies_from_gemini(detected_class)

            # Show remedies in original language (usually English)
            result_text = f"The disease predicted here is {detected_class}."
            if remedies:
                result_text += f"\nRemedies: {remedies}"
            self.ids.result_label.text = result_text

            # Store last remedies so Translate button can use them
            self.last_remedies = remedies
            self.last_disease = detected_class
            
            # Enable translate button for detected diseases
            self.ids.translate_button.disabled = False

            # Save to history
            self.save_to_history(detected_class, remedies, self.selected_file)

            # Enable advanced analysis and export buttons
            self.ids.analysis_button.disabled = False
            self.ids.export_button.disabled = False

            # Show confidence meter
            self.ids.confidence_card.opacity = 1
            self.ids.confidence_bar.value = confidence * 100
            self.ids.confidence_text.text = f"Confidence: {confidence:.1%}"

            # Enable chat
            self.enable_chat()

    def get_remedies_from_gemini(self, disease_name):
        """
        Gets remedies for coffee leaf disease from local database.
        Uses Groq API if needed, but defaults to local fallback.
        """
        # Fallback to local remedy database
        local_remedies = {
            "miner": "1. Remove affected leaves and burn them\n2. Apply fungicide (e.g., copper-based)\n3. Improve air circulation by pruning\n4. Avoid overhead watering",
            "nodisease": "No treatment needed - the leaf is healthy!",
            "phoma": "1. Prune infected branches\n2. Apply fungicide spray\n3. Maintain proper spacing between plants\n4. Sterilize pruning tools",
            "rust": "1. Remove infected leaves immediately\n2. Use sulfur-based fungicides\n3. Increase air circulation\n4. Avoid wet foliage during watering",
            "other": "Unable to identify the specific disease. Please consult a local agricultural expert for proper diagnosis."
        }

        disease_lower = disease_name.lower().strip()
        if disease_lower in local_remedies:
            return local_remedies[disease_lower]

        # Final fallback: generic remedies
        return f"General remedies for {disease_name}:\n1. Remove affected parts\n2. Apply fungicide\n3. Improve plant spacing for air circulation\n4. Avoid overhead watering"

    def translate_current(self):
        """Translate last_remedies into user's preferred language and update UI."""
        if not getattr(self, 'last_remedies', None):
            popup = Popup(title='Translate', content=Label(text='No remedies to translate.'), size_hint=(0.6, 0.3))
            popup.open()
            return

        try:
            app = App.get_running_app()
            user_lang = getattr(app, 'current_user_language', None)
        except Exception:
            user_lang = None

        if not user_lang or user_lang.lower() == 'english':
            popup = Popup(title='Translate', content=Label(text='Preferred language is English or not set.'), size_hint=(0.6, 0.3))
            popup.open()
            return

        translated = self.translate_remedies(self.last_remedies, user_lang)
        # Update label to show translated remedies (keep disease line)
        # Extract disease line from current label if present
        lines = self.ids.result_label.text.split('\n')
        header = lines[0] if lines else ''
        new_text = header + '\nRemedies: ' + translated
        self.ids.result_label.text = new_text
        self.ids.translate_button.disabled = True

    def enable_chat(self):
        """Enable chat functionality"""
        self.ids.chat_card.opacity = 1
        self.ids.chat_input_container.opacity = 1
        self.ids.send_button.disabled = False
        # Add initial message
        self.add_chat_message("You can now ask questions about the disease or remedies.")

    def add_chat_message(self, message, sender="AI"):
        """Add a message to the chat"""
        from kivy.uix.label import Label
        label = Label(text=f"{sender}: {message}",
                     color=(0.1, 0.3, 0.1, 1) if sender == "AI" else (0.4, 0.2, 0.1, 1),
                     halign='left',
                     size_hint_y=None,
                     height=40,
                     font_size='13sp')
        label.bind(size=label.setter('text_size'))
        self.ids.chat_container.add_widget(label)
        self.conversation.append({"sender": sender, "message": message})

    def send_question(self):
        """Send user question to AI assistant"""
        question = self.ids.chat_input.text.strip()
        if not question:
            return
        self.add_chat_message(question, "User")
        self.ids.chat_input.text = ""
        # Get response from Gemini
        response = self.ask_gemini(question)
        self.add_chat_message(response, "AI")
        # Update history
        self.update_history_with_chat()

    def ask_gemini(self, question):
        """Get response about coffee diseases based on question keywords"""
        q = question.lower()
        
        if any(w in q for w in ["miner", "leaf miner", "clm"]):
            return "Coffee Leaf Miner (CLM) creates tunnels in leaves. Remove infected leaves, use sticky traps, and apply insecticides if needed. Proper sanitation is essential."
        elif any(w in q for w in ["rust", "orange", "powder", "fungal"]):
            return "Leaf Rust causes orange-brown pustules. Remove affected leaves, improve airflow, apply sulfur fungicides, and avoid overhead watering. It thrives in humid conditions."
        elif any(w in q for w in ["phoma", "brown", "spot", "necrosis"]):
            return "Phoma causes brown spots on leaves. Remove and destroy infected leaves, apply fungicides, sterilize tools, and maintain good sanitation practices."
        elif any(w in q for w in ["prevent", "prevention", "avoid", "protect"]):
            return "Prevent disease by maintaining good spacing, avoiding overhead watering, removing fallen leaves, pruning regularly, and monitoring for early signs. Use disease-resistant varieties when possible."
        elif any(w in q for w in ["fungicide", "treatment", "spray", "pesticide"]):
            return "Apply fungicides when disease appears. Copper-based products for miners, sulfur for rust. Always follow label directions and apply during dry conditions for best results."
        else:
            return "Coffee diseases require proper management. The remedies shown focus on removing affected parts, improving air circulation, and applying appropriate treatments. Ask about specific diseases or prevention methods."

    def translate_remedies(self, remedies_text, target_lang):
        """Translate remedies text to target language using local dictionary"""
        if not remedies_text or target_lang == "English":
            return remedies_text
        
        if target_lang not in REMEDY_TRANSLATIONS:
            return remedies_text
        
        translation_dict = REMEDY_TRANSLATIONS[target_lang]
        translated_text = remedies_text
        
        for english, translated in translation_dict.items():
            translated_text = translated_text.replace(english, translated)
        
        return translated_text

    def update_history_with_chat(self):
        """Update the last history entry with conversations"""
        try:
            import json
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE history SET conversations=%s WHERE email=%s ORDER BY created_at DESC LIMIT 1",
                       (json.dumps(self.conversation), App.get_running_app().current_user_email))
            conn.commit()
            conn.close()
        except Exception as e:
            print("Update history error:", e)

    def _load_model_and_labels(self):
        """Load model and labels from saved files"""
        # Load labels if available
        try:
            if os.path.exists(self.labels_path):
                with open(self.labels_path, 'r') as f:
                    labels_map = json.load(f)
                # labels_map: class_name -> index; invert to list by index
                inv = [None] * (max(labels_map.values()) + 1)
                for name, idx in labels_map.items():
                    inv[idx] = name
                self.class_names = inv
        except Exception:
            pass

        # Try to load Keras .h5
        try:
            if os.path.exists(self.keras_h5_path):
                self.model = load_model(self.keras_h5_path)
                return
        except Exception:
            self.model = None

        # Try to load SavedModel directory
        try:
            saved_model_dir = os.path.join(self.saved_model_dir, 'SavedModel')
            if os.path.isdir(saved_model_dir):
                self.model = tf.keras.models.load_model(saved_model_dir)
                return
        except Exception:
            self.model = None

        # Fallback: try TFLite interpreter
        try:
            if os.path.exists(self.tflite_path):
                self.tflite_interpreter = tf.lite.Interpreter(model_path=self.tflite_path)
                self.tflite_interpreter.allocate_tensors()
                return
        except Exception:
            self.tflite_interpreter = None

        # If nothing loaded, leave model as None
        return

    def save_to_history(self, disease, advice, image_path):
        """Save detection result to history"""
        try:
            from kivy.app import App
            app = App.get_running_app()
            email = app.current_user_email
            if email:
                from db import execute
                execute("INSERT INTO history (email, disease, advice, image_path, conversations) VALUES (%s, %s, %s, %s, %s)",
                        (email, disease, advice, image_path, json.dumps(self.conversation)))
        except Exception as e:
            print("Save to history error:", e)

    def show_advanced_analysis(self):
        """Show advanced image analysis popup"""
        if not self.selected_file:
            popup = Popup(title='No Image', content=Label(text='Please upload an image first.'), size_hint=(0.6, 0.3))
            popup.open()
            return

        # Analyze image properties
        try:
            from PIL import Image as PILImage
            import numpy as np

            img = PILImage.open(self.selected_file)
            img_array = np.array(img)

            # Calculate brightness
            brightness = np.mean(img_array) / 255.0

            # Calculate contrast
            contrast = img_array.std() / 255.0

            # Get image dimensions
            width, height = img.size

            # Mock weather data (in real app, would fetch from API)
            weather_info = "Temperature: 25°C, Humidity: 70%, Rain: Low risk"

            analysis_text = f"""Advanced Image Analysis:

Image Quality: {'Good' if brightness > 0.3 and brightness < 0.8 else 'Poor (too dark/bright)'}
Brightness: {brightness:.2%}
Contrast: {contrast:.2%}
Resolution: {width}x{height}

Environmental Factors:
{weather_info}

Recommendations:
• {'Good lighting conditions' if 0.3 < brightness < 0.8 else 'Adjust lighting for better image quality'}
• {'Image contrast is adequate' if contrast > 0.2 else 'Consider retaking photo with better contrast'}
• {'Weather conditions favorable for analysis' if 'Low risk' in weather_info else 'Monitor weather conditions'}"""

            popup = Popup(title='Advanced Analysis', content=Label(text=analysis_text, halign='left', valign='top'), size_hint=(0.8, 0.7))
            popup.open()

        except Exception as e:
            popup = Popup(title='Analysis Error', content=Label(text=f'Could not analyze image: {e}'), size_hint=(0.6, 0.3))
            popup.open()

    def export_report(self):
        """Export detection report to file"""
        if not hasattr(self, 'last_disease') or not self.last_disease:
            popup = Popup(title='No Report', content=Label(text='Please detect a disease first.'), size_hint=(0.6, 0.3))
            popup.open()
            return

        try:
            from datetime import datetime
            import os

            # Create report content
            report_content = f"""Coffee Leaf Disease Detection Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Disease Detected: {self.last_disease}
Confidence: {self.ids.confidence_bar.value:.1f}%

Remedies:
{self.last_remedies if self.last_remedies else 'No remedies available'}

Chat History:
{chr(10).join([f"{msg['sender']}: {msg['message']}" for msg in self.conversation]) if self.conversation else 'No chat history'}

---
Report generated by Coffee Disease Detection App
"""

            # Save to file
            from plyer import filechooser
            file_path = filechooser.save_file(title="Save Report", filters=[("Text files", "*.txt")])
            if file_path:
                with open(file_path[0], 'w') as f:
                    f.write(report_content)

                popup = Popup(title='Export Success', content=Label(text=f'Report saved to: {file_path[0]}'), size_hint=(0.6, 0.3))
                popup.open()

        except Exception as e:
            popup = Popup(title='Export Error', content=Label(text=f'Could not export report: {e}'), size_hint=(0.6, 0.3))
            popup.open()
