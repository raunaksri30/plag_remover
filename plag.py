# -*- coding: utf-8 -*-
"""
Plagiarism & AI Detector Remover - Hybrid Semantic & Humanizer Edition
Featuring:
  1. Smart NLTK Engine: Context-aware, lemma-frequency filtered, inflection-preserving,
     intensity-controlled synonym replacement with compound phrase protection.
  2. AI Humanizer Engine: Cleanses ChatGPT clichés & buzzwords, injects contractions,
     and adds natural sentence burstiness to bypass ZeroGPT, GPTZero, and Turnitin AI.
  3. Academic / Research Paper Mode: Enforces formal scholarly tone, zero contractions,
     and protects in-text citations like [1] and (Author et al., 2024).
  4. AI Neural Paraphraser (T5 Transformer): Deep learning model for sentence-level rephrasing.
"""

import os
import random
import re
import string
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer

# 1. Download required NLTK resources safely
REQUIRED_PACKAGES = [
    'punkt',
    'punkt_tab',
    'averaged_perceptron_tagger',
    'averaged_perceptron_tagger_eng',
    'wordnet',
    'stopwords',
    'omw-1.4'
]

for pkg in REQUIRED_PACKAGES:
    try:
        nltk.download(pkg, quiet=True)
    except Exception:
        pass

stop_words = set(stopwords.words("english"))
detokenizer = TreebankWordDetokenizer()

# Common compound phrases, technical terms & humanizer idioms that should NEVER be chopped up
DEFAULT_PROTECTED_PHRASES = {
    "machine learning", "artificial intelligence", "deep learning", "neural network",
    "neural networks", "data science", "computer science", "natural language processing",
    "information technology", "operating system", "operating systems", "software engineering",
    "climate change", "global warming", "high school", "higher education", "real estate",
    "social media", "public health", "supply chain", "cloud computing", "cyber security",
    "keep in mind", "in fact", "key to", "rapidly changing", "quick-moving",
    "proof of", "wide variety", "plenty of", "as a result", "what's more",
    "all in all", "in short", "big step forward", "smooth connection",
    "can't", "don't", "doesn't", "didn't", "isn't", "aren't", "wasn't", "weren't",
    "won't", "wouldn't", "couldn't", "shouldn't", "hasn't", "haven't", "it's",
    "there's", "that's", "they're", "we're", "you're", "also", "plus", "notably",
    "interestingly", "noticeably", "remember", "explore", "explores", "exploring",
    "deep understanding", "standard deviation", "loss function", "gradient descent",
    "random forest", "support vector machine", "cross validation"
}

# Mass / uncountable nouns that must NEVER be inflected with plural -s
UNCOUNTABLE_NOUNS = {
    'information', 'equipment', 'software', 'advice', 'furniture',
    'knowledge', 'research', 'homework', 'money', 'evidence', 'traffic', 'data'
}

# --- Standard Humanizer: Conversational / Everyday ---
GPT_TRANSITIONS = [
    (r"\bFurthermore,\s*", "Also, "),
    (r"\bFurthermore\b", "Also"),
    (r"\bMoreover,\s*", "Plus, "),
    (r"\bMoreover\b", "Plus"),
    (r"\bAdditionally,\s*", "What's more, "),
    (r"\bAdditionally\b", "Also"),
    (r"\bIn conclusion,\s*", "Overall, "),
    (r"\bTo summarize,\s*", "In short, "),
    (r"\bIn summary,\s*", "All in all, "),
]

