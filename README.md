# Deepfake Detection System

An AI-driven toolkit for identifying manipulated images (“deepfakes”) via both a command-line interface (CLI) and an intuitive Streamlit web application.

---

## 🚀 Key Features

* **Dual Interfaces**

  * **CLI (`main.py`)**: Step-by-step prompts for language selection, image source (URL or local path), regional context, and ownership details—outputs legal considerations and SDG impact statements.
  * **Web App (`app.py`)**: Streamlit-based GUI offering language and country selection, image input, instant preview, legal guidance, and downloadable CSV reports.

* **Robust Deep Learning Core**

  * Powered by Hugging Face’s `prithivMLmods/Deep-Fake-Detector-Model`.
  * Integrates ResNet/CNN and Transformer architectures for per-pixel authenticity scoring.
  * Configurable decision threshold via the `FAKE_THRESHOLD` environment variable.

* **Multilingual Legal Compliance**

  * Interfaces in **English** and **Türkçe**.
  * Country-specific legal references for Turkey, USA, Germany, France, and India.
  * Sustainable Development Goals (SDG) impact messages to highlight social implications.

* **Logging & User Feedback**

  * Automatically appends results to `deepfake_results.csv` (CLI) or `deepfake_sonuclar.csv` (web).
  * In-app feedback button allows users to report misclassifications.

---

## 🛠️ Technology Stack

* **Python 3.8+**
* **Streamlit** for the web interface
* **Transformers** (Hugging Face) for model inference
* **Pillow** and **requests** for image I/O
* Built-in **csv** and **os** modules for result persistence

---

## 📥 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/dogaulkua/Deepfake.git
   cd Deepfake
   ```
2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   .\\.venv\\Scripts\\activate  # Windows
   ```
3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Usage

### 1. Command-Line Interface

```bash
python main.py
```

* Select your language (English/Türkçe).
* Provide an image URL or local file path.
* Specify your region and whether you own the image.
* View authenticity verdict, legal notes, and SDG insights in the console.
* Results saved to `deepfake_results.csv`.

### 2. Streamlit Web Application

```bash
streamlit run app.py
```

* In the browser:

  1. Choose interface language and country context.
  2. Enter an image URL.
  3. Click **Analyze** to see: image preview, “Real” vs. “Fake” verdict, legal guidance, and feedback option.
* Downloads and feedback data recorded in `deepfake_sonuclar.csv`.

---

## 🔍 How It Works

1. **Image Acquisition & Validation**: Supports JPEG and PNG formats; verifies accessibility.
2. **Model Inference**: Utilizes a Hugging Face pipeline returning a list of `{\"label\": \"Real\"|\"Fake\", \"score\": float}` entries.
3. **Score Aggregation**:

   ```python
   real_score = sum(item["score"] for item in results if item["label"].lower() == "real")
   fake_score = sum(item["score"] for item in results if item["label"].lower() == "fake")
   ```
4. **Decision Logic**: Compares aggregated scores against each other and the `FAKE_THRESHOLD` (default: 0.1) to classify the image.
5. **Result Logging**: Captures URL/path, individual scores, and final classification in a CSV file.

---




## 📹 Demo Video

https://github.com/user-attachments/assets/ab438127-1c7c-4426-8f7d-eebede109c89
