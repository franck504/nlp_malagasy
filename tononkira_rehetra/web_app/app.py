from flask import Flask, render_template, request, jsonify
from gensim.models import FastText
import os
import re

app = Flask(__name__)

# Config
MODEL_PATH = "model/malagasy_fasttext.model"
model = None

def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        print(f"📦 Chargement du cerveau Malagasy: {MODEL_PATH}")
        model = FastText.load(MODEL_PATH)
        print("✅ Modèle chargé !")
    else:
        print(f"⚠️ Modèle introuvable à {MODEL_PATH}. L'app fonctionnera sans IA.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    if model is None:
        return jsonify({"errors": []})
        
    data = request.json
    text = data.get("text", "")
    
    # Extraction des mots (on garde la ponctuation pour le mapping)
    words = re.findall(r"\b\w+\b", text)
    errors = []
    
    for word in words:
        word_lower = word.lower()
        # Si le mot n'est pas dans le vocabulaire connu
        if word_lower not in model.wv:
            # On vérifie si FastText peut le "comprendre" quand même (subwords)
            # Sinon on le marque comme erreur potentielle
            # (Note: FastText a tjs une réponse, on utilise un score de confiance)
            similars = model.wv.most_similar(word_lower, topn=1)
            if similars[0][1] < 0.7: # Seuil de confiance arbitraire
                errors.append(word)
                
    return jsonify({"errors": errors})

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({"suggestions": []})
        
    data = request.json
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"suggestions": []})
        
    last_word = text.split()[-1].lower()
    
    try:
        # On demande les mots qui apparaissent souvent dans le même contexte
        suggestions = model.wv.most_similar(last_word, topn=5)
        # On ne garde que les mots qui ne sont pas des variations du mot actuel
        clean_suggestions = [s[0] for s in suggestions if s[0] != last_word][:3]
        return jsonify({"suggestions": clean_suggestions})
    except:
        return jsonify({"suggestions": []})

if __name__ == '__main__':
    load_model()
    app.run(host='0.0.0.0', port=5000, debug=True)