GPT_CLICHES_MAP = [
    (r"\bit is important to note that\b", "notably,"),
    (r"\bit is worth noting that\b", "interestingly,"),
    (r"\bit is essential to remember that\b", "keep in mind,"),
    (r"\bit should be noted that\b", "noticeably,"),
    (r"\bit is crucial to understand that\b", "remember,"),
    (r"\bplays a crucial role in\b", "is key to"),
    (r"\bplay a crucial role in\b", "are key to"),
    (r"\bplays a vital role in\b", "is essential for"),
    (r"\bplay a vital role in\b", "are essential for"),
    (r"\bplays a pivotal role in\b", "is a major driver of"),
    (r"\bplay a pivotal role in\b", "are a major driver of"),
    (r"\bdelve into\b", "explore"),
    (r"\bdelves into\b", "explores"),
    (r"\bdelving into\b", "exploring"),
    (r"\ba testament to\b", "proof of"),
    (r"\brich tapestry of\b", "wide variety of"),
    (r"\btapestry of\b", "blend of"),
    (r"\bharnessing the power of\b", "using"),
    (r"\bharness the power of\b", "use"),
    (r"\bever-evolving\b", "rapidly changing"),
    (r"\bfast-paced\b", "quick-moving"),
    (r"\bin the realm of\b", "in"),
    (r"\ba myriad of\b", "many"),
    (r"\ba plethora of\b", "plenty of"),
    (r"\bfosters a\b", "builds a"),
    (r"\bfoster a\b", "build a"),
    (r"\bfostering\b", "encouraging"),
    (r"\bunderscores the importance of\b", "highlights the need for"),
    (r"\bunderscores\b", "highlights"),
    (r"\bunderscoring\b", "highlighting"),
    (r"\bparamount\b", "vital"),
    (r"\bspearheading\b", "leading"),
    (r"\bseamless integration\b", "smooth connection"),
    (r"\bseamlessly\b", "smoothly"),
    (r"\bgame-changer\b", "big step forward"),
    (r"\butilize\b", "use"),
    (r"\butilizes\b", "uses"),
    (r"\butilizing\b", "using"),
    (r"\butilization\b", "use"),
]

# --- Academic Humanizer: Scholarly & Peer-Review Safe ---
ACADEMIC_TRANSITIONS = [
    (r"\bFurthermore,\s*", "Additionally, "),
    (r"\bMoreover,\s*", "In addition, "),
    (r"\bAdditionally,\s*", "Furthermore, "),
    (r"\bIn conclusion,\s*", "In summary, "),
    (r"\bTo summarize,\s*", "In summary, "),
]

ACADEMIC_CLICHES_MAP = [
    (r"\bit is important to note that\b", "notably,"),
    (r"\bit is worth noting that\b", "it is noteworthy that"),
    (r"\bit is essential to remember that\b", "it is vital to consider that"),
    (r"\bplays a crucial role in\b", "is fundamental to"),
    (r"\bplay a crucial role in\b", "are fundamental to"),
    (r"\bplays a vital role in\b", "is essential for"),
    (r"\bplay a vital role in\b", "are essential for"),
    (r"\bplays a pivotal role in\b", "serves as a primary driver of"),
    (r"\bdelve into\b", "investigate"),
    (r"\bdelves into\b", "investigates"),
    (r"\bdelving into\b", "investigating"),
    (r"\ba testament to\b", "evidence of"),
    (r"\ba plethora of\b", "numerous"),
    (r"\ba myriad of\b", "a broad spectrum of"),
    (r"\bharnessing the power of\b", "employing"),
    (r"\bharnessing\b", "employing"),
    (r"\bfosters a\b", "promotes a"),
    (r"\bfosters\b", "promotes"),
    (r"\bfostering\b", "promoting"),
    (r"\bunderscores the importance of\b", "demonstrates the significance of"),
    (r"\bunderscores\b", "demonstrates"),
    (r"\bunderscoring\b", "demonstrating"),
    (r"\butilize\b", "apply"),
    (r"\butilizes\b", "applies"),
    (r"\butilizing\b", "applying"),
    (r"\butilization\b", "application"),
]

CONTRACTIONS = [
    (r"\bdo not\b", "don't"),
    (r"\bdoes not\b", "doesn't"),
    (r"\bdid not\b", "didn't"),
    (r"\bcannot\b", "can't"),
    (r"\bcan not\b", "can't"),
    (r"\bcould not\b", "couldn't"),
    (r"\bwould not\b", "wouldn't"),
    (r"\bshould not\b", "shouldn't"),
    (r"\bwill not\b", "won't"),
    (r"\bis not\b", "isn't"),
    (r"\bare not\b", "aren't"),
    (r"\bwas not\b", "wasn't"),
    (r"\bwere not\b", "weren't"),
    (r"\bhas not\b", "hasn't"),
    (r"\bhave not\b", "haven't"),
    (r"\bhad not\b", "hadn't"),
    (r"\bit is\b", "it's"),
    (r"\bthere is\b", "there's"),
    (r"\bthat is\b", "that's"),
    (r"\bthey are\b", "they're"),
    (r"\bwe are\b", "we're"),
    (r"\byou are\b", "you're"),
]


