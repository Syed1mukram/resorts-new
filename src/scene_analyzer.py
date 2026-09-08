import re

VISUAL_CATEGORIES = {

    "room": [
        "room", "suite", "bedroom", "bed",
        "villa", "apartment", "family room",
        "deluxe", "king", "queen"
    ],

    "bathroom": [
        "bathroom", "shower", "bathtub",
        "washroom", "toilet"
    ],

    "pool": [
        "pool", "swimming", "infinity pool",
        "lazy river", "water park"
    ],

    "beach": [
        "beach", "ocean", "sea",
        "shore", "coast", "sand",
        "waves"
    ],

    "balcony": [
        "balcony", "terrace",
        "ocean view", "sea view",
        "mountain view"
    ],

    "restaurant": [
        "restaurant", "buffet",
        "breakfast", "dining",
        "food", "chef"
    ],

    "bar": [
        "bar", "cocktail",
        "lounge", "drinks"
    ],

    "spa": [
        "spa", "massage",
        "wellness", "sauna"
    ],

    "gym": [
        "gym", "fitness",
        "workout"
    ],

    "lobby": [
        "lobby", "reception",
        "check in"
    ],

    "kids": [
        "kids club",
        "children",
        "playground"
    ],

    "outside": [
        "resort",
        "hotel",
        "building",
        "exterior",
        "garden",
        "aerial",
        "drone",
        "entrance"
    ]

}


class SceneAnalyzer:

    def __init__(self):
        pass

    # --------------------------------------------

    def analyze(self, text):

        text = text.lower()

        text = re.sub(
            r"[^a-z0-9\s]",
            " ",
            text
        )

        found = []

        scene = "general"

        for category, words in VISUAL_CATEGORIES.items():

            for word in words:

                if word in text:

                    found.append(word)

                    if scene == "general":
                        scene = category

        if not found:

            return {

                "scene": "general",

                "prompt": text,

                "keywords": []

            }

        prompt = ", ".join(found)

        return {

            "scene": scene,

            "prompt": prompt,

            "keywords": found

        }


# -------------------------------------------------

if __name__ == "__main__":

    analyzer = SceneAnalyzer()

    while True:

        t = input("Text : ").strip()

        if not t:
            break

        print(analyzer.analyze(t))