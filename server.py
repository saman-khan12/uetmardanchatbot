"""
Flask app for the UET Mardan assistant.

All the answering logic lives in rag.py; this file is just the web layer:
one page, one JSON endpoint.

Run:
    python server.py
Then open http://127.0.0.1:5000
"""

from flask import Flask, jsonify, render_template, request

from rag import answer_question

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    data = request.get_json(silent=True) or {}
    question = (data.get("message") or "").strip()

    if not question:
        return jsonify({"error": "Empty message"}), 400

    try:
        answer, sources = answer_question(question)
    except Exception as error:  # noqa: BLE001 - surface any failure to the UI
        return jsonify({"error": str(error)}), 500

    return jsonify({"answer": answer, "sources": sources})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)