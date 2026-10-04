from __future__ import annotations
import os
import sys
import json
import logging

# Add backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings
from app.services import gemini_client
from app.services.image_understanding_service import build_and_validate_image_profile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("generate_demo_profiles")

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "data"))
MANIFEST_PATH = os.path.join(DATA_DIR, "demo_library.json")
PHOTOS_DIR = os.path.join(DATA_DIR, "demo-photos")
OUTPUT_PROFILES_PATH = os.path.join(DATA_DIR, "demo_profiles.json")


FALLBACK_METADATA = {
    # CLUSTER A — BIRTHDAY / CELEBRATION (8 images)
    "demo_001": {
        "people_count": "3+", "people_age_group": ["child", "adult"],
        "people_description": "child and adults gathered around a table with a birthday cake",
        "setting": "indoor", "setting_type": "home living room", "setting_details": "decorated with colorful balloons and party streamers",
        "time_of_day": "night", "season_hint": "unclear", "activity": "celebrating", "occasion": "birthday",
        "clothing": ["pink dress", "blue shirt", "party hat"], "objects": ["birthday cake", "candles", "balloons", "gifts"],
        "animals": [], "dominant_colors": ["pink", "blue", "white", "yellow"], "mood": "happy", "composition": "group",
        "free_description": "Childhood birthday party indoors with a birthday cake, candles, balloons, and party hats.",
        "identity_tags": ["Sister", "Mom"],
    },
    "demo_002": {
        "people_count": "2", "people_age_group": ["adult"],
        "people_description": "two adults smiling near a decorated birthday dessert table",
        "setting": "indoor", "setting_type": "dining room", "setting_details": "decorated background with yellow banners and balloons",
        "time_of_day": "night", "season_hint": "unclear", "activity": "celebrating", "occasion": "birthday",
        "clothing": ["yellow dress", "black shirt"], "objects": ["chocolate cake", "yellow balloons", "sparklers"],
        "animals": [], "dominant_colors": ["yellow", "black", "gold"], "mood": "happy", "composition": "group",
        "free_description": "Birthday celebration with yellow balloons, cake, and warm party lights.",
        "identity_tags": [],
    },
    "demo_003": {
        "people_count": "3+", "people_age_group": ["child", "adult"],
        "people_description": "child and adults around outdoor patio table with cake",
        "setting": "outdoor", "setting_type": "backyard patio", "setting_details": "sunlit garden patio with wooden table",
        "time_of_day": "day", "season_hint": "summer", "activity": "celebrating", "occasion": "birthday",
        "clothing": ["blue t-shirt", "white shorts"], "objects": ["birthday cake", "patio table", "juice glasses"],
        "animals": [], "dominant_colors": ["blue", "green", "white"], "mood": "happy", "composition": "group",
        "free_description": "Outdoor birthday party on patio with birthday cake and outdoor sunshine.",
        "identity_tags": [],
    },
    "demo_004": {
        "people_count": "1", "people_age_group": ["adult"],
        "people_description": "solo adult holding a single cupcake with a birthday candle",
        "setting": "indoor", "setting_type": "home kitchen", "setting_details": "cozy room decorated with soft background balloons",
        "time_of_day": "night", "season_hint": "unclear", "activity": "celebrating", "occasion": "birthday",
        "clothing": ["pink sweater"], "objects": ["cupcake", "candle", "balloons"],
        "animals": [], "dominant_colors": ["pink", "white", "beige"], "mood": "happy", "composition": "posed",
        "free_description": "Solo adult celebrating a birthday indoors in a pink sweater with a cupcake and balloons.",
        "identity_tags": [],
    },
    "demo_005": {
        "people_count": "3+", "people_age_group": ["adult"],
        "people_description": "group of friends celebrating birthday at restaurant dinner table",
        "setting": "indoor", "setting_type": "restaurant", "setting_details": "dim ambient lighting with sparkler on birthday cake",
        "time_of_day": "night", "season_hint": "unclear", "activity": "eating", "occasion": "birthday",
        "clothing": ["black blazer", "gold dress"], "objects": ["birthday cake", "sparklers", "wine glasses"],
        "animals": [], "dominant_colors": ["black", "gold", "white"], "mood": "happy", "composition": "group",
        "free_description": "Birthday dinner in a restaurant setting with sparklers on cake and formal attire.",
        "identity_tags": [],
    },
    "demo_006": {
        "people_count": "3+", "people_age_group": ["adult"],
        "people_description": "friends at outdoor park pavilion decorated with colorful balloons",
        "setting": "outdoor", "setting_type": "park pavilion", "setting_details": "covered outdoor park structure with balloon decor",
        "time_of_day": "day", "season_hint": "summer", "activity": "celebrating", "occasion": "birthday",
        "clothing": ["pink t-shirt", "denim shorts"], "objects": ["balloons", "cupcakes", "picnic table"],
        "animals": [], "dominant_colors": ["pink", "green", "blue"], "mood": "happy", "composition": "group",
        "free_description": "Outdoor birthday gathering at a park pavilion with pink clothing and colorful balloons.",
        "identity_tags": [],
    },
    "demo_007": {
        "people_count": "2", "people_age_group": ["child", "adult"],
        "people_description": "child and parent smiling behind yellow birthday balloons",
        "setting": "indoor", "setting_type": "home living room", "setting_details": "brightly lit living room with birthday cake",
        "time_of_day": "day", "season_hint": "unclear", "activity": "celebrating", "occasion": "birthday",
        "clothing": ["blue shirt", "jeans"], "objects": ["yellow balloons", "birthday cake", "gifts"],
        "animals": [], "dominant_colors": ["yellow", "blue", "white"], "mood": "happy", "composition": "group",
        "free_description": "Child in blue shirt celebrating birthday indoors with yellow balloons and birthday cake.",
        "identity_tags": [],
    },
    "demo_008": {
        "people_count": "3+", "people_age_group": ["adult"],
        "people_description": "outdoor garden party with birthday cake and balloons on table",
        "setting": "outdoor", "setting_type": "backyard garden", "setting_details": "green lawn garden decorated with balloons",
        "time_of_day": "day", "season_hint": "spring", "activity": "celebrating", "occasion": "birthday",
        "clothing": ["yellow dress", "white shirt"], "objects": ["birthday cake", "balloons", "garden table"],
        "animals": [], "dominant_colors": ["yellow", "white", "green"], "mood": "happy", "composition": "group",
        "free_description": "Outdoor garden birthday party with guests wearing yellow and white, featuring cake and balloons.",
        "identity_tags": [],
    },

    # CLUSTER B — BEACH / TRAVEL (7 images)
    "demo_009": {
        "people_count": "3+", "people_age_group": ["adult", "child"],
        "people_description": "family members standing together near water's edge at sunset",
        "setting": "outdoor", "setting_type": "beach shoreline", "setting_details": "sandy beach at golden hour with ocean waves",
        "time_of_day": "golden_hour", "season_hint": "summer", "activity": "traveling", "occasion": "vacation",
        "clothing": ["white t-shirt", "blue shorts", "sunglasses"], "objects": ["ocean waves", "sand", "beach towel"],
        "animals": [], "dominant_colors": ["orange", "blue", "yellow"], "mood": "candid", "composition": "group",
        "free_description": "Family walking along a sandy beach shoreline during golden hour sunset.",
        "identity_tags": ["Mom", "Dad"],
    },
    "demo_010": {
        "people_count": "1", "people_age_group": ["adult"],
        "people_description": "person walking alone along the wet sand by the sea",
        "setting": "outdoor", "setting_type": "beach coastline", "setting_details": "bright sunny sandy coast with ocean water",
        "time_of_day": "day", "season_hint": "summer", "activity": "traveling", "occasion": "vacation",
        "clothing": ["blue swimwear", "sun hat"], "objects": ["ocean water", "sand", "sun hat"],
        "animals": [], "dominant_colors": ["blue", "beige", "cyan"], "mood": "candid", "composition": "posed",
        "free_description": "A person walking along the sandy beach coastline on a bright sunny day.",
        "identity_tags": [],
    },
    "demo_011": {
        "people_count": "1", "people_age_group": ["adult"],
        "people_description": "solo person relaxing under beach umbrella on sunny coast",
        "setting": "outdoor", "setting_type": "beach resort", "setting_details": "white sand beach with beach umbrella and lounge chair",
        "time_of_day": "day", "season_hint": "summer", "activity": "posing", "occasion": "vacation",
        "clothing": ["white shirt", "sunglasses"], "objects": ["beach umbrella", "lounge chair", "sand"],
        "animals": [], "dominant_colors": ["white", "blue", "yellow"], "mood": "candid", "composition": "posed",
        "free_description": "Solo person relaxing on white sandy beach under an umbrella in white shirt and sunglasses.",
        "identity_tags": [],
    },
    "demo_012": {
        "people_count": "3+", "people_age_group": ["adult"],
        "people_description": "three friends sitting on beach blanket near ocean waves",
        "setting": "outdoor", "setting_type": "beach sand", "setting_details": "sunny coastline with ocean water in background",
        "time_of_day": "day", "season_hint": "summer", "activity": "traveling", "occasion": "vacation",
        "clothing": ["pink top", "white shorts", "sunglasses"], "objects": ["beach blanket", "ocean waves", "sand"],
        "animals": [], "dominant_colors": ["pink", "white", "blue"], "mood": "happy", "composition": "group",
        "free_description": "Friends sitting together on a beach blanket in pink and white casual clothing near the ocean.",
        "identity_tags": [],
    },
    "demo_013": {
        "people_count": "2", "people_age_group": ["adult"],
        "people_description": "couple walking along rocky coastline with blue sea behind them",
        "setting": "outdoor", "setting_type": "rocky coastline", "setting_details": "coastal scenic trail overlooking ocean",
        "time_of_day": "day", "season_hint": "summer", "activity": "walking", "occasion": "vacation",
        "clothing": ["blue linen shirt", "white dress", "sun hat"], "objects": ["ocean rocks", "sea", "sun hat"],
        "animals": [], "dominant_colors": ["blue", "white", "brown"], "mood": "candid", "composition": "group",
        "free_description": "Pair walking along scenic rocky coastline with blue ocean and sun hats.",
        "identity_tags": [],
    },
    "demo_014": {
        "people_count": "3+", "people_age_group": ["adult"],
        "people_description": "group playing beach volleyball on sandy court near water",
        "setting": "outdoor", "setting_type": "beach court", "setting_details": "sandy beach with volleyball net and ocean backdrop",
        "time_of_day": "day", "season_hint": "summer", "activity": "playing", "occasion": "vacation",
        "clothing": ["red swimwear", "shorts"], "objects": ["volleyball", "volleyball net", "sand"],
        "animals": [], "dominant_colors": ["red", "blue", "yellow"], "mood": "happy", "composition": "candid",
        "free_description": "Group actively playing beach volleyball on sunny coast near ocean water.",
        "identity_tags": [],
    },
    "demo_015": {
        "people_count": "1", "people_age_group": ["adult"],
        "people_description": "person standing under palm trees near tropical beach coast",
        "setting": "outdoor", "setting_type": "tropical beach", "setting_details": "palm tree groove next to ocean shoreline",
        "time_of_day": "day", "season_hint": "summer", "activity": "posing", "occasion": "vacation",
        "clothing": ["yellow sun dress"], "objects": ["palm trees", "ocean waves", "sand"],
        "animals": [], "dominant_colors": ["yellow", "green", "blue"], "mood": "happy", "composition": "posed",
        "free_description": "Solo person in a yellow sun dress posing under palm trees on a tropical beach trip.",
        "identity_tags": [],
    },

    # CLUSTER C — PARK / OUTDOOR ACTIVITY (7 images)
    "demo_016": {
        "people_count": "2", "people_age_group": ["adult"],
        "people_description": "two people sitting on picnic blanket on green park grass",
        "setting": "outdoor", "setting_type": "park lawn", "setting_details": "green grass field with large trees and picnic blanket",
        "time_of_day": "day", "season_hint": "spring", "activity": "eating", "occasion": "picnic",
        "clothing": ["green sweater", "jeans"], "objects": ["picnic basket", "blanket", "sandwiches", "green trees"],
        "animals": [], "dominant_colors": ["green", "brown", "blue"], "mood": "happy", "composition": "group",
        "free_description": "Outdoor picnic on a blanket on the green grass of a public park.",
        "identity_tags": [],
    },
    "demo_017": {
        "people_count": "3+", "people_age_group": ["young adult"],
        "people_description": "friends playing outdoor sports on open grass",
        "setting": "outdoor", "setting_type": "park field", "setting_details": "sunny open grass field flanked by tall trees",
        "time_of_day": "day", "season_hint": "summer", "activity": "playing", "occasion": "casual outing",
        "clothing": ["red sports jersey", "shorts", "sneakers"], "objects": ["frisbee", "water bottle", "grass field"],
        "animals": [], "dominant_colors": ["green", "red", "white"], "mood": "happy", "composition": "candid",
        "free_description": "Friends actively playing frisbee on an open green park field on a sunny day.",
        "identity_tags": [],
    },
    "demo_018": {
        "people_count": "1", "people_age_group": ["adult"],
        "people_description": "person in pink hoodie walking golden retriever dog along wooded park path",
        "setting": "outdoor", "setting_type": "wooded park", "setting_details": "tree-lined dirt path with green foliage",
        "time_of_day": "day", "season_hint": "autumn", "activity": "walking", "occasion": "casual outing",
        "clothing": ["pink hoodie", "black leggings"], "objects": ["dog leash", "trees", "park bench"],
        "animals": ["dog"], "dominant_colors": ["pink", "green", "brown"], "mood": "candid", "composition": "posed",
        "free_description": "Person in pink hoodie walking a golden retriever dog on a wooded park trail.",
        "identity_tags": [],
    },
    "demo_019": {
        "people_count": "3+", "people_age_group": ["adult", "child"],
        "people_description": "family gathered on picnic blanket under large oak tree",
        "setting": "outdoor", "setting_type": "park lawn", "setting_details": "golden hour sunlight filtering through park tree leaves",
        "time_of_day": "golden_hour", "season_hint": "summer", "activity": "eating", "occasion": "picnic",
        "clothing": ["white t-shirt", "blue jeans", "yellow hat"], "objects": ["picnic blanket", "fruit basket", "water bottles"],
        "animals": [], "dominant_colors": ["green", "yellow", "white"], "mood": "happy", "composition": "group",
        "free_description": "Family picnic under an oak tree in park lawn during golden hour.",
        "identity_tags": [],
    },
    "demo_020": {
        "people_count": "3+", "people_age_group": ["adult"],
        "people_description": "group playing soccer on green park grass field",
        "setting": "outdoor", "setting_type": "sports field", "setting_details": "open park grass field with soccer ball",
        "time_of_day": "day", "season_hint": "summer", "activity": "playing", "occasion": "casual outing",
        "clothing": ["blue athletic jersey", "shorts", "sneakers"], "objects": ["soccer ball", "grass field"],
        "animals": [], "dominant_colors": ["blue", "green", "white"], "mood": "happy", "composition": "candid",
        "free_description": "Group playing outdoor sports in blue athletic wear on park grass.",
        "identity_tags": [],
    },
    "demo_021": {
        "people_count": "1", "people_age_group": ["adult"],
        "people_description": "person sitting on wooden park bench surrounded by flowers",
        "setting": "outdoor", "setting_type": "botanical park", "setting_details": "park garden bench surrounded by blooming flowers and trees",
        "time_of_day": "day", "season_hint": "spring", "activity": "posing", "occasion": "casual outing",
        "clothing": ["yellow jacket", "blue jeans"], "objects": ["wooden bench", "flowers", "trees"],
        "animals": [], "dominant_colors": ["yellow", "green", "red"], "mood": "candid", "composition": "posed",
        "free_description": "Person wearing yellow jacket sitting peacefully on a park bench near flower beds.",
        "identity_tags": [],
    },
    "demo_022": {
        "people_count": "3+", "people_age_group": ["adult"],
        "people_description": "friends sitting on park lawn with pet dog eating snacks",
        "setting": "outdoor", "setting_type": "park lawn", "setting_details": "open park grass with blanket and dog",
        "time_of_day": "day", "season_hint": "spring", "activity": "eating", "occasion": "casual outing",
        "clothing": ["red sweater", "blue jeans"], "objects": ["blanket", "snack bowl"],
        "animals": ["dog"], "dominant_colors": ["green", "red", "brown"], "mood": "happy", "composition": "group",
        "free_description": "Friends sitting on park grass blanket sharing snacks with a pet dog.",
        "identity_tags": [],
    },

    # CLUSTER D — FESTIVAL / FORMAL CELEBRATION (7 images)
    "demo_023": {
        "people_count": "3+", "people_age_group": ["adult", "elderly"],
        "people_description": "family in traditional ethnic clothing standing near decorated sweets tray",
        "setting": "indoor", "setting_type": "home living room", "setting_details": "festive lighting with oil lamps (diyas) and traditional decor",
        "time_of_day": "night", "season_hint": "autumn", "activity": "celebrating", "occasion": "festival",
        "clothing": ["red kurta", "gold saree", "maroon sherwani"], "objects": ["diyas", "traditional sweets tray", "marigold flowers"],
        "animals": [], "dominant_colors": ["gold", "red", "maroon", "orange"], "mood": "happy", "composition": "group",
        "free_description": "Diwali festival celebration indoors with illuminated diyas, traditional sweets, and ethnic clothing.",
        "identity_tags": ["Grandma"],
    },
    "demo_024": {
        "people_count": "3+", "people_age_group": ["adult"],
        "people_description": "bride and groom surrounded by wedding guests in formal wedding attire",
        "setting": "outdoor", "setting_type": "wedding venue garden", "setting_details": "decorated floral arch with white chairs and carpet walkway",
        "time_of_day": "day", "season_hint": "spring", "activity": "celebrating", "occasion": "wedding",
        "clothing": ["white bridal gown", "black tuxedo", "formal suit"], "objects": ["flower arch", "wedding cake", "bouquet"],
        "animals": [], "dominant_colors": ["white", "green", "black"], "mood": "posed", "composition": "group",
        "free_description": "Traditional wedding ceremony in an outdoor garden setting with floral arch and wedding party.",
        "identity_tags": [],
    },
    "demo_025": {
        "people_count": "3+", "people_age_group": ["adult"],
        "people_description": "people in colorful ethnic clothing lighting sparklers outdoors for festival",
        "setting": "outdoor", "setting_type": "home courtyard", "setting_details": "night courtyard decorated with lighted diyas and marigold garlands",
        "time_of_day": "night", "season_hint": "autumn", "activity": "celebrating", "occasion": "festival",
        "clothing": ["pink kurti", "yellow dupatta", "red kurta"], "objects": ["sparklers", "diyas", "marigold garlands"],
        "animals": [], "dominant_colors": ["pink", "yellow", "gold"], "mood": "happy", "composition": "group",
        "free_description": "Outdoor festival celebration lighting sparklers in pink and yellow traditional attire.",
        "identity_tags": [],
    },
    "demo_026": {
        "people_count": "3+", "people_age_group": ["adult"],
        "people_description": "guests at formal indoor evening reception gathered near dessert table",
        "setting": "indoor", "setting_type": "banquet hall", "setting_details": "elegant hall decorated with flower arrangements and warm chandeliers",
        "time_of_day": "night", "season_hint": "winter", "activity": "celebrating", "occasion": "wedding",
        "clothing": ["black suit", "red saree", "gold dress"], "objects": ["dessert table", "flower vase", "chandelier"],
        "animals": [], "dominant_colors": ["gold", "black", "red"], "mood": "posed", "composition": "group",
        "free_description": "Formal indoor evening banquet reception with guests in suits and sarees near floral decor.",
        "identity_tags": [],
    },
    "demo_027": {
        "people_count": "1", "people_age_group": ["adult"],
        "people_description": "solo person in yellow traditional outfit holding a decorated tray of sweets",
        "setting": "indoor", "setting_type": "home kitchen", "setting_details": "festive home interior decorated with marigold flowers",
        "time_of_day": "day", "season_hint": "autumn", "activity": "celebrating", "occasion": "festival",
        "clothing": ["yellow kurta", "gold dupatta"], "objects": ["sweets tray", "marigold flowers", "brass lamp"],
        "animals": [], "dominant_colors": ["yellow", "gold", "orange"], "mood": "happy", "composition": "posed",
        "free_description": "Person in yellow traditional dress holding a tray of festival sweets indoors.",
        "identity_tags": [],
    },
    "demo_028": {
        "people_count": "2", "people_age_group": ["adult"],
        "people_description": "couple posing in formal evening wear in outdoor garden",
        "setting": "outdoor", "setting_type": "garden patio", "setting_details": "scenic garden with blooming roses and decorative arches",
        "time_of_day": "day", "season_hint": "spring", "activity": "posing", "occasion": "wedding",
        "clothing": ["blue formal suit", "pink gown"], "objects": ["flower arch", "rose bushes"],
        "animals": [], "dominant_colors": ["pink", "blue", "green"], "mood": "posed", "composition": "group",
        "free_description": "Formal outdoor photo of couple in blue suit and pink gown in garden venue.",
        "identity_tags": [],
    },
    "demo_029": {
        "people_count": "3+", "people_age_group": ["adult", "child"],
        "people_description": "family members decorating house entrance with marigold garlands and diyas",
        "setting": "outdoor", "setting_type": "home entrance", "setting_details": "front doorway decorated with rangoli art and flowers",
        "time_of_day": "day", "season_hint": "autumn", "activity": "celebrating", "occasion": "festival",
        "clothing": ["red silk saree", "yellow kurta"], "objects": ["marigold garlands", "diyas", "rangoli powder"],
        "animals": [], "dominant_colors": ["red", "yellow", "orange"], "mood": "happy", "composition": "group",
        "free_description": "Family decorating home doorway with marigolds and diyas for festive occasion.",
        "identity_tags": [],
    },
}


