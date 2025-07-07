import sys
import os
import re
import html
import uuid
import requests
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify, render_template, Response, stream_with_context
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
import ast

sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    uploaded_files = request.files.getlist("files[]")
    filenames = []
    all_text = ""

    for uploaded_file in uploaded_files:
        filename = secure_filename(uploaded_file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        uploaded_file.save(filepath)
        filenames.append(filename)

        try:
            if filename.lower().endswith(".pdf"):
                reader = PdfReader(filepath)
                for page in reader.pages:
                    content = page.extract_text()
                    if content:
                        all_text += content + "\n"
            else:
                with open(filepath, "r", encoding="utf-8") as f:
                    all_text += f.read() + "\n"
        except:
            continue

    return jsonify({"filenames": filenames, "content": all_text})


def search_duckduckgo(query):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        response = requests.get(url, headers=headers, timeout=10)
        matches = re.findall(r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', response.text)
        cleaned_results = []

        for match in matches[:5]:
            text = re.sub(r'<.*?>', '', match)
            cleaned = html.unescape(text).strip()
            if cleaned:
                cleaned_results.append("• " + cleaned)

        if cleaned_results:
            return "🌐 Top Result:\n" + "\n".join(cleaned_results)
        return "🌐 No clear answer found from DuckDuckGo."
    except Exception as e:
        return f"🌐 DuckDuckGo error: {str(e)}"


def evaluate_expression(expr):
    try:
        expr = expr.replace("^", "**")
        tree = ast.parse(expr, mode='eval')
        return str(eval(compile(tree, "<string>", mode="eval")))
    except:
        return None


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()
    file_content = request.json.get("file_content", "").strip()
    short_file = file_content[:2000] if file_content else ""

    # ✅ Math expression check
    if re.fullmatch(r"[0-9+\-*/().^ \n]+", user_input):
        result = evaluate_expression(user_input)
        if result:
            def reply():
                yield f"🧮 Result: `{result}`"
            return Response(stream_with_context(reply()), content_type="text/plain; charset=utf-8")
        else:
            return Response(stream_with_context(lambda: ["⚠️ Couldn't evaluate the expression."]), content_type="text/plain; charset=utf-8")

    # ✅ Greeting shortcut
    greetings = ["hi", "hello", "hey", "hai", "hii"]
    if user_input.lower() in greetings:
        def greet():
            yield "👋 Hello! How can I help you today?"
        return Response(stream_with_context(greet()), content_type="text/plain; charset=utf-8")

    # ✅ Decide if web search is needed
    future_keywords = ["2024", "2025", "next year", "will", "predict", "upcoming", "winner"]
    use_web = any(kw in user_input.lower() for kw in future_keywords)

    prompt = (
        f"The following is from uploaded documents:\n\n{short_file}\n\nNow answer:\n{user_input}"
        if short_file and not use_web else user_input
    )

    def generate():
        if use_web:
            yield "🌐 Let me fetch accurate info...\n\n"
            result = search_duckduckgo(user_input)
            yield result
            return

        full_reply = ""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "mistral", "prompt": prompt, "stream": True},
                stream=True,
                timeout=60
            )
            for line in response.iter_lines():
                if line:
                    part = line.decode("utf-8")
                    if '"response":"' in part:
                        token = part.split('"response":"')[-1].split('"')[0]
                        full_reply += token
                        yield token
        except:
            pass

        if not full_reply.strip():
            fallback = search_duckduckgo(user_input)
            yield "\n\n🌐 Backup Info:\n" + fallback

    return Response(stream_with_context(generate()), content_type="text/plain; charset=utf-8")


@app.route("/visualize", methods=["POST"])
def visualize_chart():
    try:
        file = request.files.get("file")
        chart_type = request.form.get("chart_type")

        print("🔹 Received chart_type:", chart_type)
        print("🔹 Received file:", file.filename if file else "No file")

        if not file or not chart_type:
            print("❌ Missing file or chart_type")
            return jsonify({"error": "Missing file or chart type"}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        if filename.endswith(".xlsx"):
            df = pd.read_excel(filepath)
        else:
            df = pd.read_csv(filepath)

        print("🔹 File loaded successfully:")
        print(df.head())

        if df.shape[1] < 2:
            print("❌ File must have at least 2 columns")
            return jsonify({"error": "File must have at least 2 columns"}), 400

        x = df.iloc[:, 0]
        y = df.iloc[:, 1]

        plt.figure(figsize=(6, 4))

        if chart_type == "1":
            plt.pie(y, labels=x, autopct='%1.1f%%')
            plt.title("Pie Chart")
        elif chart_type == "2":
            plt.plot(x, y, marker='o')
            plt.title("Line Chart")
            plt.xlabel(x.name)
            plt.ylabel(y.name)
        elif chart_type == "3":
            plt.bar(x, y)
            plt.title("Bar Chart")
            plt.xlabel(x.name)
            plt.ylabel(y.name)
        else:
            print("❌ Invalid chart type:", chart_type)
            return jsonify({"error": "Invalid chart type"}), 400

        chart_filename = f"{uuid.uuid4().hex}.png"
        chart_folder = os.path.join("static", "charts")
        os.makedirs(chart_folder, exist_ok=True)
        chart_path = os.path.join(chart_folder, chart_filename)
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()

        print("✅ Chart saved at:", chart_path)
        return jsonify({"img_url": f"/static/charts/{chart_filename}"})

    except Exception as e:
        print("🔥 Chart generation error:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

