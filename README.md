# 🛡️ CredCard AI: Financial Health & Underwriting Platform

CredCard AI is a next-generation financial health and automated credit underwriting platform engineered specifically for corporate MSME evaluation. 

Traditional commercial credit checks are slow, expensive, and compromise data privacy by uploading sensitive corporate banking records to centralized cloud servers. CredCard AI solves this institutional bottleneck through a unique decoupled hybrid architecture: while the lightweight user dashboard and mathematical scoring engine run smoothly in the cloud, the heavy cognitive AI reasoning is completely decentralized—running natively on the user's host machine via local edge execution. Financial data remains completely air-gapped, secure, and fully compliant with strict banking regulations.

---

## 🔑 Core Platform Features

1. **Alternative Corporate Telemetry Ingestion Array:** Captures and displays high-frequency operational data point slopes (including GST filing delays, UPI cash flow variances, net staffing shifts, and power consumption metrics) rather than outdated static annual balance sheets.
2. **Deterministic Credit Scoring Engine:** A robust Python backend processing node that executes algorithmic risk weight distributions to calculate final credit health matrices in under 1 millisecond.
3. **Automated Underwriter Advocacy Brief:** A dynamic top-tier user interface card that prompts the local AI core to instantly compile a tight, two-sentence executive summary of core cash flow risks right inside the browser window the moment a profile loads.
4. **Decentralized Edge-AI Proprietary Credit Assistant:** An interactive conversational chatbot interface that uses client-side browser loopback routing to connect safely to an on-premise Llama 3.2 engine without transmitting data over public networks.
5. **Cross-Origin State Synchronization Pipeline:** A background data bridge that securely transfers client-side local text inferences back to the hosted server session cache so no data is lost.
6. **ReportLab Corporate Document Compiler:** A document compilation engine that gathers all cached telemetry graphs, score labels, and local AI summaries to stream a clean, audit-compliant Sanction Memo PDF directly via binary web data packets.

---

## ⚠️ SYSTEM PREREQUISITES (CRITICAL FOR DEPLOYMENT)

For **CredCard AI** to operate successfully across its decentralized architecture, your local machine must meet the following baseline requirements before launching the application:

* **Python 3.10 or Above:** The backend scoring framework and state bridges require a stable installation of **Python 3.10+**. Ensure it is added to your system environment variables path.
* **Ollama Framework Engine:** You must download and install **Ollama** natively on your host machine to handle local LLM execution. You can download it directly from **[ollama.com/download](https://ollama.com/download)**.
* **Llama 3.2 Large Language Model:** Your local Ollama node must have the **`llama3.2:latest`** model pulled and compiled. You can initialize this by running **`ollama pull llama3.2`** in your system terminal.
* **Global CORS Origin Access Permission:** To allow the live cloud-hosted website to communicate securely with your computer's local AI port, the global environment variable **`OLLAMA_ORIGINS="*"`** must be injected and active on your system.
* **Active Native Dependencies:** The automated PDF printing module requires **`reportlab`**, and the web framework requires **`flask`** and **`gunicorn`**, all of which must be installed inside your project's virtual environment using **`pip install -r requirements.txt`**.

---

## 🚀 Local Installation & Setup

### 1. Configure the Local AI Core Terminal
Ensure your background Ollama instances are fully closed from your taskbar system tray, then run these commands in a fresh **PowerShell** window to allow cross-origin cloud traffic to link to your laptop:

```powershell
# Inject the CORS flag permanently into your Windows User variables
[System.Environment]::SetEnvironmentVariable('OLLAMA_ORIGINS', '*', 'User')

# Pull the target lightweight underwriting language model
ollama pull llama3.2