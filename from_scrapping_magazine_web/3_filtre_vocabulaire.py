#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════
   FILTRE VOCABULAIRE MALGACHE - VERSION UNIFIÉE
═══════════════════════════════════════════════════════════════════════

Ce script unifie TOUS les algorithmes de filtration pour le vocabulaire malgache.
Il remplace : clean_complementary_vocabulary.py, final_clean.py, detect_and_filter_language.py

Auteur: Franck
Date: 2024-12-25
═══════════════════════════════════════════════════════════════════════
"""

import re
from pathlib import Path
from collections import Counter
from shutil import copy2

# ═══════════════════════════════════════════════════════════════════════
# CONFIGURATION GLOBALE
# ═══════════════════════════════════════════════════════════════════════

class FilterConfig:
    """Configuration centralisée pour tous les filtres"""
    
    # Mots malgaches très fréquents (pour détection de langue)
    MALAGASY_MARKERS = {
        'ny', 'dia', 'ary', 'fa', 'ka', 'sy', 'koa', 'no',
        'amin', "amin'ny", 'tamin', "tamin'ny", 'ianao', 'aho', 'izy',
        'izay', 'izany', 'izao', 'hoe', 'ao', 'eto', 'any', 'ity',
        'ireo', 'ireny', 'mbola', 'mba', 'tsy', 'tsia', 'eny',
        'azo', 'tokony', 'mety', 'marina', 'tsara', 'ratsy',
        'lehibe', 'kely', 'be', 'vitsy', 'maro', 'olona'
    }
    
    # Liste COMPLÈTE des mots français à exclure
    FRENCH_WORDS = {
        # Articles, pronoms, conjonctions de base
        'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'à', 'au', 'aux',
        'en', 'pour', 'par', 'sur', 'dans', 'avec', 'ce', 'cette', 'ces',
        'qui', 'que', 'dont', 'où', 'ne', 'pas', 'plus', 'sans', 'tout', 'tous',
        
        # Mots français courants
        'accord', 'accueil', 'accès', 'action', 'administration', 'affaires',
        'agence', 'agents', 'agriculture', 'anciens', 'appui', 'audit',
        'aviation', 'base', 'budget', 'bureau', 'cabinet', 'chef', 'chefs',
        'code', 'colonel', 'commerce', 'commission', 'commune', 'conseil',
        'contrat', 'cour', 'culture', 'droit', 'droits', 'eau', 'ecole',
        'education', 'emploi', 'energie', 'etat', 'etudes', 'fin', 'force',
        'forces', 'formation', 'guerre', 'information', 'justice', 'loi',
        'lutte', 'membres', 'ministre', 'ministres', 'monde', 'nation',
        'ordre', 'page', 'paix', 'pays', 'plan', 'police', 'president',
        'projet', 'public', 'region', 'sante', 'securite', 'service',
        'services', 'social', 'sport', 'systeme', 'travail', 'zone',
        
        # Mots techniques/administratifs français
        'directeur', 'general', 'international', 'national', 'local',
        'regional', 'central', 'principal', 'technique', 'economique',
        'politique', 'juridique', 'financier', 'social', 'culturel',
        
        # Mots avec terminaisons françaises typiques
        'financement', 'developpement', 'environnement', 'gouvernement',
        'departement', 'investissement', 'enseignement', 'renforcement',
        
        # Ajouts de la liste étendue
        'accord', 'accueil', 'action', 'actions', 'administratif',
        'administratives', 'agents', 'agricoles', 'air', 'aires',
        'amendement', 'amiral', 'applications', 'appuis', 'arabes',
        'artisanal', 'artisanat', 'artisanaux', 'assainissement',
        'association', 'audiences', 'avantages', 'bataillon', 'batterie',
        'budget', 'bureau', 'cabinet', 'catastrophes', 'cellule',
        'central', 'centraux', 'centre', 'centres', 'certification',
        'charge', 'charges', 'circonstances', 'citerne', 'civil', 'civile',
        'coalition', 'code', 'colonel', 'combattants', 'commandement',
        'commerce', 'commission', 'commune', 'communication', 'concertation',
        'concours', 'concurrence', 'conseil', 'conseils', 'conteneurs',
        'contrat', 'contre', 'convention', 'coordination', 'corruption',
        'cour', 'couverture', 'croissance', 'culture', 'culturelle',
        'defensse', 'developpement', 'directeurs', 'direction', 'discipline',
        'division', 'domaines', 'droit', 'droits', 'durable', 'eau',
        'ecole', 'economique', 'education', 'elevage', 'emploi', 'energie',
        'energies', 'engagement', 'enseignements', 'entrepreneures',
        'entreprises', 'environnement', 'equilibre', 'etat', 'etudes',
        'evaluation', 'evolution', 'examens', 'financement', 'finances',
        'financier', 'foncier', 'fonctionnement', 'fond', 'fonds', 'force',
        'forces', 'formation', 'formations', 'forum', 'fourniture',
        'gendarmerie', 'gestion', 'gouvernance', 'grand', 'groupe',
        'groupes', 'guerre', 'habitat', 'handicap', 'haut', 'haute',
        'humain', 'humaines', 'immigration', 'inclusion', 'incubation',
        'industrie', 'industriel', 'industrielle', 'infanterie',
        'informatique', 'information', 'informations', 'infrastructure',
        'infrastructures', 'initiative', 'innovation', 'inondations',
        'insertion', 'inspection', 'institut', 'institutionnels',
        'instituts', 'intelligence', 'intendance', 'interconnexion',
        'international', 'internationale', 'intervention', 'investissement',
        'investissements', 'judiciaire', 'juridiques', 'justice', 'langue',
        'lettres', 'libre', 'licence', 'liens', 'litterature', 'local',
        'logement', 'logistique', 'loi', 'lutte', 'management', 'marine',
        'maritime', 'marche', 'masse', 'master', 'matiere', 'medecine',
        'membres', 'ministres', 'modernisation', 'monde', 'mondial',
        'monitoring', 'moral', 'mouvement', 'moyenne', 'nation', 'nationale',
        'nationales', 'nations', 'nature', 'naturelles', 'norme', 'nouveau',
        'nucleaire', 'numerique', 'nutrition', 'obligatoire', 'observatoire',
        'office', 'officiers', 'operation', 'operationnel', 'operations',
        'ordinateurs', 'ordre', 'organe', 'organisation', 'organismes',
        'orientation', 'pacte', 'page', 'paix', 'partenariat', 'partenariats',
        'parties', 'patrimoine', 'perfectionnement', 'performance',
        'permanent', 'personnel', 'personnes', 'petits', 'peut', 'phase',
        'physique', 'pillage', 'pilotage', 'plan', 'planification', 'plaine',
        'plaines', 'police', 'pollution', 'pompier', 'population', 'portuaire',
        'post', 'premier', 'principal', 'prioritaires', 'procedures',
        'produits', 'professeur', 'professionnelle', 'profit', 'programmation',
        'programme', 'progressive', 'project', 'projet', 'projets', 'promotion',
        'propriete', 'prospective', 'protection', 'protocole', 'protegees',
        'precedent', 'presence', 'presidence', 'preventive', 'public',
        'publique', 'publiques', 'pedagogie', 'peche', 'pole', 'qualite',
        'quantitatifs', 'quartier', 'quartiers', 'radio', 'rapport',
        'recherches', 'recouvrement', 'reformes', 'regime', 'region',
        'regional', 'regulation', 'relance', 'relatif', 'relation', 'relations',
        'renforcement', 'renouvelables', 'renseignements', 'ressources',
        'retour', 'reseaux', 'reserves', 'resilience', 'rouge', 'routiere',
        'royaume', 'rural', 'reduction', 'sanitaire', 'sante', 'sciences',
        'sectoriel', 'sectorielle', 'sein', 'service', 'services', 'situation',
        'smart', 'social', 'sociale', 'sociales', 'societes', 'soins',
        'solidarites', 'sous', 'soutien', 'souverain', 'sport', 'sportif',
        'sports', 'special', 'specialisees', 'strategie', 'strategies',
        'strategique', 'strategiques', 'structuration', 'structure',
        'stupefiants', 'substances', 'subvention', 'subventions', 'sud',
        'suisse', 'suite', 'suivant', 'suivi', 'superieure', 'systeme',
        'systemes', 'securite', 'senat', 'table', 'task', 'taxes',
        'technicite', 'technique', 'techniques', 'technologies', 'temple',
        'tension', 'terre', 'territoire', 'territoriale', 'territoriales',
        'terrorisme', 'topographique', 'tourisme', 'touristique', 'touristiques',
        'traitement', 'tranche', 'transfert', 'transferts', 'transformateur',
        'transnationale', 'transparence', 'transport', 'transports', 'travail',
        'tresor', 'tropicaux', 'truck', 'telecommunications', 'television',
        'unesco', 'unis', 'unite', 'universitaires', 'urbain', 'urbaine',
        'utiles', 'utilisation', 'utilite', 'uvres', 'vaccinale', 'vaccins',
        'vaisseau', 'valorisation', 'veille', 'vers', 'victimes', 'vie',
        'vienne', 'village', 'villes', 'visio', 'vivants', 'world', 'youth',
        'zone', 'ecole', 'economique', 'education', 'electrique', 'elevage',
        'energie', 'energetique', 'etat', 'evaluation', 'etes',
        
        # Mots supplémentaires français détectés
        'acces', 'accessoires', 'accompagnements', 'adjoint', 'africaine', 
        'afrique', 'alimentaires', 'aller', 'ans', 'aper', 'appauvrissent',
        'auto', 'bacs', 'basse', 'ans', 'artec', 'asam', 'avin', 'bama',
        'barea', 'baro', 'base', 'basket', 'basketball', 'ball', 'bazezy',
        'barea', 'batam', 'batterie', 'bay', 'bei', 'belo', 'bety',
        'bodybuilding', 'boly', 'bonne', 'boule', 'bruno', 'bsp', 'bus',
        'cahiers', 'can', 'cargo', 'cassette', 'certification', 'cessna',
        'champion', 'chan', 'cher', 'chevalier', 'chimie', 'chinois',
        'chinoises', 'cis', 'citerne', 'civilisation', 'civique', 'civisme',
        'clag', 'classic', 'clean', 'combattants', 'commandant', 'commandement',
        'commissaire', 'commissariat', 'commune', 'concertation', 'concours',
        'connaissances', 'connectivité', 'consommables', 'constant',
        'constitutionnelle', 'conteneurs', 'contenu', 'continentale',
        'cooking', 'coordinateur', 'coordonateur', 'coordonnateur',
        'coordonnateurs', 'cop', 'copyright', 'cost', 'couche', 'coupe',
        'couverture', 'cpf', 'cpp', 'criminalité', 'croix', 'crédits',
        'cup', 'défense', 'démonstration', 'développement', 'directeurs',
        'discipline', 'disciplines', 'discours', 'diversité', 'divisionnaire',
        'doléances', 'données', 'durable', 'dynamique', 'début',
        'décentralisation', 'décentralisées', 'déchets', 'découlant',
        'désenclavement', 'détachement', 'détails', 'eau', 'echange',
        'ecosystème', 'elevage', 'elèves', 'emergents', 'emigration',
        'emissions', 'encadrements', 'encadrés', 'enfants', 'enquête',
        'enquêtes', 'enrôlement', 'entimbahoakan', 'environnementale',
        'environnements', 'equilibre', 'ethique', 'etrangère', 'evènement',
        'evènements', 'expropriation', 'extractives', 'fédération',
        'financière', 'financières', 'foncière', 'fondamentaux', 'fourniture',
        'francophonie', 'gel', 'genève', 'geosciences', 'glocalisme',
        'greffes', 'guillois', 'génie', 'générale', 'généraux',
        'génétiques', 'géosciences', 'géotechnique', 'géotechniques',
        'halieutique', 'haut', 'haute', 'humanités', 'hydrocarbures',
        'hydrofluorocarbures', 'hôtes', 'identité', 'illicites',
        'immigration', 'immunité', 'importations', 'incubation',
        'indemnités', 'indianocéaniques', 'indonezia', 'industriels',
        'indépendance', 'infanterie', 'informatika', 'ingénierie',
        'ingénieries', 'innondations', 'insertion', 'inspecteur',
        'inspecteurs', 'integrité', 'interarmée', 'interarmées',
        'interrégional', 'intégration', 'intégré', 'intéressés',
        'investissement', 'judiciaire', 'juridiques', 'laser', 'lettres',
        'libertés', 'littérature', 'logement', 'logistique', 'management',
        'marché', 'maritime', 'maritimes', 'maroc', 'marrakech', 'masse',
        'master', 'mathématiques', 'matière', 'médecin', 'médecine',
        'mérite', 'métiers', 'métrologie', 'mines', 'ministères',
        'minières', 'modernisation', 'modeste', 'modélisation', 'mondial',
        'moniteurs', 'monitoring', 'montréal', 'monétaire', 'mouvement',
        'moyenne', 'multi', 'mutations', 'née', 'non', 'nouvelle',
        'nouveau', 'nucléaire', 'numérique', 'numérisation', 'nutrition',
        'obligatoire', 'observatoire', 'opérationnel', 'opérations',
        'ordinateurs', 'organique', 'organisée', 'pacte', 'palais',
        'paramédicaux', 'parquets', 'partage', 'partenariat', 'partenariats',
        'parties', 'pathogènes', 'patrimoine', 'payés', 'perfectionnement',
        'performance', 'personnel', 'personnes', 'petits', 'peut', 'phase',
        'physiques', 'pillage', 'pilotage', 'planification', 'plaine',
        'plaines', 'pollution', 'polychlorobiphényles', 'pompier',
        'population', 'portuaire', 'post', 'présidentiel', 'précédent',
        'présence', 'presidence', 'préventive', 'prioritaires',
        'problèmatiques', 'procédés', 'produits', 'professeur',
        'professionnalisation', 'programmation', 'progressive', 'projet',
        'propriété', 'prospective', 'protégées', 'pédagogie', 'pédagogique',
        'pêche', 'pôle', 'pôlitika', 'qualité', 'quartier', 'radio',
        'recherche', 'reforme', 'région', 'régional', 'régis', 'régulation',
        'réseaux', 'réserves', 'résilience', 'responsable', 'risques',
        'routière', 'routières', 'royaume', 'réduction', 'sanitaire',
        'santé', 'sciences', 'sectoriel', 'sectorielle', 'sein', 'service',
        'situation', 'sociologie', 'sociétés', 'soins', 'solidarités',
        'soutien', 'souverain', 'sportif', 'spécial', 'spécialisées',
        'stratégie', 'stratégies', 'stratégique', 'stratégiques',
        'structuration', 'stupéfiants', 'subvention', 'subventions',
        'suisse', 'suite', 'suivant', 'supérieure', 'système', 'systèmes',
        'sécurité', 'sénat', 'table', 'tale', 'taxes', 'technicité',
        'technologies', 'temple', 'tension', 'terrorisme', 'topographique',
        'touristique', 'touristiques', 'traitement', 'tranche', 'transfert',
        'transformateur', 'transnationale', 'transparence', 'travail',
        'trésor', 'tropicaux', 'truck', 'télé communications', 'télévision',
        'unité', 'universitaires', 'urbaine', 'utiles', 'utilité', 'uvres',
        'vaccinale', 'vaisseau', 'veille', 'vers', 'victimes', 'vienne',
        'villages', 'vivants', 'zone',
    }
    
    # Mots anglais courants
    ENGLISH_WORDS = {
        'the', 'and', 'for', 'are', 'with', 'this', 'that', 'from', 'have',
        'facebook', 'twitter', 'instagram', 'youtube', 'google', 'gmail',
        'world', 'youth', 'task', 'smart', 'post', 'cup', 'ball', 'basket',
    }
    
    # Acronymes/techniques à exclure
    TECHNICAL_WORDS = {
        'bp', 'tel', 'tél', 'www', 'http', 'https', 'email', 'pdf', 'com',
        'org', 'net', 'gov', 'edu',
    }
    
    # Mois (français et autres)
    MONTHS = {
        'janvier', 'février', 'fevrier', 'mars', 'avril', 'mai', 'juin',
        'juillet', 'août', 'aout', 'septembre', 'octobre', 'novembre', 'décembre',
        'december', 'janoary', 'febroary', 'martsa', 'aprily', 'mey', 'jona',
        'jolay', 'aogositra', 'septambra', 'oktobra', 'novambra', 'desambra',
    }
    
    # Terminaisons françaises typiques
    FRENCH_ENDINGS = [
        'tion', 'sion', 'ment', 'ance', 'ence', 'ique', 'able', 'ible',
        'eur', 'teur', 'rice', 'esse', 'isme', 'iste', 'ité', 'age',
        'aire', 'oire', 'ature', 'ence'
    ]
    
    # Accents français (vs malgaches)
    FRENCH_ACCENTS = ['é', 'è', 'ê', 'à', 'ç', 'ô', 'î', 'û']
    
    # Longueur minimale des mots
    MIN_WORD_LENGTH = 3


# ═══════════════════════════════════════════════════════════════════════
# CLASSE PRINCIPALE: FILTRE UNIFIÉ
# ═══════════════════════════════════════════════════════════════════════

class MalagasyVocabularyFilter:
    """Filtre unifié pour le vocabulaire malgache"""
    
    def __init__(self, config=None):
        self.config = config or FilterConfig()
        self.stats = {
            'total': 0,
            'excluded': {},
            'kept': 0
        }
    
    # ───────────────────────────────────────────────────────────────────
    # DÉTECTION DE LANGUE
    # ───────────────────────────────────────────────────────────────────
    
    def extract_words(self, text):
        """Extrait les mots d'un texte"""
        pattern = r"[a-zA-ZàâäéèêëïîôùûüÀÂÄÉÈÊËÏÎÔÙÛÜ]+(?:'[a-zA-ZàâäéèêëïîôùûüÀÂÄÉÈÊËÏÎÔÙÛÜ]+)*"
        return re.findall(pattern, text.lower())
    
    def detect_language(self, text, min_words=20):
        """Détecte si un texte est en malgache ou français"""
        words = self.extract_words(text)
        
        if len(words) < min_words:
            return 'unknown'
        
        word_set = set(words)
        word_freq = Counter(words)
        
        # Scores basés sur les marqueurs
        malagasy_score = sum(word_freq[w] for w in self.config.MALAGASY_MARKERS if w in word_freq)
        french_score = sum(word_freq[w] for w in self.config.FRENCH_WORDS if w in word_freq)
        
        total_score = malagasy_score + french_score
        
        if total_score == 0:
            return 'unknown'
        
        malagasy_pct = (malagasy_score / total_score) * 100
        
        if malagasy_pct > 60:
            return 'malagasy'
        elif malagasy_pct > 30:
            return 'mixed'
        else:
            return 'french'
    
    # ───────────────────────────────────────────────────────────────────
    # FILTRES INDIVIDUELS
    # ───────────────────────────────────────────────────────────────────
    
    def is_too_short(self, word):
        """Vérifie si le mot est trop court"""
        return len(word) < self.config.MIN_WORD_LENGTH
    
    def is_in_french_list(self, word):
        """Vérifie si le mot est dans la liste française"""
        return word.lower() in (
            self.config.FRENCH_WORDS |
            self.config.ENGLISH_WORDS |
            self.config.TECHNICAL_WORDS |
            self.config.MONTHS
        )
    
    def has_french_ending(self, word):
        """Vérifie si le mot a une terminaison française"""
        if len(word) <= 5:
            return False
        
        for ending in self.config.FRENCH_ENDINGS:
            if word.endswith(ending):
                # Exception: si le mot a aussi une terminaison malgache
                if word.endswith(('na', 'tra', 'ka', 'ny', 'tsoa', 'ina')):
                    return False
                return True
        return False
    
    def has_french_accents(self, word):
        """Vérifie si le mot a des accents français"""
        if not any(c in word for c in self.config.FRENCH_ACCENTS):
            return False
        
        # Exception: si le mot a aussi des terminaisons malgaches
        if word.endswith(('na', 'tra', 'ka', 'ny', 'tsoa', 'ina')):
            return False
        
        return True
    
    def is_likely_url_or_email(self, word):
        """Vérifie si c'est une URL ou email"""
        return '.' in word or '@' in word or '//' in word
    
    # ───────────────────────────────────────────────────────────────────
    # FILTRE PRINCIPAL
    # ───────────────────────────────────────────────────────────────────
    
    def should_exclude(self, word):
        """
        Décide si un mot doit être exclu
        Returns: (should_exclude: bool, reason: str)
        """
        # Test 1: Trop court
        if self.is_too_short(word):
            return True, "trop court"
        
        # Test 2: Dans la liste française
        if self.is_in_french_list(word):
            return True, "liste française"
        
        # Test 3: Terminaison française
        if self.has_french_ending(word):
            return True, "terminaison française"
        
        # Test 4: Accents français
        if self.has_french_accents(word):
            return True, "accents français"
        
        # Test 5: URL/Email
        if self.is_likely_url_or_email(word):
            return True, "URL/email"
        
        return False, None
    
    def filter_vocabulary(self, words):
        """
        Filtre une liste de mots
        Returns: (kept_words, excluded_words_with_reasons)
        """
        kept = []
        excluded = []
        
        for word in words:
            should_exclude, reason = self.should_exclude(word)
            
            if should_exclude:
                excluded.append((word, reason))
                # Stats
                if reason not in self.stats['excluded']:
                    self.stats['excluded'][reason] = 0
                self.stats['excluded'][reason] += 1
            else:
                kept.append(word)
                self.stats['kept'] += 1
        
        self.stats['total'] = len(words)
        return kept, excluded
    
    # ───────────────────────────────────────────────────────────────────
    # UTILITAIRES
    # ───────────────────────────────────────────────────────────────────
    
    def print_stats(self):
        """Affiche les statistiques de filtrage"""
        print("\n" + "=" * 60)
        print("📊 STATISTIQUES DE FILTRAGE")
        print("=" * 60)
        print(f"  Total mots       : {self.stats['total']:,}")
        print(f"  Mots conservés   : {self.stats['kept']:,}")
        print(f"  Mots exclus      : {self.stats['total'] - self.stats['kept']:,}")
        
        if self.stats['total'] > 0:
            pct = ((self.stats['total'] - self.stats['kept']) / self.stats['total']) * 100
            print(f"  Taux d'exclusion : {pct:.1f}%")
        
        if self.stats['excluded']:
            print(f"\n📋 Raisons d'exclusion :")
            for reason, count in sorted(self.stats['excluded'].items(), key=lambda x: x[1], reverse=True):
                print(f"  - {reason:25s} : {count:,} mots")