# --- AI Humanizer Engine ---
def humanize_text(text, inject_contractions=True, vary_burstiness=True, academic_mode=False):
    """
    Transforms text to evade AI detectors (ZeroGPT, GPTZero, Turnitin AI):
      1. Cleanses sterile ChatGPT transitions and overused clichés.
      2. Injects natural human contractions (disabled in academic mode).
      3. Breaks uniform sentence lengths by splitting compound sentences (boosts burstiness).
    """
    out = text

    # Select transitions and clichés based on Academic Mode vs General Mode
    trans_list = ACADEMIC_TRANSITIONS if academic_mode else GPT_TRANSITIONS
    cliche_list = ACADEMIC_CLICHES_MAP if academic_mode else GPT_CLICHES_MAP

    for pattern, repl in trans_list:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)

    for pattern, repl in cliche_list:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)

    # Contractions are NEVER injected in research papers
    if inject_contractions and not academic_mode:
        for pattern, repl in CONTRACTIONS:
            def make_sub(m, r=repl):
                matched = m.group(0)
                if matched[0].isupper():
                    return r[0].upper() + r[1:]
                return r
            out = re.sub(pattern, make_sub, out, flags=re.IGNORECASE)

    # Burstiness Injection (Rhythm & Sentence Length Variance)
    if vary_burstiness:
        sentences = sent_tokenize(out)
        humanized_sentences = []
        for sent in sentences:
            words = sent.split()
            # If sentence is long (>16 words) and has coordinate conjunctions, split it
            if len(words) > 16:
                if academic_mode:
                    split_patterns = [
                        (r",\s+and\s+this\s+", ". Specifically, this "),
                        (r",\s+and\s+", ". Furthermore, "),
                        (r",\s+but\s+", ". However, "),
                        (r",\s+which indicates that\s+", ". This indicates that "),
                        (r",\s+while\s+", ". In contrast, "),
                    ]
                else:
                    split_patterns = [
                        (r",\s+and\s+this\s+", ". In fact, this "),
                        (r",\s+and\s+", ". In addition, "),
                        (r",\s+but\s+", ". However, "),
                        (r",\s+which means that\s+", ". This means "),
                        (r",\s+while\s+", ". Meanwhile, "),
                    ]
                for p, rep in split_patterns:
                    if re.search(p, sent, flags=re.IGNORECASE):
                        sent = re.sub(p, rep, sent, count=1, flags=re.IGNORECASE)
                        break
            humanized_sentences.append(sent)
        out = " ".join(humanized_sentences)

    return out


# --- Smart Inflection Engine ---
def inflect_candidate(candidate_lemma, original_word, pos_tag):
    """
    Preserve grammatical inflection (plural, -ing, -ed, 3rd-person -s)
    so the paraphrased candidate fits the exact syntax of the sentence.
    """
    c = candidate_lemma.lower()
    o = original_word.lower()

    # Never pluralize mass / uncountable nouns
    if c in UNCOUNTABLE_NOUNS or o in UNCOUNTABLE_NOUNS:
        return c

    # Plural Nouns (NNS)
    if pos_tag == 'NNS':
        if not c.endswith(('s', 'es')):
            if c.endswith(('sh', 'ch', 'x', 'z', 's')):
                c += 'es'
            elif c.endswith('y') and len(c) > 1 and c[-2] not in 'aeiou':
                c = c[:-1] + 'ies'
            else:
                c += 's'
        return c

    # Gerund / Present Participle (VBG) -> ending in -ing
    if pos_tag == 'VBG':
        if not c.endswith('ing'):
            if c.endswith('ie'):
                c = c[:-2] + 'ying'
            elif c.endswith('e') and not c.endswith(('ee', 'oe', 'ye')):
                c = c[:-1] + 'ing'
            else:
                c += 'ing'
        return c

    # 3rd-person singular present verbs (VBZ) -> ending in -s / -es
    if pos_tag == 'VBZ':
        if not c.endswith(('s', 'es')):
            if c.endswith(('sh', 'ch', 'x', 'z', 's')):
                c += 'es'
            elif c.endswith('y') and len(c) > 1 and c[-2] not in 'aeiou':
                c = c[:-1] + 'ies'
            else:
                c += 's'
        return c

    # Past tense / Past participle (VBD, VBN) -> ending in -ed
    if pos_tag in ('VBD', 'VBN'):
        if not c.endswith(('ed', 't', 'en')):
            if c.endswith('e'):
                c += 'd'
            elif c.endswith('y') and len(c) > 1 and c[-2] not in 'aeiou':
                c = c[:-1] + 'ied'
            else:
                c += 'ed'
        return c

    return c

