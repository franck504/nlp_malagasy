import os
import argparse
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace

def train_tokenizer(corpus_path, output_dir, vocab_size=30000):
    print("======================================================================")
    print("🧠 ENTRAÎNEMENT DU TOKENIZER (BPE - Morphologie Malgache)")
    print(f"   Corpus : {corpus_path}")
    print(f"   Vocab  : {vocab_size} mots/sous-mots")
    print("======================================================================")

    if not os.path.exists(corpus_path):
        print(f"❌ Erreur : Le fichier {corpus_path} est introuvable.")
        return

    # 1. Initialiser le modèle BPE
    tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
    tokenizer.pre_tokenizer = Whitespace()

    # 2. Configurer l'entraîneur (Trainer)
    trainer = BpeTrainer(
        vocab_size=vocab_size,
        min_frequency=2,
        show_progress=True,
        special_tokens=["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"]
    )

    # 3. Entraîner sur le corpus
    print("📖 Apprentissage des patterns linguistiques...")
    tokenizer.train(files=[corpus_path], trainer=trainer)

    # 4. Sauvegarder
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    tokenizer_path = os.path.join(output_dir, "tokenizer-mg.json")
    tokenizer.save(tokenizer_path)
    
    print("======================================================================")
    print(f"✅ TOKENIZER ENTRAÎNÉ AVEC SUCCÈS !")
    print(f"💾 Sauvegardé dans : {tokenizer_path}")
    print("   Ce fichier contient maintenant l'intelligence pour découper")
    print("   les tovona (préfixes) et tovana (suffixes) malgaches.")
    print("======================================================================")

    # Test rapide
    test_text = "Ny fifankatiavana no fototry ny fiainana."
    output = tokenizer.encode(test_text)
    print(f"🔍 Test sur : '{test_text}'")
    print(f"📦 Découpage : {output.tokens}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Entraîne un tokenizer sur le corpus malgache.')
    parser.add_argument('--corpus', type=str, default='malagasy_corpus_v1_fixed.txt', help='Chemin vers le corpus consolidé')
    parser.add_argument('--output', type=str, default='tokenizer_mg', help='Dossier de sortie')
    parser.add_argument('--vocab', type=int, default=30000, help='Taille du vocabulaire')

    args = parser.parse_args()
    train_tokenizer(args.corpus, args.output, args.vocab)
