import argparse
import os
import multiprocessing
from gensim.models import FastText
from gensim.models.word2vec import LineSentence

def train_embeddings(corpus_path, output_dir, vector_size=100, window=5, min_count=5):
    print("======================================================================")
    print("🚀 ENTRAÎNEMENT DES WORD EMBEDDINGS (FastText)")
    print(f"   Corpus : {corpus_path}")
    print(f"   Dimension : {vector_size}")
    print(f"   Fenêtre   : {window}")
    print("======================================================================")

    if not os.path.exists(corpus_path):
        print(f"❌ Erreur : Le fichier {corpus_path} est introuvable.")
        return

    # 1. Configurer le modèle FastText
    # On utilise FastText car il gère les "Subwords" (morphologie malgache)
    print("🧠 Initialisation du modèle FastText...")
    model = FastText(
        vector_size=vector_size,
        window=window,
        min_count=min_count,
        workers=multiprocessing.cpu_count(),
        sg=1 # Skip-gram (souvent meilleur pour de petits/moyens corpus)
    )

    # 2. Construire le vocabulaire
    print("📖 Construction du vocabulaire...")
    sentences = LineSentence(corpus_path)
    model.build_vocab(corpus_iterable=sentences)

    # 3. Entraîner
    print("🔥 Entraînement en cours (cela peut prendre quelques minutes)...")
    model.train(
        corpus_iterable=sentences,
        total_examples=model.corpus_count,
        epochs=10
    )

    # 4. Sauvegarder
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    model_path = os.path.join(output_dir, "malagasy_fasttext.model")
    model.save(model_path)
    
    print("======================================================================")
    print(f"✅ EMBEDDINGS ENTRAÎNÉS AVEC SUCCÈS !")
    print(f"💾 Sauvegardé dans : {model_path}")
    print("======================================================================")

    # Test de similarité
    word_test = "fitiavana"
    print(f"🔍 Test de similarité pour : '{word_test}'")
    try:
        similar_words = model.wv.most_similar(word_test, topn=5)
        for word, score in similar_words:
            print(f"   - {word}: {score:.4f}")
    except KeyError:
        print(f"   ⚠️ Le mot '{word_test}' n'a pas été trouvé dans le vocabulaire.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Entraîne des embeddings FastText sur le corpus malgache.')
    parser.add_argument('--corpus', type=str, default='malagasy_corpus_v1_fixed.txt', help='Chemin vers le corpus consolidé')
    parser.add_argument('--output', type=str, default='embeddings_mg', help='Dossier de sortie')
    parser.add_argument('--size', type=int, default=100, help='Taille des vecteurs')

    args = parser.parse_args()
    train_embeddings(args.corpus, args.output, vector_size=args.size)