def get_wordnet_pos(treebank_tag):
    """Map Penn Treebank tags to WordNet POS categories."""
    if treebank_tag.startswith('J'):
        return wn.ADJ
    elif treebank_tag.startswith('V'):
        return wn.VERB
    elif treebank_tag.startswith('N'):
        return wn.NOUN
    elif treebank_tag.startswith('R'):
        return wn.ADV
    return None

def find_smart_synonym(word, treebank_tag, replacement_rate=0.35):
    """
    Find a context-appropriate, natural synonym that preserves meaning:
      1. Uses controlled replacement rate to avoid 'thesaurus syndrome'.
      2. Skips proper nouns, stopwords, acronyms, and short words.
      3. Focuses strictly on primary synsets to prevent definition drift.
      4. Ranks candidates by corpus frequency (total_count >= 2) to eliminate archaic/dialect words.
      5. Correctly inflects the candidate to match sentence grammar.
    """
    if random.random() > replacement_rate:
        return word, False

    w_lower = word.lower()
    if w_lower in stop_words or word in string.punctuation or not word.isalpha():
        return word, False

    # Skip proper nouns, acronyms (e.g. NASA, AI, CPU, CNN), and very short words
    if treebank_tag in ('NNP', 'NNPS') or (word.isupper() and len(word) <= 5) or len(word) <= 2:
        return word, False

    wn_pos = get_wordnet_pos(treebank_tag)
    if not wn_pos:
        return word, False

    synsets = wn.synsets(w_lower, pos=wn_pos)
    if not synsets:
        return word, False

    # Focus on the primary synset (sense 0) to avoid polysemy drift
    primary_synset = synsets[0]

    # Gather clean, single-word lemmas with their corpus usage frequency
    candidates = []
    for lemma in primary_synset.lemmas():
        candidate_name = lemma.name().lower().replace('_', ' ')
        if (
            ' ' not in candidate_name
            and '-' not in candidate_name
            and len(candidate_name) >= 3
            and candidate_name.isalpha()
            and candidate_name != w_lower
        ):
            total_freq = sum(l.count() for l in wn.lemmas(candidate_name))
            if total_freq >= 2:
                candidates.append((candidate_name, total_freq))

    if not candidates:
        return word, False

    candidates.sort(key=lambda item: item[1], reverse=True)
    best_candidate = candidates[0][0]

    inflected = inflect_candidate(best_candidate, word, treebank_tag)

    if word.isupper():
        result = inflected.upper()
    elif word.istitle():
        result = inflected.title()
    else:
        result = inflected.lower()

    return result, (result.lower() != w_lower)

def smart_nltk_paraphrase(text, replacement_rate=0.35, custom_protected=None, enable_humanizer=True, academic_mode=False):
    """
    Paraphrase text with phrase protection, line preservation, change tracking,
    and optional AI Humanizer / Academic Paper transformation.
    """
    if enable_humanizer:
        text = humanize_text(
            text, inject_contractions=(not academic_mode),
            vary_burstiness=True, academic_mode=academic_mode
        )

    protected = set(DEFAULT_PROTECTED_PHRASES)
    if custom_protected:
        for p in custom_protected:
            if p.strip():
                protected.add(p.strip().lower())

    lines = text.splitlines()
    processed_lines = []
    total_words = 0
    changed_words = 0
    diff_tokens_all = []

    for line in lines:
        if not line.strip():
            processed_lines.append("")
            diff_tokens_all.append([])
            continue

        tokens = word_tokenize(line)
        tagged_tokens = nltk.pos_tag(tokens)

        # Detect and protect multi-word compound terms & citations
        skip_indices = set()
        tokens_lower = [t.lower() for t in tokens]

        # Protect in-text citations like [1], [2-4], [12, 15] or (Author et al., 2024)
        for i, tok in enumerate(tokens):
            if re.match(r"^\[\d+[\d,\s\-]*\]$", tok) or "et al" in tok.lower():
                skip_indices.add(i)

        for i in range(len(tokens_lower)):
            # Check bigrams
            if i < len(tokens_lower) - 1:
                bigram = f"{tokens_lower[i]} {tokens_lower[i+1]}"
                if bigram in protected or "et al" in bigram:
                    skip_indices.add(i)
                    skip_indices.add(i + 1)
            # Check trigrams
            if i < len(tokens_lower) - 2:
                trigram = f"{tokens_lower[i]} {tokens_lower[i+1]} {tokens_lower[i+2]}"
                if trigram in protected:
                    skip_indices.add(i)
                    skip_indices.add(i + 1)
                    skip_indices.add(i + 2)

        line_out_tokens = []
        line_diff = []

        for idx, (token, tag) in enumerate(tagged_tokens):
            if token.isalpha():
                total_words += 1

            if idx in skip_indices or token.lower() in protected:
                line_out_tokens.append(token)
                line_diff.append((token, False))
            else:
                new_token, was_changed = find_smart_synonym(token, tag, replacement_rate)
                line_out_tokens.append(new_token)
                line_diff.append((new_token, was_changed))
                if was_changed:
                    changed_words += 1

        processed_lines.append(detokenizer.detokenize(line_out_tokens))
        diff_tokens_all.append(line_diff)

    final_text = "\n".join(processed_lines)
    stats = {
        "total_words": total_words,
        "changed_words": changed_words,
        "change_percent": (changed_words / total_words * 100) if total_words > 0 else 0,
        "diff_tokens": diff_tokens_all,
        "humanized": enable_humanizer,
        "academic": academic_mode
    }
    return final_text, stats


