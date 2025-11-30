import os
import json
import time
import uuid
from pathlib import Path

import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROFILE_PATH = Path("profile.json")
CHATS_PATH = Path("chats.json")

# Обновленная структура профиля
DEFAULT_PROFILE = {
    "name": "User",
    "email": "",
    "city": "",
    "about": "",
    # Новые структурированные поля
    "gender": "Unisex",
    "height": "",
    "weight": "",
    "body_type": "Regular",
    "skin_tone": "Neutral",
    "style": "Casual"
}


# --- HELPERS ---

def load_profile():
    if PROFILE_PATH.exists():
        try:
            data = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
            merged = DEFAULT_PROFILE.copy()
            merged.update(data)
            return merged
        except:
            return DEFAULT_PROFILE.copy()
    return DEFAULT_PROFILE.copy()


def save_profile(data: dict) -> None:
    PROFILE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_chats():
    if CHATS_PATH.exists():
        try:
            return json.loads(CHATS_PATH.read_text(encoding="utf-8"))
        except:
            return {}
    return {}


def save_chats(data: dict) -> None:
    CHATS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# --- OUTFIT VALIDATION ---

# Define incompatible clothing combinations
INCOMPATIBLE_ITEMS = {
    "bottoms": ["jeans", "pants", "shorts", "skirt", "trousers", "leggings", "cargo"],
    "shoes": ["sneakers", "boots", "heels", "sandals", "loafers", "oxfords", "flats"],
    "outerwear": ["jacket", "coat", "blazer", "cardigan", "sweater", "hoodie"],
}

def get_item_category(item: dict) -> str:
    """
    Determine the category of a clothing item based on its type.
    """
    item_type = item.get("type", "").lower()
    
    for category, types in INCOMPATIBLE_ITEMS.items():
        for item_type_name in types:
            if item_type_name in item_type:
                return category
    
    return "accessory"  # Default category


def validate_outfit(wardrobe: list, outfit_items: list) -> tuple:
    """
    Validates an outfit to ensure no incompatible items are combined.
    Returns: (is_valid: bool, conflicts: list, filtered_items: list)
    """
    if not outfit_items:
        return True, [], []
    
    # Create a map of item_id to item for quick lookup
    wardrobe_map = {item.get("id"): item for item in wardrobe}
    
    # Track items by category
    bottoms = []
    shoes = []
    outerwear = []
    tops = []
    accessories = []
    conflicts = []
    
    for item_id in outfit_items:
        if item_id not in wardrobe_map:
            continue
            
        item = wardrobe_map[item_id]
        item_type = item.get("type", "").lower()
        
        # Categorize item
        is_bottom = any(x in item_type for x in ["jeans", "pants", "shorts", "skirt", "trousers", "leggings", "cargo"])
        is_shoe = any(x in item_type for x in ["sneaker", "boot", "heel", "sandal", "loafer", "oxford", "flat", "shoe"])
        is_outerwear = any(x in item_type for x in ["jacket", "coat", "blazer", "cardigan", "sweater", "hoodie", "vest"])
        is_top = any(x in item_type for x in ["shirt", "blouse", "tshirt", "t-shirt", "top", "dress", "tank"])
        
        if is_bottom:
            bottoms.append(item)
        elif is_shoe:
            shoes.append(item)
        elif is_outerwear:
            outerwear.append(item)
        elif is_top:
            tops.append(item)
        else:
            accessories.append(item)
    
    # Validate outfit structure
    if len(bottoms) > 1:
        conflicts.append(f"Multiple bottoms detected: {', '.join([i.get('type', 'item') for i in bottoms])}")
    
    if len(shoes) > 1:
        conflicts.append(f"Multiple shoes detected: {', '.join([i.get('type', 'item') for i in shoes])}")
    
    if len(outerwear) > 1:
        conflicts.append(f"Multiple outerwear items detected: {', '.join([i.get('type', 'item') for i in outerwear])}")
    
    if len(tops) > 2:
        conflicts.append(f"Too many tops detected: {len(tops)} items (max 2)")
    
    # Build filtered valid outfit
    filtered_items = []
    # Add at most 1 of each critical category
    if bottoms:
        filtered_items.append(bottoms[0].get("id"))
    if shoes:
        filtered_items.append(shoes[0].get("id"))
    # Add up to 2 tops
    for top in tops[:2]:
        filtered_items.append(top.get("id"))
    # Add at most 1 outerwear
    if outerwear:
        filtered_items.append(outerwear[0].get("id"))
    # Add all accessories
    for acc in accessories:
        filtered_items.append(acc.get("id"))
    
    is_valid = len(conflicts) == 0
    return is_valid, conflicts, filtered_items


