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

def get_word_freq(w):
    try:
        return model.wv.get_vecattr(w.lower(), "count")
    except:
        return 0

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
    
    print(f"\n--- Analyse de texte ---")
    
    for word in words:
        word_lower = word.lower()
        freq = get_word_freq(word_lower)
        
        # LOGIQUE DÉTECTION :
        # Un mot est considéré "Correct" si :
        # 1. Il est fréquent dans le corpus (freq >= 5)
        # 2. OU il est moyennement fréquent (1-4) ET il a un score de confiance sémantique très élevé
        
        is_error = False
        
        if freq < 5:
            # Si le mot est rare ou absent, on demande l'avis sémantique de l'IA
            try:
                similars = model.wv.most_similar(word_lower, topn=1)
                score = similars[0][1]
                
                # Seuil de tolérance : 
                # Si le mot est absent (freq=0) et score < 0.85 -> Erreur
                # Si le mot est très rare (freq < 5) et score < 0.75 -> Erreur
                if freq == 0 and score < 0.85:
                    is_error = True
                elif freq > 0 and score < 0.70:
                    is_error = True
                    
                if is_error:
                    print(f"🚩 FAUTE : '{word}' (Freq: {freq}, Score: {score:.4f})")
            except:
                is_error = True
                print(f"🚩 FAUTE : '{word}' (Mot inconnu et impossible à analyser)")

        if is_error:
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
            
        # PRIORITÉ : index_to_key est trié par fréquence décroissante.
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
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
