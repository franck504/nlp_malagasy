from flask import Flask, render_template, request, jsonify, make_response
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
    response = make_response(render_template('index.html'))
    # On force le navigateur à ne pas mettre en cache pour le développement
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response

@app.route('/check', methods=['POST'])
def check():
    if model is None:
        return jsonify({"errors": []})
        
    data = request.json
    text = data.get("text", "")
    
    # On ignore les nombres et les symboles, on ne garde que les lettres et tirets
    words = re.findall(r"\b[a-zA-Zà-ÿ'-]+\b", text)
    errors = []
    
    for word in words:
        word_lower = word.lower()
        # 1. Vérification directe dans le vocabulaire
        if word_lower not in model.wv:
            # 2. Vérification sémantique pour les mots "inconnus"
            try:
                # FastText génère un vecteur même pour l'inconnu. 
                similars = model.wv.most_similar(word_lower, topn=1)
                score = similars[0][1]
                # Seuil relevé à 0.80 pour détecter les fautes plus facilement
                if score < 0.80: 
                    errors.append(word)
                    print(f"🚩 Faute détectée : '{word}' (Score: {score:.4f})")
            except:
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
        
    # Cas 1 : AUTO-COMPLÉTION (Prefix Search)
    if not text.endswith(' '):
        last_word_part = text.split()[-1].lower()
        if len(last_word_part) < 2:
            return jsonify({"suggestions": []})
            
        suggestions = [w for w in model.wv.index_to_key if w.startswith(last_word_part)][:5]
        return jsonify({"suggestions": suggestions, "type": "completion"})
        
    # Cas 2 : PRÉDICTION DU MOT SUIVANT (Contextual)
    else:
        last_word = text.strip().split()[-1].lower()
        try:
            raw_suggestions = model.wv.most_similar(last_word, topn=15)
            suggestions = []
            for s in raw_suggestions:
                s_word = s[0]
                if s_word != last_word and not s_word.startswith(last_word[:4]):
                    suggestions.append(s_word)
                if len(suggestions) >= 3: break
            return jsonify({"suggestions": suggestions, "type": "prediction"})
        except:
            return jsonify({"suggestions": []})

if __name__ == '__main__':
    load_model()
    # Debug=True avec use_reloader=False 
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
