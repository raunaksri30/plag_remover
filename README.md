# 📝 Plagiarism Remover & AI Humanizer (Hybrid Edition)

An intelligent desktop application built with Python, NLTK, PyTorch, Transformers, and Tkinter that paraphrases text to eliminate **both Plagiarism AND AI Detection (ZeroGPT, GPTZero, Turnitin AI)** while **strictly preserving meaning, natural flow, and grammatical accuracy**.

---

## ⚡ Why Was the Meaning Changing & Why Was it Flagged as GPT?

1. **Plagiarism ≠ AI Detection**:
   - Standard plagiarism checkers look for exact identical word sequences (*n*-grams).
   - AI detectors (ZeroGPT, Turnitin AI) look for **Perplexity** (word predictability) and **Burstiness** (sentence length uniformity), plus distinct **ChatGPT clichés**.
2. **The "Thesaurus Syndrome"**:
   - Blindly replacing 100% of words created gibberish (*"systems that hear from datum"*).
   - Replacing words without changing sentence cadence left the mathematical fingerprint of ChatGPT at **60–80% AI**.

---

## ✨ Key Features & Enhancements

- **🎓 Academic / Research Paper Mode**:
  - Automatically shifts intensity to **22% (Safe Scholarly Level)** to prevent technical drift.
  - **Zero Contractions**: Preserves formal writing (*"cannot"*, *"do not"*, *"it is"* stay untouched).
  - **In-Text Citation Protection**: Shields citation brackets like `[1]`, `[1-3]`, `[12, 15]` and `(Author et al., 2024)` from being altered.
  - **Scholarly Phrasing**: Replaces ChatGPT clichés with peer-reviewed academic vocabulary (*"investigate"*, *"is fundamental to"*, *"demonstrates"*, *"numerous"*).
- **👤 AI Humanizer (Bypass AI Detectors)**:
  - **ChatGPT Cliché Cleanser**: Strips overused LLM transitions and filler words.
  - **Burstiness Injection**: Splits long, uniform compound sentences into varied, punchy statements.
- **🧠 AI Neural Paraphraser (T5 Transformer)**:
  - Powered by Hugging Face `transformers` and PyTorch.
  - Deep-learning sequence-to-sequence model that rewrites full sentences from scratch (like QuillBot).
- **🎚️ Paraphrase Intensity Slider**:
  - Lets you control substitution rate: **Academic (~22%)**, **Balanced (~35% - Recommended)**, or **Strong (~50%)**.
- **🛡️ Protected Compound Phrases & Keywords**:
  - Automatically preserves technical multi-word terms (*"machine learning"*, *"convolutional neural networks"*, *"standard deviation"*, etc.).
  - Custom protection box for acronyms, datasets, and method names.
- **📚 Word Frequency & Naturalness Filter**:
  - Requires candidate synonyms to have real-world corpus frequency (`total_freq >= 2`), blocking archaic dictionary oddities.
- **🔧 Morphological Inflection & Uncountable Noun Safeguards**:
  - Keeps verbs in `-ing` (*building* → *making*) and 3rd person singular (*focuses* → *centers*).
  - Protects mass nouns (*information*, *software*, *equipment*, *data*) from incorrect pluralization.
- **🔍 Visual Diff Highlighter**:
  - One-click button to highlight every modified word in yellow/gold, with live statistics.
- **🧵 Responsive Threading**:
  - Background worker thread prevents Tkinter from freezing or hanging during execution.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- `pip` package manager

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🖥️ Usage

Run the application:

```bash
python plag.py
```

### 🎓 For Research Papers (IEEE, Springer, Elsevier, Turnitin):
1. Check **`☑️ 🎓 Academic Paper Mode`**.
2. Slider will auto-set to **22% (Safe Academic Level)**.
3. Put model names or metrics into **Protect Terms** (e.g. `CNN, ResNet, p-value, F1-score`).
4. Paste your section and click **🚀 Remove Plag & Humanize**.

### ⚡ For General Essays & Content:
1. Select your **Engine**:
   - **⚡ Smart NLTK**: Fast, 100% offline, context-aware.
   - **🧠 AI Neural Paraphraser (T5)**: Deep learning transformer rephrasing.
2. Enable **`☑️ 👤 Humanize & Bypass AI`**.
3. Adjust the **Intensity Slider** (Recommended: **35% - Balanced**).
4. Click **🚀 Remove Plag & Humanize**.

---

## 🛠️ Project Structure

```text
plag_remover/
├── plag.py             # Main application script & Tkinter GUI
├── requirements.txt    # Python dependencies (NLTK & Transformers)
└── README.md           # Documentation
```

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