def main():
    if not os.path.exists(MANIFEST_PATH):
        logger.error(f"Manifest not found at {MANIFEST_PATH}")
        sys.exit(1)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        demo_items = json.load(f)

    logger.info(f"Loaded {len(demo_items)} items from demo_library.json")

    profiles = []
    has_api_key = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key")

    for item in demo_items:
        image_id = item["image_id"]
        filename = item["filename"]
        file_path = os.path.abspath(os.path.join(PHOTOS_DIR, filename))
        image_url = item.get("image_url", f"/images/demo-photos/{filename}")
        manual_label = item.get("manual_label", "")

        # Collect identity tags strictly from explicit manual person tags
        fallback_data = FALLBACK_METADATA.get(image_id, {})
        identity_tags = list(fallback_data.get("identity_tags", []))

        raw_dict = None
        if has_api_key and os.path.exists(file_path):
            try:
                logger.info(f"Analyzing {image_id} via Gemini Vision...")
                with open(file_path, "rb") as img_f:
                    img_bytes = img_f.read()
                raw_dict = gemini_client.analyze_image(img_bytes, mime_type="image/jpeg")
            except Exception as e:
                logger.warning(f"Gemini API call failed for {image_id}: {e}. Using fallback metadata.")

        if not raw_dict:
            logger.info(f"Using fallback metadata for {image_id}")
            raw_dict = fallback_data or {
                "setting": "indoor" if "indoor" in manual_label.lower() else "outdoor",
                "activity": "celebrating" if "birthday" in manual_label.lower() else "posing",
                "occasion": manual_label,
                "free_description": f"Demo photo representing {manual_label}.",
                "dominant_colors": ["blue", "white"],
            }

        profile = build_and_validate_image_profile(
            image_id=image_id,
            raw_dict=raw_dict,
            file_path=file_path if os.path.exists(file_path) else None,
            image_url=image_url,
            identity_tags=identity_tags,
        )

        profiles.append(profile.model_dump())

    with open(OUTPUT_PROFILES_PATH, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2)

    logger.info(f"Successfully generated {len(profiles)} demo profiles at {OUTPUT_PROFILES_PATH}")


if __name__ == "__main__":
    main()