# ═══════════════════════════════════════════════════════════════════════
# FONCTIONS PRINCIPALES
# ═══════════════════════════════════════════════════════════════════════

def filter_file(input_file, output_file, backup=True):
    """Filtre un fichier de vocabulaire"""
    
    print("=" * 60)
    print("🧹 FILTRAGE DU VOCABULAIRE MALGACHE")
    print("=" * 60)
    
    # Backup
    if backup:
        backup_file = str(input_file).replace('.txt', '_backup.txt')
        copy2(input_file, backup_file)
        print(f"📋 Backup créé : {Path(backup_file).name}\n")
    
    # Charger
    with open(input_file, 'r', encoding='utf-8') as f:
        words = [line.strip() for line in f if line.strip()]
    
    print(f"✅ Chargé : {len(words):,} mots\n")
    
    # Filtrer
    filter_obj = MalagasyVocabularyFilter()
    kept, excluded = filter_obj.filter_vocabulary(words)
    
    # Trier
    kept.sort()
    
    # Sauvegarder
    with open(output_file, 'w', encoding='utf-8') as f:
        for word in kept:
            f.write(word + '\n')
    
    # Stats
    filter_obj.print_stats()
    
    # Exemples
    print(f"\n📝 Exemples de mots EXCLUS (10 premiers) :")
    for i, (word, reason) in enumerate(excluded[:10], 1):
        print(f"  {i:2d}. {word:30s} ({reason})")
    
    print(f"\n✅ Exemples de mots CONSERVÉS (10 premiers) :")
    for i, word in enumerate(kept[:10], 1):
        print(f"  {i:2d}. {word}")
    
    print(f"\n💾 Fichier filtré : {Path(output_file).name}")
    print("=" * 60)
    
    return len(kept), len(excluded)


# ═══════════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════

def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Filtre unifié pour le vocabulaire malgache',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python filtre_vocabulaire.py --input mots.txt --output mots_filtres.txt
  python filtre_vocabulaire.py --input mots.txt --no-backup
        """
    )
    
    parser.add_argument('--input', default='nouveaux_vocabulaires_malgaches_complementaire_scrapping.txt',
                       help='Fichier d\'entrée')
    parser.add_argument('--output', default=None,
                       help='Fichier de sortie (défaut: écrase l\'entrée)')
    parser.add_argument('--no-backup', action='store_true',
                       help='Ne pas créer de backup')
    
    args = parser.parse_args()
    
    input_file = Path(args.input)
    output_file = Path(args.output) if args.output else input_file
    
    if not input_file.exists():
        print(f"❌ Fichier introuvable : {input_file}")
        return 1
    
    kept, excluded = filter_file(input_file, output_file, backup=not args.no_backup)
    
    print(f"\n✅ Terminé ! {kept:,} mots conservés, {excluded:,} mots exclus")
    return 0


if __name__ == "__main__":
    exit(main())