# --- TOKEN OPTIMIZATION ---

def optimize_wardrobe(wardrobe: list, max_items: int = 50) -> list:
    """
    Optimizes wardrobe data to reduce token usage by:
    1. Limiting items count
    2. Keeping only essential attributes (id, type, color, style, season)
    3. Removing verbose descriptions
    """
    if not wardrobe:
        return []
    
    # Limit to max_items to prevent token overflow
    limited_wardrobe = wardrobe[:max_items]
    
    optimized = []
    for item in limited_wardrobe:
        optimized_item = {
            "id": item.get("id", ""),
            "type": item.get("type", ""),
            "color": item.get("color", ""),
            "style": item.get("style", ""),
            "season": item.get("season", ""),
            "warmth": item.get("warmth", ""),
        }
        # Only add non-empty values
        optimized.append({k: v for k, v in optimized_item.items() if v})
    
    return optimized


def create_wardrobe_summary(wardrobe: list) -> str:
    """
    Creates a concise text summary of wardrobe instead of full JSON
    to save tokens when wardrobe is very large.
    """
    if not wardrobe:
        return "No wardrobe items"
    
    # Group items by type
    types = {}
    for item in wardrobe:
        item_type = item.get("type", "Other")
        if item_type not in types:
            types[item_type] = 0
        types[item_type] += 1
    
    # Create summary
    summary = "Available wardrobe items:\n"
    for item_type, count in sorted(types.items()):
        summary += f"- {item_type}: {count} items\n"
    
    summary += f"\nTotal: {len(wardrobe)} items"
    return summary


# --- PAGES ---

@app.route("/")
def home():
    return render_template("home.html", page="home", profile=load_profile())


@app.route("/wardrobe")
def wardrobe():
    return render_template("wardrobe.html", page="wardrobe")


@app.route("/wardrobe/item/<item_id>")
def wardrobe_item(item_id):
    return render_template("wardrobe_item.html", page="wardrobe", view="wardrobe-item", item_id=item_id)


@app.route("/chat")
def chat():
    return render_template("chat.html", page="chat")


@app.route("/profile")
def profile():
    return render_template("profile.html", page="profile", view="profile-overview", profile=load_profile())


@app.route("/profile/basic")
def profile_basic():
    return render_template("profile_basic.html", page="profile", view="profile-basic", profile=load_profile())


@app.route("/profile/parameters")
def profile_parameters():
    return render_template("profile_params.html", page="profile", view="profile-params", profile=load_profile())


# --- API ---

@app.route("/api/profile", methods=["GET", "POST"])
def api_profile():
    if request.method == "GET":
        return jsonify(load_profile())

    data = request.get_json() or {}
    profile = load_profile()

    # Список всех разрешенных полей
    allowed_keys = ["name", "email", "city", "about", "gender", "height", "weight", "body_type", "skin_tone", "style"]

    for key in allowed_keys:
        if key in data:
            profile[key] = str(data[key]).strip()

    save_profile(profile)
    return jsonify(profile)


