# CODE ARTIFACT: app_flask.py
from flask import Flask, render_template, request, jsonify
from scoring_engine import compute_credit_profile
from ai_engine import query_qwen_underwriter
import requests
import json
from ai_training import TRAINING_PROMPT_TEMPLATE

from flask import make_response
from pdf_generator import build_sanction_pdf

app = Flask(__name__)

# Global array to store the interactive conversation thread
chat_history = []

@app.route('/')
def index():
    global chat_history
    chat_history = [] # Reset conversation history on fresh page load
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    result = compute_credit_profile(
        data['gst_delay'], 
        data['upi_var'], 
        data['staff_delta'], 
        data['power_delta']
    )
    return jsonify(result)

@app.route('/generate_upfront_brief', methods=['POST'])
def generate_upfront_brief():
    global chat_history

    data = request.json

    # 🎯 Updated to the chat endpoint to prevent loopback timeouts
    url = "http://127.0.0.1:11434/api/chat"

    analysis_prompt = f"""
    Provide a tight, maximum 2-sentence underwriting narrative explaining the core bottleneck or strength driving this score. Do not use generic introductory filler phrases.

    Entity Name: {data['name']}
    Assigned Score: {data['score']}
    Verdict Label: {data['verdict']}
    Raw Technical Inputs:
    - GST Delay: {data['inputs']['gst_delay']} days
    - UPI Variance: {data['inputs']['upi_var']}%
    - Net Staff Delta: {data['inputs']['staff_delta']}
    - Power Slope: {data['inputs']['power_delta']} kWh
    """

    payload = {
        "model": "llama3.2:latest",  # Swap to "qwen3:8b" if your terminal instance has it loaded!
        "messages": [
            {
                "role": "system",
                "content": "You are a professional credit underwriting officer detailing risk summaries upfront."
            },
            {
                "role": "user",
                "content": analysis_prompt
            }
        ],
        "stream": False
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=25)
        if response.status_code == 200:
            # Extract content correctly from the chat response schema
            brief_text = response.json()["message"]["content"].strip()

            # ✅ IMPORTANT: add this brief into chat_history so pdf_generator can print it
            # (pdf_generator prints assistant messages and also skips only the 'Ingested successfully' boilerplate)
            chat_history.append({"role": "assistant", "content": brief_text})

            return jsonify({"brief": brief_text})

        return jsonify({"brief": "Operational metrics logged. Core summary generation paused."})

    except Exception as e:
        # Pass the actual technical message if it fails again so we can read it
        return jsonify({"brief": f"System connection trace reset: {str(e)}"})

@app.route('/query_ai', methods=['POST'])
def query_ai():
    global chat_history
    data = request.json
    user_query = data.get('query')
    metrics = data.get('metrics')

    url = "http://127.0.0.1:11434/api/chat"
    
    # 1. Initialize context ONLY if the thread history profile is completely empty
    if not chat_history:
        chat_history.append({"role": "system", "content": TRAINING_PROMPT_TEMPLATE})
        
        clean_dossier = (
            f"Company: {metrics['name']}. "
            f"Score: {metrics['score']} ({metrics['percentage']}). "
            f"Inputs: GST Delay {metrics['inputs']['gst']} days, "
            f"UPI Var {metrics['inputs']['upi']}%, "
            f"Staff Delta {metrics['inputs']['staff']}, "
            f"Power {metrics['inputs']['power']} kWh."
        )
        chat_history.append({"role": "user", "content": f"Ingest target data: {clean_dossier}"})
        chat_history.append({"role": "assistant", "content": "Metrics logged. Processing interactive evaluation thread."})

    # 2. Append the user's new question to the active array memory
    chat_history.append({"role": "user", "content": user_query})

    # 3. SAFETY WINDOW TRIM: Always keep the rules (0) + last 4 operational turns
    if len(chat_history) > 6:
        chat_history = [chat_history[0]] + chat_history[-4:]

    # 4. FIXED: Payload is now globally declared outside the condition boundaries!
    payload = {
        "model": "llama3.2:latest", 
        "messages": chat_history,
        "stream": False
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        # Pushed to 120 seconds for safety margin space execution
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        if response.status_code == 200:
            ai_text = response.json()["message"]["content"]
            chat_history.append({"role": "assistant", "content": ai_text})
            return jsonify({"status": "success", "history": chat_history})
        else:
            return jsonify({"status": "error", "response": f"⚠️ Ollama Core Fault: Status code {response.status_code}"})
    except Exception as e:
        return jsonify({"status": "error", "response": f"🚨 Connection timeout. Trace: {str(e)}"})
    
@app.route('/reset_chat', methods=['POST'])
def reset_chat():
    global chat_history
    chat_history = []
    return jsonify({"status": "reset"})

@app.route('/export_pdf', methods=['POST'])
def export_pdf():
    global chat_history
    data = request.json
    metrics = data.get('metrics')

    # Call the ReportLab engine module to generate the binary stream
    pdf_binary = build_sanction_pdf(metrics, chat_history)

    response = make_response(pdf_binary)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f"attachment; filename=Sanction_Memo_{metrics['name'].replace(' ', '_')}.pdf"
    return response

if __name__ == '__main__':
    print("🔋 Interactive Chat Engine Active on http://127.0.0.1:5000")
    app.run(port=5000, debug=True)
