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

        wardrobe_for_ai = []
        for item in wardrobe:
            clean_item = item.copy()
            if "imageDataUrl" in clean_item:
                del clean_item["imageDataUrl"]
            wardrobe_for_ai.append(clean_item)
        # ========================================================

        user_desc = (
            f"Name: {profile.get('name')}. "
            f"Gender: {profile.get('gender')}. "
            f"Body: {profile.get('height')}cm, {profile.get('weight')}kg, {profile.get('body_type')} build. "
            f"Skin Tone: {profile.get('skin_tone')}. "
            f"Style Preference: {profile.get('style')}."
        )

        system_prompt = (
            "You are an expert AI Personal Stylist focused on color analysis and body type matching.\n"
            "1. Analyze the user's body type and skin tone to select the most flattering items.\n"
            "2. Consider weather and event.\n"
            "3. Return JSON: { \"items\": [id1, id2...], \"reason\": \"explanation\" }\n"
            "4. The explanation MUST mention why these items fit the user's body type or skin tone (e.g. 'This color pops against your warm skin tone')."
        )

        user_content = f"User Profile: {user_desc}\nWeather: {weather}\nEvent: {user_event}\nWardrobe JSON: {json.dumps(wardrobe_for_ai)}"

        resp = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}]
        )
        return jsonify(json.loads(resp.choices[0].message.content))
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

    # AI Context injection
    system_msg = {
        "role": "system",
        "content": (
            f"You are a Personal Stylist. User: {profile.get('name')}. "
            f"Details: {profile.get('gender')}, {profile.get('height')}cm, {profile.get('weight')}kg. "
            f"Body: {profile.get('body_type')}, Skin: {profile.get('skin_tone')}. "
            f"Style: {profile.get('style')}. "
            "Give advice based on these physical attributes."
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