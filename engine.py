import random

class CoffeeAdviceEngine:

    def __init__(self):
        # Coffee-specific advice database
        self.responses = {
            "coffee_leaf_rust": [
                {
                    "explanation": (
                        "Your coffee plant appears to have symptoms of Coffee Leaf Rust, a fungal disease "
                        "caused by *Hemileia vastatrix*. This disease often starts as small yellow spots "
                        "on the upper leaf surface before forming orange powder underneath. It weakens the "
                        "plant by reducing photosynthesis, especially during warm and humid periods."
                    ),
                    "actions": [
                        "Remove severely infected leaves to slow the spread.",
                        "Apply copper-based fungicides or organic sprays like neem at early stages.",
                        "Ensure proper spacing and pruning to improve air flow.",
                        "Avoid overhead watering which increases humidity.",
                        "Plant resistant varieties such as Ruiru 11 or Batian if replanting."
                    ]
                },
                {
                    "explanation": (
                        "This looks like Coffee Leaf Rust, a very common issue in coffee farms. The fungus "
                        "thrives in warm, moist environments and spreads quickly during the rainy season. "
                        "If not managed early, the plant loses leaves and yields drop significantly."
                    ),
                    "actions": [
                        "Prune dense branches to allow sunlight penetration.",
                        "Spray approved fungicides at the first sign of infection.",
                        "Apply foliar feeds to strengthen plant immunity.",
                        "Remove leaf litter under the coffee bush—they hold fungal spores."
                    ]
                }
            ],

            "coffee_berry_disease": [
                {
                    "explanation": (
                        "The symptoms match Coffee Berry Disease (CBD), caused by *Colletotrichum kahawae*. "
                        "CBD attacks developing berries, turning them black and causing them to dry or fall. "
                        "It is very destructive in high-altitude, cool regions."
                    ),
                    "actions": [
                        "Spray copper-based fungicides during early berry development.",
                        "Collect and destroy fallen berries—they contain fungal spores.",
                        "Prune to reduce excessive shade and moisture.",
                        "Use resistant varieties like Ruiru 11."
                    ]
                },
                {
                    "explanation": (
                        "This appears to be Coffee Berry Disease. It spreads rapidly during wet conditions "
                        "and mostly affects green berries. Yield losses can be very high if unmanaged."
                    ),
                    "actions": [
                        "Maintain a clean farm by removing infected berries.",
                        "Avoid excessive shade—CBD thrives in cold, moist conditions.",
                        "Apply regular protective sprays during the flowering and berry-growth stages."
                    ]
                }
            ],

            "leaf_miner": [
                {
                    "explanation": (
                        "The damage looks like an attack by the Coffee Leaf Miner. The larvae dig tunnels "
                        "inside the leaf, leaving white trails and causing premature leaf drop."
                    ),
                    "actions": [
                        "Remove and destroy heavily-damaged leaves.",
                        "Introduce biological controls like parasitoid wasps if available.",
                        "Use recommended systemic insecticides if infestation is severe.",
                        "Keep the farm weed-free to reduce breeding grounds."
                    ]
                }
            ],

            "wilt_disease": [
                {
                    "explanation": (
                        "This seems to be Coffee Wilt Disease, a serious fungal problem caused by "
                        "*Fusarium xylarioides*. Infected trees show sudden wilting, bark cracking, "
                        "and dark-streaking inside the stem."
                    ),
                    "actions": [
                        "Remove and burn infected plants to prevent spread.",
                        "Disinfect tools before moving to another tree.",
                        "Avoid waterlogging as it encourages fungal growth.",
                        "Plant resistant varieties during replanting."
                    ]
                }
            ],

            "nutrient_deficiency": [
                {
                    "explanation": (
                        "The plant shows signs of nutrient deficiency. Yellowing leaves, poor growth, "
                        "and weak branches are often caused by low nitrogen, potassium, or magnesium."
                    ),
                    "actions": [
                        "Apply well-balanced fertilizers such as NPK 20-10-10.",
                        "Add organic compost or manure to improve soil structure.",
                        "Test soil pH — coffee prefers 5.3 to 6.5.",
                        "Mulch to reduce nutrient loss and maintain moisture."
                    ]
                }
            ]
        }

    def generate_advice(self, disease_key, language="en"):
        """
        Returns:
            explanation: long description
            steps: list of recommended actions
        """

        if disease_key not in self.responses:
            return {
                "explanation": "The system could not identify this issue on your coffee plant.",
                "steps": ["Try uploading a clearer image.", "Ensure the whole leaf or berry is visible."]
            }

        disease_options = self.responses[disease_key]
        selected = random.choice(disease_options)

        explanation = selected["explanation"]
        steps = random.sample(selected["actions"], min(4, len(selected["actions"])))

        # Placeholder for multilingual expansion
        if language == "sw":
            explanation += "\n\n(Swahili translation coming soon)"
        elif language == "ki":
            explanation += "\n\n(Kikuyu translation coming soon)"

        return {
            "explanation": explanation,
            "steps": steps
        }
