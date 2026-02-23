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
            similars = model.wv.most_similar(word_lower, topn=1)
            if similars[0][1] < 0.7: # Seuil de confiance arbitraire
                errors.append(word)
                
    return jsonify({"errors": errors})

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({"suggestions": []})
        
    data = request.json
    text = data.get("text", "")
    
    if not text:
        return jsonify({"suggestions": []})
        
    # Cas 1 : L'utilisateur est en train de taper un mot (pas d'espace à la fin)
    # On fait de l'AUTO-COMPLÉTION (Prefix Search)
    if not text.endswith(' '):
        last_word_part = text.split()[-1].lower()
        if len(last_word_part) < 2:
            return jsonify({"suggestions": []})
            
        # On cherche dans le vocabulaire les mots qui commencent par ce préfixe
        suggestions = [w for w in model.wv.index_to_key if w.startswith(last_word_part)][:5]
        return jsonify({"suggestions": suggestions, "type": "completion"})
        
    # Cas 2 : L'utilisateur a fini un mot (espace à la fin)
    # On fait de la PRÉDICTION du mot suivant (Contextual)
    else:
        last_word = text.strip().split()[-1].lower()
        try:
            # FastText donne des mots sémantiquement proches
            raw_suggestions = model.wv.most_similar(last_word, topn=10)
            
            # On filtre pour éviter les répétitions et garder les 3 meilleurs
            suggestions = [s[0] for s in raw_suggestions if s[0] != last_word][:3]
            return jsonify({"suggestions": suggestions, "type": "prediction"})
        except:
            return jsonify({"suggestions": []})

if __name__ == '__main__':
    load_model()
    # On désactive use_reloader pour éviter le double chargement de RAM
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
