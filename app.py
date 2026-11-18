import os
import json
import requests
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6IgjbmNLaCclpJOf1p5X2W5mtIBKUg61y55cWjkrqq5_w")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/sw.js")
def service_worker():
    return send_from_directory("static", "sw.js", mimetype="application/javascript")

@app.route("/api/discover", methods=["POST"])
def discover_places():
    data = request.json
    city = data.get("city", "").strip()
    days = data.get("days", 3)

    if not city:
        return jsonify({"error": "Podaj nazwe miasta"}), 400

    if GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            prompt = f"Zaproponuj 8 konkretnych miejsc w {city} na {days} dni (tanie jedzenie, darmowe atrakcje, punkty widokowe). Zwroc wylacznie JSON liste obiektow z polami: title, category, cost, tip."
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"}
            }
            res = requests.post(url, json=payload, timeout=20)
            res.raise_for_status()
            result_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
            places = json.loads(result_text)
            return jsonify({"places": places})
        except Exception as e:
            print("Tryb zapasowy:", e)

    demo_places = [
        {"title": f"Stare Miasto i glowny plac ({city})", "category": "Zwiedzanie", "cost": "Darmowe", "tip": "Najlepiej przyjsc rano przed tlumami."},
        {"title": f"Lokalny targ / Street Food w {city}", "category": "Jedzenie", "cost": "ok. 25 PLN", "tip": "Szukaj stoisk, gdzie jedza miejscowi."},
        {"title": f"Punkt widokowy na panorame {city}", "category": "Widok", "cost": "Darmowe", "tip": "Idealne miejsce na zachod slonca."},
        {"title": "Darmowy spacer tematyczny (Free Walking Tour)", "category": "Zwiedzanie", "cost": "Napiwek", "tip": "Zarezerwuj miejsce dzien wczesniej."}
    ]
    return jsonify({"places": demo_places})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