@app.route("/api/weather")
def api_weather():
    city = (request.args.get("city") or "").strip()
    if not city: return jsonify({"error": "City required"}), 400
    try:
        geo = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                           params={"name": city, "count": 1, "language": "en", "format": "json"}, timeout=3).json()
        if not geo.get("results"): return jsonify({"error": "City not found"}), 404
        loc = geo["results"][0]
        w = requests.get("https://api.open-meteo.com/v1/forecast",
                         params={"latitude": loc["latitude"], "longitude": loc["longitude"], "current_weather": True},
                         timeout=3).json().get("current_weather", {})
        return jsonify({"city": loc["name"], "country": loc.get("country", ""), "temperature": w.get("temperature"),
                        "windspeed": w.get("windspeed")})
    except:
        return jsonify({"error": "Weather service unavailable"}), 503


@app.route("/api/recognize", methods=["POST"])
def api_recognize():
    try:
        data = request.get_json()
        img_url = data.get("imageDataUrl")
        if not img_url: return jsonify({"error": "No image"}), 400
        prompt = "Analyze this image. Return JSON: { \"is_clothing\": boolean, \"type\": string, \"style\": string, \"season\": string, \"warmth\": string, \"brand\": string, \"tags\": [] }"
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt},
                                                   {"type": "image_url", "image_url": {"url": img_url}}]}]
        )
        return jsonify(json.loads(resp.choices[0].message.content))
    except Exception as e:
        print(e)
        return jsonify({"error": "AI Error"}), 500


@app.route("/api/outfit", methods=["POST"])
def api_outfit():
    try:
        data = request.get_json()
        wardrobe = data.get("wardrobe", [])
        weather = data.get("weather", "Unknown")
        user_event = data.get("user", {}).get("event", "General Day")

        profile = load_profile()

        user_desc = (
            f"Name: {profile.get('name')}. "
            f"Gender: {profile.get('gender')}. "
            f"Body: {profile.get('height')}cm, {profile.get('weight')}kg, {profile.get('body_type')} build. "
            f"Skin Tone: {profile.get('skin_tone')}. "
            f"Style Preference: {profile.get('style')}."
        )

        system_prompt = (
            "You are an expert AI Personal Stylist. Create ONE complete outfit - a single cohesive look.\n\n"
            "ABSOLUTE RULES (MUST FOLLOW EXACTLY):\n"
            "• NEVER include multiple bottoms (NO jeans + pants, NO skirt + shorts, etc.)\n"
            "• NEVER include multiple shoes\n"
            "• NEVER include multiple jackets/coats\n"
            "• Select EXACTLY 1 bottom (choose ONE: jeans, pants, skirt, shorts, leggings)\n"
            "• Select EXACTLY 1 pair of shoes\n"
            "• Select 1-2 tops\n"
            "• Select 0-1 outerwear item\n"
            "• Add accessories as desired\n\n"
            "This is ONE outfit to wear. Not multiple options. Not variations.\n"
            "ONE complete look from head to toe.\n\n"
            "ANALYSIS:\n"
            "1. Body Type: Flatter the user's body type\n"
            "2. Colors: Complement skin tone\n"
            "3. Weather: Appropriate for climate\n"
            "4. Occasion: Matches the event\n"
            "5. Style: Aligns with preferences\n\n"
            "RESPONSE:\n"
            "Return ONLY valid JSON: { \"items\": [id1, id2, id3...], \"reason\": \"explanation\" }\n\n"
            "IMPORTANT: The items array should contain IDs of pieces that work TOGETHER as ONE outfit."
        )

        # Optimize wardrobe data to reduce tokens
        optimized_wardrobe = optimize_wardrobe(wardrobe, max_items=50)
        
        user_content = (
            f"Create ONE outfit (not variations or options) for:\n"
            f"User: {user_desc}\n"
            f"Weather: {weather}\n"
            f"Event: {user_event}\n"
            f"Wardrobe: {json.dumps(optimized_wardrobe)}"
        )

        resp = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}]
        )
        
        result = json.loads(resp.choices[0].message.content)
        outfit_items = result.get("items", [])
        
        # STRICT VALIDATION: Fix invalid outfits automatically
        is_valid, conflicts, filtered_items = validate_outfit(wardrobe, outfit_items)
        
        # If invalid, use filtered items instead
        if not is_valid:
            result["items"] = filtered_items
            result["validation_applied"] = True
            result["original_conflicts"] = conflicts
        
        return jsonify(result)
    except Exception as e:
        print(e)
        return jsonify({"error": "AI Error"}), 500


