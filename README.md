Intelligent Assistant using LLM

---

````markdown
# 🧠 ProChat – Local AI Chatbot App

ProChat is a powerful local AI chatbot built using **Flask** that:
- Accepts user input and files (PDF, TXT, CSV)
- Streams responses from a **local Mistral model (Ollama)**
- Uses **web search fallback** for 2024–2025 queries (via Wikipedia)
- Performs **data analytics** from uploaded CSVs
- Renders formatted answers and code blocks (like ChatGPT)

---

## 🚀 Features

- ✅ Chat interface with typing animation and markdown support
- 📎 PDF & TXT file upload with automatic content extraction
- 🌐 Web fallback using Wikipedia when local model is unsure
- 📊 Data Analytics tool to visualize bar, pie, and line charts from uploaded CSVs
- 🧠 Local model support (via Ollama + Mistral)
- 💬 Greeting responses to "hi", "hello", etc.
- 📝 Auto-formatted code blocks with copy buttons

---

## 🛠 Requirements

Make sure the following are installed:

```bash
Python 3.10+ (Recommended)
ollama (https://ollama.com)
````

### Python Packages

Install them using:

```bash
pip install -r required.txt
```

**required.txt**:

```
flask
requests
beautifulsoup4
PyPDF2
pandas
matplotlib
werkzeug
```

---

## 💡 How to Run the App

1. **Install Ollama + Mistral locally**:

   ```bash
   ollama pull mistral
   ```

2. **Run the Flask app**:

   ```bash
   python app.py
   ```

3. **Visit in browser**:

   ```
   http://127.0.0.1:5000/
   ```

---

## 📁 Project Structure

```
ProChat/
│
├── app.py                # Main Flask backend
├── templates/
│   └── chat.html         # Frontend chat UI
├── uploads/              # Uploaded PDF, TXT, CSV files
├── required.txt          # Python dependencies
├── README.md             # This file
```

---

## 🌐 Web Fallback Examples

For future-based or trending queries, the app fetches real-time info via Wikipedia (2024–2025):

> **User:** Which team won the IPL 2025 title?
> **Response:** Royal Challengers Bengaluru (RCB) won the title by defeating PBKS by 6 runs...

---

## 📊 Data Analytics

Click **"Tools → Data Analytics"**, upload a CSV, and choose:

* `1` for Pie Chart
* `2` for Bar Chart
* `3` for Line Chart

Downloadable image of the chart appears inside the chat interface.

---

## 🤖 Local Model via Ollama

Ollama handles the local LLM (like Mistral). Make sure it’s running on port `11434`.

```bash
ollama run mistral
```

---

## 🤝 Credits

* [Ollama](https://ollama.com) for local model hosting
* [Mistral](https://mistral.ai) for open weights
* [Wikipedia REST API](https://en.wikipedia.org/api/rest_v1/) for web fallback
* Built with ❤️ using Flask and Open Source tools

---

## 📜 License

This project is free and open-source under the [MIT License](LICENSE)


AUTHOR
VIJAY CHIDAMBARANATHAN - GEETHAN 
---

```

Let me know if you'd also like me to generate:
- A matching `LICENSE` file
- Screenshots for your `README`
- GitHub repository setup instructions
```
