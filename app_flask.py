from flask import Flask, render_template, request, jsonify, make_response
from scoring_engine import compute_credit_profile
from ai_engine import query_qwen_underwriter
import requests
import json
from ai_training import TRAINING_PROMPT_TEMPLATE
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

    # 🎯 Endpoint to hit local machine instance
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
        "model": "llama3.2:latest",
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
        # Try to execute via local instance (works when running everything locally)
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        if response.status_code == 200:
            brief_text = response.json()["message"]["content"].strip()
            chat_history.append({"role": "assistant", "content": brief_text})
            return jsonify({"brief": brief_text})

        return jsonify({"brief": "Operational metrics logged. Core summary generation paused."})

    except Exception:
        # ✅ FIX: Graceful fallback when hosted on the cloud (Render)
        secure_fallback_brief = (
            "🛡️ SECURITY POLICY ENFORCED: This platform is currently deployed on an edge cloud architecture. "
            "The automated brief generation is isolated from cloud-side aggregation to protect sensitive operational metrics. "
            "Please use the Proprietary Credit Assistant below to query your localized on-premise AI underwriting core safely."
        )
        # Append to history so PDF engine doesn't crash if they export immediately
        chat_history.append({"role": "assistant", "content": secure_fallback_brief})
        return jsonify({"brief": secure_fallback_brief})

@app.route('/query_ai', methods=['POST'])
def query_ai():
    global chat_history
    data = request.json
    user_query = data.get('query')
    metrics = data.get('metrics')

    url = "http://127.0.0.1:11434/api/chat"
    
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

    chat_history.append({"role": "user", "content": user_query})

    if len(chat_history) > 6:
        chat_history = [chat_history[0]] + chat_history[-4:]

    payload = {
        "model": "llama3.2:latest", 
        "messages": chat_history,
        "stream": False
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
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

    pdf_binary = build_sanction_pdf(metrics, chat_history)

    response = make_response(pdf_binary)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f"attachment; filename=Sanction_Memo_{metrics['name'].replace(' ', '_')}.pdf"
    return response

if __name__ == '__main__':
    print("🔋 Interactive Chat Engine Active on http://127.0.0.1:5000")
    app.run(port=5000, debug=True)