@app.route("/api/outfit/remix", methods=["POST"])
def api_outfit_remix():
    """
    Regenerates outfit recommendations using different wardrobe items
    while preserving the original outfit's style and characteristics.
    """
    try:
        data = request.get_json()
        wardrobe = data.get("wardrobe", [])
        weather = data.get("weather", "Unknown")
        user_event = data.get("user", {}).get("event", "General Day")
        original_outfit = data.get("original_outfit", {})  # Previous outfit for style reference

        profile = load_profile()

        user_desc = (
            f"Name: {profile.get('name')}. "
            f"Gender: {profile.get('gender')}. "
            f"Body: {profile.get('height')}cm, {profile.get('weight')}kg, {profile.get('body_type')} build. "
            f"Skin Tone: {profile.get('skin_tone')}. "
            f"Style Preference: {profile.get('style')}."
        )

        # Extract style characteristics from original outfit if available
        original_reason = original_outfit.get("reason", "casual") if original_outfit else ""
        original_items = original_outfit.get("items", []) if original_outfit else []
        
        system_prompt = (
            "You are an expert AI Personal Stylist. Create ONE complete outfit - a fresh remix while preserving the original style.\n\n"
            "ABSOLUTE RULES (MUST FOLLOW EXACTLY):\n"
            "• AVOID using items from the original outfit (create a different combination)\n"
            "• NEVER include multiple bottoms (NO jeans + pants, NO skirt + shorts, etc.)\n"
            "• NEVER include multiple shoes\n"
            "• NEVER include multiple jackets/coats\n"
            "• Select EXACTLY 1 bottom (choose ONE: jeans, pants, skirt, shorts, leggings)\n"
            "• Select EXACTLY 1 pair of shoes\n"
            "• Select 1-2 tops\n"
            "• Select 0-1 outerwear item\n"
            "• Add accessories as desired\n\n"
            "REMIX STRATEGY:\n"
            "- Keep the same style vibe as the original outfit\n"
            "- Use different pieces to create a fresh look\n"
            "- Maintain the same formality level and occasion appropriateness\n"
            "- Preserve color harmony with the user's skin tone\n\n"
            "ANALYSIS:\n"
            "1. Body Type: Flatter the user's body type\n"
            "2. Colors: Complement skin tone\n"
            "3. Weather: Appropriate for climate\n"
            "4. Occasion: Matches the event\n"
            "5. Style: Aligns with original mood while using different items\n\n"
            "RESPONSE:\n"
            "Return ONLY valid JSON: { \"items\": [id1, id2, id3...], \"reason\": \"explanation\" }\n\n"
            "IMPORTANT: The items array should contain IDs of NEW pieces that work TOGETHER as ONE outfit."
        )

        # Optimize wardrobe data to reduce tokens
        optimized_wardrobe = optimize_wardrobe(wardrobe, max_items=50)
        
        user_content = (
            f"Create ONE fresh outfit (remix) that:\n"
            f"- Uses DIFFERENT items than: {original_items}\n"
            f"- Maintains the style of: {original_reason}\n\n"
            f"User: {user_desc}\n"
            f"Weather: {weather}\n"
            f"Event: {user_event}\n"
            f"Wardrobe: {json.dumps(optimized_wardrobe)}"
        )

        resp = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}]
        )
        
        result = json.loads(resp.choices[0].message.content)
        outfit_items = result.get("items", [])
        
        # STRICT VALIDATION: Fix invalid outfits automatically
        is_valid, conflicts, filtered_items = validate_outfit(wardrobe, outfit_items)
        
        # If invalid, use filtered items instead
        if not is_valid:
            result["items"] = filtered_items
            result["validation_applied"] = True
            result["original_conflicts"] = conflicts
        
        return jsonify(result)
    except Exception as e:
        print(e)
        return jsonify({"error": "AI Error"}), 500


