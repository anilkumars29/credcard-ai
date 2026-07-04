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

@app.route('/sync_brief_to_history', methods=['POST'])
def sync_brief_to_history():
    """
    🔗 Edge Execution Sync Pipeline:
    Receives the locally-inferred brief text computed in the user's browser frame 
    and directly appends it into server session memory. This guarantees the 
    downstream ReportLab PDF compiler captures the precise narrative for print execution.
    """
    global chat_history
    data = request.json
    brief_text = data.get('brief', '').strip()
    
    if brief_text:
        chat_history.append({"role": "assistant", "content": brief_text})
        return jsonify({"status": "success", "message": "Edge brief synchronized with server state memory."})
    return jsonify({"status": "error", "message": "Null data payload rejected by state synchronization core."}), 400

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