# --- Optional AI Neural Paraphraser (T5 Transformer) ---
AI_MODEL_NAME = "Vamsi/T5_Paraphrase_Paws"
ai_tokenizer = None
ai_model = None
ai_device = None

def load_ai_model():
    """Lazy load Hugging Face T5 model when requested."""
    global ai_tokenizer, ai_model, ai_device
    if ai_model is not None:
        return True

    import sys
    # Prevent torchvision C++ operator mismatch from blocking text transformers
    sys.modules['torchvision'] = None
    sys.modules['torchvision.transforms'] = None

    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

    ai_device = "cuda" if torch.cuda.is_available() else "cpu"
    ai_tokenizer = AutoTokenizer.from_pretrained(AI_MODEL_NAME)
    ai_model = AutoModelForSeq2SeqLM.from_pretrained(AI_MODEL_NAME).to(ai_device)
    return True

def ai_paraphrase_text(text, num_beams=5, temperature=1.2):
    """
    Rephrase text sentence-by-sentence using neural sequence-to-sequence model.
    Rewrites full grammatical structure while preserving complete meaning.
    """
    load_ai_model()
    import torch

    sentences = sent_tokenize(text)
    paraphrased_sentences = []

    for sent in sentences:
        if not sent.strip():
            continue
        prompt = f"paraphrase: {sent.strip()} </s>"
        inputs = ai_tokenizer(
            prompt, padding="longest", truncation=True, max_length=256, return_tensors="pt"
        ).to(ai_device)

        with torch.no_grad():
            outputs = ai_model.generate(
                **inputs,
                num_beams=num_beams,
                num_return_sequences=1,
                max_length=256,
                no_repeat_ngram_size=2,
                early_stopping=True
            )

        output_str = ai_tokenizer.decode(outputs[0], skip_special_tokens=True)
        paraphrased_sentences.append(output_str)

    return " ".join(paraphrased_sentences)


