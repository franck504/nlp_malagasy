import os
import numpy as np
import json
from gensim.models import FastText
from tqdm import tqdm
import argparse

class MalagasyNLPApp:
    def __init__(self, model_path, corpus_dir):
        print(f"📦 Chargement du modèle {model_path}...")
        self.model = FastText.load(model_path)
        self.corpus_dir = corpus_dir
        self.index_path = "semantic_index.json"
        self.song_index = []

    def get_sentence_vector(self, text):
        """Calcule le vecteur moyen d'une phrase/paragraphe."""
        words = text.lower().replace('.', '').replace(',', '').split()
        vectors = [self.model.wv[w] for w in words if w in self.model.wv]
        if not vectors:
            return np.zeros(self.model.vector_size)
        return np.mean(vectors, axis=0)

    def build_index(self):
        """Indexe sémantiquement tous les fichiers .txt du dossier corpus."""
        if os.path.exists(self.index_path):
            print(f"ℹ️ Index existant trouvé ({self.index_path}). Chargement...")
            with open(self.index_path, 'r', encoding='utf-8') as f:
                self.song_index = json.load(f)
            return

        print(f"🏗️ Création de l'index sémantique depuis {self.corpus_dir}...")
        indexed_data = []
        
        # Parcourir Artistes/Chansons
        if not os.path.exists(self.corpus_dir):
            print(f"❌ Erreur : Dossier {self.corpus_dir} introuvable.")
            return

        artists = [d for d in os.listdir(self.corpus_dir) if os.path.isdir(os.path.join(self.corpus_dir, d))]
        for artist in tqdm(artists, desc="Indexation des artistes"):
            artist_path = os.path.join(self.corpus_dir, artist)
            for song_file in os.listdir(artist_path):
                if song_file.endswith(".txt"):
                    path = os.path.join(artist_path, song_file)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            vector = self.get_sentence_vector(content)
                            indexed_data.append({
                                "artist": artist,
                                "title": song_file.replace(".txt", ""),
                                "vector": vector.tolist(),
                                "snippet": content[:200] + "..."
                            })
                    except:
                        continue
        
        self.song_index = indexed_data
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(indexed_data, f)
        print(f"✅ Indexation terminée : {len(indexed_data)} chansons indexées.")

    def semantic_search(self, query, top_k=5):
        """Recherche par sens."""
        query_vec = self.get_sentence_vector(query)
        similarities = []
        
        for item in self.song_index:
            item_vec = np.array(item["vector"])
            norm_a = np.linalg.norm(query_vec)
            norm_b = np.linalg.norm(item_vec)
            if norm_a == 0 or norm_b == 0:
                score = 0
            else:
                score = np.dot(query_vec, item_vec) / (norm_a * norm_b)
            similarities.append((score, item))
            
        similarities.sort(key=lambda x: x[0], reverse=True)
        return similarities[:top_k]

    def spell_check(self, word):
        """Suggère des corrections basées sur FastText."""
        try:
            similars = self.model.wv.most_similar(word, topn=3)
            return [s[0] for s in similars]
        except:
            return []

    def explore_concept(self, word):
        """Affiche le 'nuage' sémantique d'un mot."""
        try:
            return self.model.wv.most_similar(word, topn=10)
        except:
            return []

    def solve_analogy(self, a, b, c):
        """A est à B ce que C est à ?"""
        try:
            res = self.model.wv.most_similar(positive=[b, c], negative=[a], topn=3)
            return [r[0] for r in res]
        except:
            return []

    def detect_style(self, text):
        """Style Bible, Wikipédia ou Lyrics."""
        anchors = {
            "Bible": ["andriamanitra", "jesosy", "famonjena", "israely", "tenindriamanitra"],
            "Wikipedia": ["tantara", "jeografia", "politika", "firenena", "siansa"],
            "Lyrics": ["fitiavana", "hira", "foko", "malala", "tsiky"]
        }
        text_vec = self.get_sentence_vector(text)
        scores = {}
        for name, words in anchors.items():
            anchor_vec = self.get_sentence_vector(" ".join(words))
            norm_a = np.linalg.norm(text_vec)
            norm_b = np.linalg.norm(anchor_vec)
            score = np.dot(text_vec, anchor_vec) / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0
            scores[name] = score
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def main():
    parser = argparse.ArgumentParser(description="Application de test NLP Malagasy.")
    parser.add_argument("--query", type=str, help="Recherche sémantique")
    parser.add_argument("--spell", type=str, help="Correction")
    parser.add_argument("--explore", type=str, help="Exploration")
    parser.add_argument("--analogy", type=str, nargs=3, help="Analogy A B C")
    parser.add_argument("--style", type=str, help="Style detection")
    parser.add_argument("--index", action="store_true", help="Réindexer")
    
    args = parser.parse_args()
    
    app = MalagasyNLPApp(
        model_path="embeddings_mg/malagasy_fasttext.model", 
        corpus_dir="output"
    )
    
    if args.index:
        if os.path.exists("semantic_index.json"): os.remove("semantic_index.json")
    app.build_index()

    print("\n" + "="*55)
    if args.spell:
        print(f"📝 CORRECTION : '{args.spell}' suggestions -> {', '.join(app.spell_check(args.spell))}")
    if args.explore:
        print(f"🧠 CONCEPT : '{args.explore}'")
        for word, score in app.explore_concept(args.explore): print(f"   - {word:<20} ({score:.4f})")
    if args.analogy:
        print(f"⚖️ ANALOGIE : '{args.analogy[0]}' -> '{args.analogy[1]}' comme '{args.analogy[2]}' -> {', '.join(app.solve_analogy(*args.analogy))}")
    if args.style:
        print(f"🎭 STYLE : '{args.style}'")
        for s, sc in app.detect_style(args.style): print(f"   - {s:<15} ({sc:.4f})")
    if args.query:
        print(f"🔍 RECHERCHE : '{args.query}'")
        for s, i in app.semantic_search(args.query): print(f"[{s:.4f}] {i['artist']} - {i['title']}\n      {i['snippet']}")
    print("="*55)

if __name__ == "__main__":
    main()