# --- CHATS ---

@app.route("/api/chats", methods=["GET"])
def get_chats():
    chats = load_chats()
    summary = []
    for cid, data in chats.items():
        summary.append({"id": cid, "title": data.get("title", "New Conversation"), "last_ts": data.get("last_ts", 0)})
    summary.sort(key=lambda x: x["last_ts"], reverse=True)
    return jsonify(summary)


@app.route("/api/chats/<chat_id>", methods=["GET"])
def get_chat_history(chat_id):
    chats = load_chats()
    return jsonify(chats.get(chat_id, {})) if chat_id in chats else (jsonify({"error": "Not found"}), 404)


@app.route("/api/chats", methods=["POST"])
def create_chat():
    chats = load_chats()
    new_id = str(uuid.uuid4())
    chats[new_id] = {"title": "New Chat", "messages": [], "last_ts": time.time()}
    save_chats(chats)
    return jsonify({"id": new_id})


@app.route("/api/chats/<chat_id>/message", methods=["POST"])
def send_chat_message(chat_id):
    chats = load_chats()
    if chat_id not in chats: return jsonify({"error": "Not found"}), 404

    user_text = request.get_json().get("message", "").strip()
    if not user_text: return jsonify({"error": "Empty"}), 400

    profile = load_profile()
    chats[chat_id]["messages"].append({"role": "user", "content": user_text})

    # AI Context injection with strict fashion-focused prompt
    system_msg = {
        "role": "system",
        "content": (
            f"You are a helpful fashion assistant that specializes in clothing and style advice.\n\n"
            f"USER PROFILE (use for personalized recommendations):\n"
            f"- {profile.get('name')}\n"
            f"- {profile.get('gender')}, {profile.get('height')}cm, {profile.get('weight')}kg\n"
            f"- Body Type: {profile.get('body_type')}, Skin Tone: {profile.get('skin_tone')}\n"
            f"- Style: {profile.get('style')}\n\n"
            f"SCOPE - Answer ONLY about:\n"
            f"✓ Clothing recommendations and outfit ideas\n"
            f"✓ Fashion tips and styling advice\n"
            f"✓ Colors, body type flattery, and personal style\n"
            f"✓ Accessories and wardrobe management\n"
            f"✓ Seasonal trends and occasion-appropriate clothing\n\n"
            f"OUT OF SCOPE - Politely decline and redirect:\n"
            f"✗ Questions NOT about fashion or clothing\n"
            f"Respond with: 'I focus on fashion and clothing advice. Ask me about outfits, styling tips, or your wardrobe!'\n\n"
            f"TONE: Be conversational, helpful, and friendly. Keep responses natural and not overly formal."
        )
    }

    context = chats[chat_id]["messages"][-10:]
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[system_msg] + context)
        reply = resp.choices[0].message.content
        chats[chat_id]["messages"].append({"role": "assistant", "content": reply})
        chats[chat_id]["last_ts"] = time.time()
        if len(chats[chat_id]["messages"]) <= 2: chats[chat_id]["title"] = user_text[:30] + "..."
        save_chats(chats)
        return jsonify({"reply": reply})
    except Exception as e:
        print(e)
        return jsonify({"error": "AI Error"}), 500


@app.route("/api/chats/<chat_id>", methods=["DELETE"])
def delete_chat(chat_id):
    chats = load_chats()
    if chat_id in chats:
        del chats[chat_id]
        save_chats(chats)
    return jsonify({"status": "deleted"})


if __name__ == "__main__":
    app.run(debug=True)