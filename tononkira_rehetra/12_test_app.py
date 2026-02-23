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
        artists = [d for d in os.listdir(self.corpus_dir) if os.path.isdir(os.path.join(self.corpus_dir, d))]
        for artist in tqdm(artists, desc="Indexation des artistes"):
            artist_path = os.path.join(self.corpus_dir, artist)
            for song_file in os.listdir(artist_path):
                if song_file.endswith(".txt"):
                    path = os.path.join(artist_path, song_file)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # On prend le vecteur moyen du texte
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
            # Similarité cosinus
            norm_a = np.linalg.norm(query_vec)
            norm_b = np.linalg.norm(item_vec)
            if norm_a == 0 or norm_b == 0:
                score = 0
            else:
                score = np.dot(query_vec, item_vec) / (norm_a * norm_b)
            similarities.append((score, item))
            
        # Trier par score décroissant
        similarities.sort(key=lambda x: x[0], reverse=True)
        return similarities[:top_k]

    def spell_check(self, word):
        """Suggère des corrections basées sur FastText."""
        try:
            # FastText est excellent pour ça car il connaît les subwords
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

def main():
    parser = argparse.ArgumentParser(description="Application de test NLP Malagasy.")
    parser.add_argument("--query", type=str, help="Requête de recherche sémantique")
    parser.add_argument("--spell", type=str, help="Mot à corriger")
    parser.add_argument("--explore", type=str, help="Concept à explorer")
    parser.add_argument("--index", action="store_true", help="Force la reconstruction de l'index")
    
    args = parser.parse_args()
    
    app = MalagasyNLPApp(
        model_path="embeddings_mg/malagasy_fasttext.model", 
        corpus_dir="output"
    )
    
    if args.index:
        if os.path.exists("semantic_index.json"): os.remove("semantic_index.json")
        app.build_index()
        return

    app.build_index()

    print("\n" + "="*50)
    if args.spell:
        print(f"📝 CORRECTION POUR : '{args.spell}'")
        suggestions = app.spell_check(args.spell)
        print(f"👉 Suggestions : {', '.join(suggestions)}")
    
    if args.explore:
        print(f"🧠 EXPLORATION DU CONCEPT : '{args.explore}'")
        relatives = app.explore_concept(args.explore)
        for word, score in relatives:
            print(f"   - {word:<20} (score: {score:.4f})")
            
    if args.query:
        print(f"🔍 RECHERCHE SÉMANTIQUE : '{args.query}'")
        results = app.semantic_search(args.query)
        for score, item in results:
            print(f"[{score:.4f}] {item['artist']} - {item['title']}")
            print(f"      Extrait: {item['snippet'].replace('\\n', ' ')}")
            print("-" * 30)
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