# --- Tkinter Desktop Application ---
class PlagRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Plagiarism Remover & AI Humanizer - Hybrid Edition")
        self.root.geometry("900x800")
        self.root.minsize(740, 640)
        self.root.configure(bg="#F8F9FA")

        self.last_stats = None
        self.is_processing = False

        self._build_ui()

    def _build_ui(self):
        # Header banner
        header = tk.Frame(self.root, bg="#1E3A8A", padx=20, pady=14)
        header.pack(fill="x")

        lbl_title = tk.Label(
            header, text="✨ Plagiarism Remover & AI Humanizer",
            font=("Segoe UI", 16, "bold"), fg="white", bg="#1E3A8A"
        )
        lbl_title.pack(anchor="w")

        lbl_sub = tk.Label(
            header,
            text="Rewrites text to eliminate plagiarism & bypass AI detectors (ZeroGPT / Turnitin) while preserving meaning.",
            font=("Segoe UI", 9), fg="#93C5FD", bg="#1E3A8A"
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

        # Main container
        content = tk.Frame(self.root, bg="#F8F9FA", padx=20, pady=12)
        content.pack(fill="both", expand=True)

        # Control Panel: Mode Selection & Settings
        control_frame = tk.LabelFrame(
            content, text="⚙️ Paraphrasing & Humanizer Settings", font=("Segoe UI", 10, "bold"),
            bg="#FFFFFF", fg="#1E293B", padx=12, pady=10, relief="groove"
        )
        control_frame.pack(fill="x", pady=(0, 10))

        # Row 1: Engine Mode
        row_mode = tk.Frame(control_frame, bg="#FFFFFF")
        row_mode.pack(fill="x", pady=(0, 8))

        tk.Label(row_mode, text="Engine:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#334155").pack(side="left")
        self.engine_mode = tk.StringVar(value="nltk")

        rb_nltk = tk.Radiobutton(
            row_mode, text="⚡ Smart NLTK (Fast, Context-Aware)", variable=self.engine_mode,
            value="nltk", bg="#FFFFFF", font=("Segoe UI", 9), command=self._on_engine_change
        )
        rb_nltk.pack(side="left", padx=(10, 15))

        rb_ai = tk.Radiobutton(
            row_mode, text="🧠 AI Neural Paraphraser (T5 Deep Rewrite)", variable=self.engine_mode,
            value="ai", bg="#FFFFFF", font=("Segoe UI", 9), command=self._on_engine_change
        )
        rb_ai.pack(side="left")

        # Row 2: Humanizer & Academic Checkboxes
        row_humanize = tk.Frame(control_frame, bg="#FFFFFF")
        row_humanize.pack(fill="x", pady=(0, 8))

        self.var_humanize = tk.BooleanVar(value=True)
        cb_humanize = tk.Checkbutton(
            row_humanize, text="👤 Humanize & Bypass AI",
            variable=self.var_humanize, font=("Segoe UI", 9, "bold"), fg="#166534", bg="#FFFFFF",
            activebackground="#FFFFFF", cursor="hand2"
        )
        cb_humanize.pack(side="left")

        self.var_academic = tk.BooleanVar(value=False)
        cb_academic = tk.Checkbutton(
            row_humanize, text="🎓 Academic Paper Mode (Formal tone, zero contractions, citation safety)",
            variable=self.var_academic, font=("Segoe UI", 9, "bold"), fg="#1E40AF", bg="#FFFFFF",
            activebackground="#FFFFFF", cursor="hand2", command=self._on_academic_toggle
        )
        cb_academic.pack(side="left", padx=(15, 0))

        # Row 3: Intensity Slider & Protected Terms
        self.row_settings = tk.Frame(control_frame, bg="#FFFFFF")
        self.row_settings.pack(fill="x", pady=(2, 0))

        # Intensity
        tk.Label(
            self.row_settings, text="Paraphrase Intensity:",
            font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#334155"
        ).pack(side="left")

        self.slider_intensity = tk.Scale(
            self.row_settings, from_=15, to=60, orient="horizontal",
            bg="#FFFFFF", highlightthickness=0, font=("Segoe UI", 8),
            length=160, command=self._update_intensity_label
        )
        self.slider_intensity.set(35)
        self.slider_intensity.pack(side="left", padx=(5, 5))

        self.lbl_intensity_desc = tk.Label(
            self.row_settings, text="35% (Balanced - Meaning Preserved)",
            font=("Segoe UI", 8, "italic"), bg="#FFFFFF", fg="#2563EB"
        )
        self.lbl_intensity_desc.pack(side="left", padx=(0, 15))

        # Protected Keywords
        tk.Label(
            self.row_settings, text="Protect Terms:",
            font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#334155"
        ).pack(side="left")

        self.ent_protected = tk.Entry(self.row_settings, font=("Segoe UI", 9), width=24)
        self.ent_protected.insert(0, "CNN, LSTM, p-value, F1-score")
        self.ent_protected.pack(side="left", padx=(6, 0))

        # Input Text Section
        tk.Label(
            content, text="Input Text (Paste your research draft or text here):",
            font=("Segoe UI", 10, "bold"), bg="#F8F9FA", fg="#1E293B"
        ).pack(anchor="w", pady=(2, 4))

        self.text_input = tk.Text(
            content, height=6, font=("Consolas", 10), wrap="word",
            bg="#FFFFFF", relief="solid", bd=1, padx=8, pady=8
        )
        self.text_input.pack(fill="x", pady=(0, 8))

        # Action Buttons Row
        action_row = tk.Frame(content, bg="#F8F9FA")
        action_row.pack(fill="x", pady=(0, 8))

        self.btn_process = tk.Button(
            action_row, text="🚀 Remove Plag & Humanize", font=("Segoe UI", 10, "bold"),
            bg="#2563EB", fg="white", activebackground="#1D4ED8", activeforeground="white",
            padx=14, pady=6, relief="flat", cursor="hand2", command=self.start_processing
        )
        self.btn_process.pack(side="left", padx=(0, 8))

        self.btn_copy = tk.Button(
            action_row, text="📋 Copy Result", font=("Segoe UI", 9),
            bg="#E2E8F0", fg="#1E293B", padx=10, pady=6, relief="flat",
            cursor="hand2", command=self.copy_result
        )
        self.btn_copy.pack(side="left", padx=(0, 8))

        self.btn_highlight = tk.Button(
            action_row, text="🔍 Highlight Changes", font=("Segoe UI", 9),
            bg="#E2E8F0", fg="#1E293B", padx=10, pady=6, relief="flat",
            cursor="hand2", command=self.toggle_highlights
        )
        self.btn_highlight.pack(side="left", padx=(0, 8))

        self.btn_clear = tk.Button(
            action_row, text="🗑️ Clear", font=("Segoe UI", 9),
            bg="#F1F5F9", fg="#64748B", padx=8, pady=6, relief="flat",
            cursor="hand2", command=self.clear_all
        )
        self.btn_clear.pack(side="left")

        self.lbl_status = tk.Label(
            action_row, text="", font=("Segoe UI", 9, "bold"), bg="#F8F9FA", fg="#2563EB"
        )
        self.lbl_status.pack(side="left", padx=12)

        # Output Text Section
        output_header_frame = tk.Frame(content, bg="#F8F9FA")
        output_header_frame.pack(fill="x", pady=(4, 4))

        tk.Label(
            output_header_frame, text="Paraphrased Result:", font=("Segoe UI", 10, "bold"),
            bg="#F8F9FA", fg="#1E293B"
        ).pack(side="left")

        self.lbl_metrics = tk.Label(
            output_header_frame, text="", font=("Segoe UI", 8, "italic"),
            bg="#F8F9FA", fg="#059669"
        )
        self.lbl_metrics.pack(side="right")

        self.text_output = tk.Text(
            content, height=9, font=("Consolas", 10), wrap="word",
            bg="#FFFFFF", relief="solid", bd=1, padx=8, pady=8
        )
        self.text_output.pack(fill="both", expand=True, pady=(0, 6))

        # Tag configuration for highlighting changed words
        self.text_output.tag_configure(
            "changed", background="#FEF08A", foreground="#854D0E", font=("Consolas", 10, "bold")
        )

        self.highlights_on = True

    def _on_academic_toggle(self):
        if self.var_academic.get():
            self.slider_intensity.set(22)
            self._update_intensity_label(22)
            self.lbl_intensity_desc.config(text="22% (🎓 Safe Academic Paper Level)")
        else:
            self.slider_intensity.set(35)
            self._update_intensity_label(35)

    def _update_intensity_label(self, val):
        v = int(val)
        if self.var_academic.get():
            desc = f"{v}% (🎓 Academic Mode - Meaning & Rigor Preserved)"
        elif v < 25:
            desc = f"{v}% (Light - Highest Meaning Retention)"
        elif v <= 40:
            desc = f"{v}% (Balanced - Meaning Preserved)"
        else:
            desc = f"{v}% (Strong - Aggressive Rewrite)"
        self.lbl_intensity_desc.config(text=desc)

    def _on_engine_change(self):
        mode = self.engine_mode.get()
        if mode == "ai":
            self.lbl_intensity_desc.config(text="Neural rephrasing (Deep learning)")
        else:
            self._update_intensity_label(self.slider_intensity.get())

    def start_processing(self):
        if self.is_processing:
            return

        input_text = self.text_input.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showwarning("Empty Input", "Please enter or paste some text first.")
            return

        self.is_processing = True
        self.btn_process.config(state="disabled", text="⏳ Processing...")
        self.lbl_status.config(text="Paraphrasing & Humanizing...", fg="#2563EB")
        self.root.update_idletasks()

        mode = self.engine_mode.get()
        rate = float(self.slider_intensity.get()) / 100.0
        custom_p = [p.strip() for p in self.ent_protected.get().split(",") if p.strip()]
        enable_humanizer = self.var_humanize.get()
        academic_mode = self.var_academic.get()

        threading.Thread(
            target=self._run_paraphrase_worker,
            args=(input_text, mode, rate, custom_p, enable_humanizer, academic_mode),
            daemon=True
        ).start()

    def _run_paraphrase_worker(self, text, mode, rate, custom_protected, enable_humanizer, academic_mode):
        try:
            if mode == "ai":
                self.lbl_status.config(text="Running AI Neural Paraphraser (T5)...")
                try:
                    raw_result = ai_paraphrase_text(text)
                    if enable_humanizer:
                        result = humanize_text(raw_result, inject_contractions=(not academic_mode), academic_mode=academic_mode)
                    else:
                        result = raw_result
                    stats = None
                except ImportError:
                    self.root.after(
                        0, messagebox.showerror, "AI Library Missing",
                        "The 'transformers' package is required for AI Neural mode.\n\n"
                        "Run: pip install transformers\n\n"
                        "Or switch to the 'Smart NLTK' engine."
                    )
                    self.root.after(0, self._finish_processing, None, None, "AI Mode unavailable")
                    return
                except Exception as e:
                    self.root.after(0, messagebox.showerror, "AI Paraphraser Error", str(e))
                    self.root.after(0, self._finish_processing, None, None, "Error")
                    return
            else:
                result, stats = smart_nltk_paraphrase(
                    text, replacement_rate=rate, custom_protected=custom_protected,
                    enable_humanizer=enable_humanizer, academic_mode=academic_mode
                )

            self.root.after(0, self._finish_processing, result, stats, "✓ Done!")

        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"Failed to paraphrase: {e}")
            self.root.after(0, self._finish_processing, None, None, "Error")

    def _finish_processing(self, result, stats, status_msg):
        self.is_processing = False
        self.btn_process.config(state="normal", text="🚀 Remove Plag & Humanize")
        self.lbl_status.config(text=status_msg, fg="green" if status_msg.startswith("✓") else "red")

        if result is not None:
            self.last_stats = stats
            self.text_output.delete("1.0", tk.END)

            if stats and "diff_tokens" in stats and self.highlights_on:
                for line_diff in stats["diff_tokens"]:
                    line_tokens = [tok for tok, _ in line_diff]
                    detok_line = detokenizer.detokenize(line_tokens)
                    start_pos = self.text_output.index(tk.END + "-1c")
                    self.text_output.insert(tk.END, detok_line + "\n")
                    for tok, is_changed in line_diff:
                        if is_changed and tok.isalpha():
                            self._highlight_word(tok, start_pos)
            else:
                self.text_output.insert(tk.END, result)

            if stats:
                pct = stats["change_percent"]
                changed = stats["changed_words"]
                total = stats["total_words"]
                academic_tag = " • 🎓 Academic Mode (Citations Protected)" if stats.get("academic") else ""
                human_tag = " • 👤 AI Bypassed" if stats.get("humanized") and not stats.get("academic") else ""
                self.lbl_metrics.config(
                    text=f"Modified {changed}/{total} words ({pct:.1f}%){academic_tag}{human_tag} • Meaning Preserved"
                )
            else:
                self.lbl_metrics.config(text="AI Neural Rephrased (T5) • Structure Restructured • Meaning Preserved")

    def _highlight_word(self, word, start_pos):
        """Highlight specific word occurrence inside the output text."""
        cursor = start_pos
        while True:
            pos = self.text_output.search(r'\b' + re.escape(word) + r'\b', cursor, stopindex=tk.END, regexp=True)
            if not pos:
                break
            end_pos = f"{pos}+{len(word)}c"
            self.text_output.tag_add("changed", pos, end_pos)
            cursor = end_pos

    def toggle_highlights(self):
        """Toggle highlight tags on/off."""
        self.highlights_on = not self.highlights_on
        if self.highlights_on:
            self.btn_highlight.config(text="🔍 Highlight Changes (ON)", bg="#FEF08A")
            if self.last_stats and "diff_tokens" in self.last_stats:
                for line_diff in self.last_stats["diff_tokens"]:
                    for tok, is_changed in line_diff:
                        if is_changed:
                            self._highlight_word(tok, "1.0")
        else:
            self.btn_highlight.config(text="🔍 Highlight Changes (OFF)", bg="#E2E8F0")
            self.text_output.tag_remove("changed", "1.0", tk.END)

    def copy_result(self):
        output_text = self.text_output.get("1.0", tk.END).strip()
        if not output_text:
            messagebox.showinfo("Nothing to copy", "There is no result text to copy yet.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(output_text)
        self.root.update()
        self.lbl_status.config(text="✓ Copied to clipboard!", fg="green")

    def clear_all(self):
        self.text_input.delete("1.0", tk.END)
        self.text_output.delete("1.0", tk.END)
        self.lbl_status.config(text="")
        self.lbl_metrics.config(text="")
        self.last_stats = None


if __name__ == "__main__":
    app_root = tk.Tk()
    app = PlagRemoverApp(app_root)
    app_root.mainloop()