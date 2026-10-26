# 📝 Plagiarism Removal Tool

A context-aware desktop application built with Python, NLTK, and Tkinter that intelligently paraphrases text to reduce plagiarism while preserving grammatical structure, readability, and meaning.

---

## ✨ Features

- **Context-Aware POS Tagging**: Utilizes Penn Treebank tagging and WordNet mapping to replace words with synonyms that match their exact grammatical role (nouns, verbs, adjectives, adverbs).
- **Named Entity & Stopword Protection**:
  - Automatically skips proper nouns (`NNP`, `NNPS`) to preserve names, places, and brands.
  - Leaves common English stopwords untouched to maintain sentence naturalness.
- **Case & Formatting Preservation**:
  - Retains original capitalization (UPPERCASE, Title Case, and lowercase).
  - Preserves paragraphs, line breaks, and punctuation.
- **Smart Detokenization**: Uses NLTK's `TreebankWordDetokenizer` to prevent unwanted spaces around punctuation and contractions (e.g., `don't`).
- **Interactive GUI**:
  - Clean desktop interface powered by Tkinter.
  - One-click copy to clipboard (`📋 Copy Result`).
  - Status indicators for processing and completed actions.
- **Auto-Provisioning**: Automatically verifies and downloads necessary NLTK datasets on initial launch.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- `pip` package manager

### 1. Clone the Repository

```bash
git clone https://github.com/raunaksri30/plag_remover.git
cd plag_remover
```

### 2. (Optional) Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🖥️ Usage

Run the application:

```bash
python plag.py
```

1. Paste or type your text into the **Input** box.
2. Click **Remove Plagiarism**.
3. View the paraphrased output in the **Result** box.
4. Click **📋 Copy Result** to copy the transformed text to your clipboard.

---

## 🛠️ Project Structure

```text
plag_remover/
├── .gitignore          # Git ignore configuration
├── plag.py             # Main application script & Tkinter GUI
├── requirements.txt    # Python dependencies (NLTK)
└── README.md           # Documentation
```

---

## 📦 Dependencies

- [NLTK](https://www.nltk.org/) (`punkt`, `averaged_perceptron_tagger`, `wordnet`, `stopwords`, etc.)
- Tkinter (standard library with Python)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
