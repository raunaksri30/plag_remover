# -*- coding: utf-8 -*-
"""
Plagiarism Removal Tool - Context-Aware POS & Detokenizer Version
"""

import random
import string
import tkinter as tk
from tkinter import messagebox
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer

# 1. Safely ensure all required NLTK packages (including newer NLTK 3.9+ names) are present
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

def get_wordnet_pos(treebank_tag):
    """Map Penn Treebank POS tags from whole-sentence tagging to WordNet POS tags."""
    if treebank_tag.startswith('J'):
        return wn.ADJ
    elif treebank_tag.startswith('V'):
        return wn.VERB
    elif treebank_tag.startswith('N'):
        return wn.NOUN
    elif treebank_tag.startswith('R'):
        return wn.ADV
    return None

def plagiarism_remover(word, treebank_tag):
    """Find a context-appropriate synonym matching the word's exact POS in the sentence."""
    # Check lowercase against stopwords so capitalized starters like "The" or "In" are skipped
    if word.lower() in stop_words or word in string.punctuation or not word.isalpha():
        return word

    # Skip proper nouns (names, places, brands) so we don't corrupt factual entities
    if treebank_tag in ('NNP', 'NNPS'):
        return word

    wn_pos = get_wordnet_pos(treebank_tag)
    if not wn_pos:
        return word

    # Query only the primary synsets (top 2 most common senses) for that exact Part of Speech
    synsets = wn.synsets(word.lower(), pos=wn_pos)
    if not synsets:
        return word

    candidates = set()
    for syn in synsets[:2]:
        for lemma in syn.lemmas():
            syn_word = lemma.name().replace('_', ' ')
            # Keep clean single-word replacements that aren't identical to the original word
            if ' ' not in syn_word and '-' not in syn_word and syn_word.lower() != word.lower():
                candidates.add(syn_word)

    if not candidates:
        return word

    # Verify candidate matches the exact inflection/sub-tag (e.g., VBD past tense vs VBG gerund)
    valid_synonyms = []
    for candidate in candidates:
        cand_tag = nltk.pos_tag([candidate])[0][1]
        if cand_tag == treebank_tag:
            valid_synonyms.append(candidate)

    # Fallback to general POS candidates if strict inflection check filters everything out
    pool = valid_synonyms if valid_synonyms else list(candidates)
    chosen = random.choice(pool)

    # Preserve original capitalization
    if word.isupper():
        return chosen.upper()
    elif word.istitle():
        return chosen.title()
    return chosen.lower()

def plagiarism_removal(para):
    """Process paragraph line-by-line to preserve line breaks and sentence context."""
    paragraphs = para.splitlines()
    processed_paragraphs = []

    for line in paragraphs:
        if not line.strip():
            processed_paragraphs.append("")
            continue
        
        tokens = word_tokenize(line)
        # Tag the entire sentence at once so NLTK has full grammatical context
        tagged_tokens = nltk.pos_tag(tokens)
        
        new_tokens = [plagiarism_remover(word, tag) for word, tag in tagged_tokens]
        # Cleanly rebuild sentence without breaking contractions ("don't") or punctuation
        processed_paragraphs.append(detokenizer.detokenize(new_tokens))

    return "\n".join(processed_paragraphs)

# --- Tkinter GUI ---
current_result = ""

def process_text():
    global current_result
    input_text = text_input.get("1.0", tk.END).strip()
    if not input_text:
        messagebox.showwarning("Empty Input", "Please enter some text first.")
        return
    
    label_status.config(text="Processing...", fg="#1976D2")
    root.update_idletasks()
    
    result = plagiarism_removal(input_text)
    current_result = result
    
    text_output.delete("1.0", tk.END)
    text_output.insert(tk.END, result)
    label_status.config(text="✓ Done!", fg="green")

def copy_to_clipboard():
    output_text = text_output.get("1.0", tk.END).strip()
    if not output_text:
        messagebox.showinfo("Nothing to copy", "There is no result text to copy yet.")
        return
    root.clipboard_clear()
    root.clipboard_append(output_text)
    root.update()
    label_status.config(text="✓ Copied to clipboard!", fg="green")

root = tk.Tk()
root.geometry('750x650')
root.title('Plagiarism Removal Tool')
root.configure(padx=20, pady=20)

label_title = tk.Label(root, text="Plagiarism Remover", font=("Arial", 16, "bold"))
label_title.pack(anchor="w", pady=(0, 10))

label_in = tk.Label(root, text="Enter text to remove plagiarism:", font=("Arial", 11))
label_in.pack(anchor="w", pady=(5, 5))

text_input = tk.Text(root, height=8, font=("Arial", 10), wrap="word")
text_input.pack(fill="x", pady=(0, 10))

frame_actions = tk.Frame(root)
frame_actions.pack(anchor="w", pady=(0, 15))

btn_remove = tk.Button(
    frame_actions, text="Remove Plagiarism", font=("Arial", 10, "bold"),
    bg="#1976D2", fg="white", padx=10, pady=5, command=process_text
)
btn_remove.pack(side="left", padx=(0, 10))

btn_copy = tk.Button(
    frame_actions, text="📋 Copy Result", font=("Arial", 10),
    bg="#E0E0E0", padx=10, pady=5, command=copy_to_clipboard
)
btn_copy.pack(side="left")

label_status = tk.Label(frame_actions, text="", font=("Arial", 10, "italic"))
label_status.pack(side="left", padx=15)

label_out = tk.Label(root, text="Result (selectable and copyable):", font=("Arial", 11))
label_out.pack(anchor="w", pady=(5, 5))

text_output = tk.Text(root, height=10, font=("Arial", 10), wrap="word")
text_output.pack(fill="both", expand=True, pady=(0, 10))

root.mainloop()