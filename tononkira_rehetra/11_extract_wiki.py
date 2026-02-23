import bz2
import xml.etree.ElementTree as ET
import re
import os
from tqdm import tqdm

def clean_wiki_text(text):
    # Suppression élémentaire du balisage Wiki
    text = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', text) # Liens [[A|B]] -> B
    text = re.sub(r"'''+", "", text) # Gras/Italique
    text = re.sub(r'\{?\{[^\}]+\}\}?', '', text) # Modèles {{...}}
    text = re.sub(r'==+[^=]+==+', '', text) # Titres de sections
    text = re.sub(r'\[http[^\s]+ ([^\]]+)\]', r'\1', text) # Liens externes
    text = re.sub(r'<[^>]+>', '', text) # Balises HTML restant
    
    # Nettoyage des espaces
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()

def extract_wiki(input_bz2, output_txt):
    print("======================================================================")
    print("🏗️ EXTRACTION PERSONNALISÉE DE WIKIPÉDIA MALAGASY")
    print(f"   Source : {input_bz2}")
    print("======================================================================")

    if not os.path.exists(input_bz2):
        print(f"❌ Erreur : {input_bz2} introuvable.")
        return

    count = 0
    with bz2.open(input_bz2, 'rb') as f_in, open(output_txt, 'w', encoding='utf-8') as f_out:
        # On itère sur les tags <page> du XML
        context = ET.iterparse(f_in, events=('end',))
        
        for event, elem in tqdm(context, desc="Extraction des articles"):
            # Enlever les namespaces du tag (ex: {http://www.mediawiki.org/xml/export-0.10/}page)
            tag = elem.tag.split('}')[-1]
            
            if tag == 'page':
                title = elem.find('.//{*}title').text
                # On ignore les pages spéciales (Utilisateur, Discussion, etc.)
                if title and ':' not in title:
                    revision = elem.find('.//{*}revision')
                    if revision is not None:
                        text_elem = revision.find('.//{*}text')
                        if text_elem is not None and text_elem.text:
                            content = clean_wiki_text(text_elem.text)
                            if len(content) > 100: # On ignore les ébauches trop courtes
                                f_out.write(f"--- {title} ---\n")
                                f_out.write(content + "\n\n")
                                count += 1
                
                # Libérer la mémoire
                elem.clear()
            
    print(f"\n✅ Extraction terminée !")
    print(f"📊 {count} articles extraits dans {output_txt}")
    print("======================================================================")

if __name__ == "__main__":
    input_file = "../mgwiki-latest-pages-articles.xml.bz2"
    output_file = "../malagasy_wikipedia_raw.txt"
    extract_wiki(input_file, output_file)
