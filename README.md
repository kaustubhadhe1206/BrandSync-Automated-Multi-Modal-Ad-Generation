# 🎬 BrandSync

**Automated Multi-Modal Ad Generation** | **URL-to-Video AI Orchestration**

BrandSync is an end-to-end AI orchestration engine built for the Google Gemini Hackathon. By simply pasting a single business URL, BrandSync autonomously scrapes the specific brand context and generated a professional, cinematic video advertisement using Google's state-of-the-art generative models.

---

## Features

* **AI Knowledge Extraction:** Automates unstructured web scraping (via Nano Banana) to ingest target audience, product details, and brand tone.
* **Smart Style Contract:** Uses **Google Gemini 1.5 Pro** as a "Virtual Creative Director" to enforce a deterministic JSON parameter state mapping out the exact camera angles, text overlays, and audio tempo.
* **Multi-Modal Synthesis:** Orchestrates **Google Veo** for hyper-realistic video clip generation, and **Google Lyria** for professional audio and music synthesis, precisely synced to the Style Contract.
* **Live NLP Feedback Loop:** Allows users to input natural language feedback (e.g., "Make it Cyberpunk and increase BPM to 140") and surgically patches the underlying JSON contract—saving compute time and avoiding full re-generation.
* **Beautiful Real-Time UI:** Streamlit frontend with a custom premium styled dashboard, providing real-time visual progress monitoring via a decoupled backend pulling from Firebase.

---

## 🛠️ Tech Stack

### Core AI
* **Google Gemini 1.5 Pro:** Orchestration, Semantic analysis, JSON Contract formatting
* **Google Veo:** Generative Video
* **Google Lyria:** Audio / Music Generation

### Infrastructure & Engineering
* **FastAPI:** High-performance async Python backend server
* **Nano Banana:** Headless URL scraping / data-fetching layer
* **Firebase Realtime DB:** Decoupled state management between UI and Workers
* **Pydantic:** Schema validation for precise LLM outputs
* **Streamlit:** Frontend Dashboard UI with Custom CSS injections

---

## ⚙️ Architecture Flow

1. **Input:** User submits `https://example.com` into the UI.
2. **Extraction:** FastAPI delegates Nano Banana to scrape the visual semantics and text.
3. **Brain Synthesis:** Gemini 1.5 Pro outputs a strictly typed JSON block specifying visual aesthetic and audio tempo.
4. **Agent Orchestration:** The backend worker reads the contract and independently triggers Veo and Lyria endpoints.
5. **Compositing:** Rendered clips are stitched together and fed securely back to the Streamlit dashboard as an `.mp4`.

---

## 💻 Getting Started

### Prerequisites
* Python 3.9+
* API Keys for Gemini, Veo, Lyria, Nano Banana
* Firebase Credentials

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd BrandSync_Google_Gemini_Project
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your Environment Variables:**
   Create a `.env` file in the root and add your API credentials:
   ```env
   GEMINI_API_KEY="..."
   NANO_BANANA_KEY="..."
   # ... add other required keys
   ```

4. **Run the Backend (FastAPI):**
   ```bash
   # In a new terminal
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Run the Frontend (Streamlit):**
   ```bash
   # In a new terminal
   streamlit run frontend/app.py
   ```

---

## ☁️ Deployment Guide

* **Streamlit Community Cloud:** Host `frontend/app.py`. Note: Ensure you configure your secrets securely via the Streamlit dashboard (`Advanced Settings -> Secrets`).
* **Render / Railway / GCP:** Host the backend layer (`main.py`) as a web-service, then update the `API_BASE_URL` in your Streamlit secrets to point to your deployed backend URL.

---

### License
Built for the Google Gemini Developer Hackathon.