import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import re
import pytz

# --- CONFIGURATION ---
BASE_URL = "https://planning.iae-paris.com/cours?formation=MAE+25.208+FIS&paginate=pages&view=list&filter=all&start_date=2025-09-01"
PARIS_TZ = pytz.timezone('Europe/Paris')

# --- BASE DE DONNÉES PÉDAGOGIQUE ---
UE_DB = {
    "1": {
        "nom": "Environnement Économique",
        "prof": "Stéphane Saussier",
        "keywords": ["ECONOM", "CROISSANCE", "PIB", "CARTEL", "SALARIALE", "FRONTIERES"],
        "sessions": {
            1: "Amphi Ouverture - PIB & Croissance",
            2: "Relation salariale & incitation",
            3: "L'entreprise et la production",
            4: "Les frontières de l'entreprise",
            5: "Rôle de l'Etat & gestion publique",
            6: "Les cartels",
            7: "Environnement & nouveaux modèles",
            8: "Amphi de Fermeture"
        },
        "exercices": {}
    },
    "2": {
        "nom": "Droit des affaires",
        "prof": "Marianne Dournaux",
        "keywords": ["DROIT", "JURIDIQUE", "CONTRAT", "RESPONSABILIT", "SOCIETE", "CONCURRENCE"],
        "sessions": {
            1: "CM En ligne 1 - Intro matière",
            2: "Intro générale au droit",
            3: "Droit des contrats (Formation)",
            4: "Droit des contrats (Effets)",
            5: "Droit de la responsabilité civile",
            6: "CM En ligne 2 - Éléments de cours",
            7: "Droit des sociétés (Formation)",
            8: "Droit des sociétés (Cessions)",
            9: "Droit des sociétés (Crises)",
            10: "Responsabilité des dirigeants",
            11: "Droit des biens",
            12: "Droit de la concurrence",
            13: "Droit du travail",
            14: "Entreprises en difficulté"
        },
        "exercices": {}
    },
    "3": {
        "nom": "Information comptable",
        "prof": "Stéphane Bellanger",
        "keywords": ["COMPTA", "FINANCIER", "ACTIF", "BILAN", "TRESORERIE", "RESULTAT"],
        "sessions": {
            1: "Amphi 1 - Contexte normatif",
            2: "TD1 - Modèle comptable & états financiers",
            3: "TD2 - Actifs non courants",
            4: "TD3 - Moyens de financement",
            5: "TD4 - Actifs courants",
            6: "TD5 - Résultat activités ordinaires",
            7: "Amphi 2 - Actifs immatériels & Goodwill",
            8: "TD6 - Obligations non financières",
            9: "TD7 - Flux de trésorerie",
            10: "TD8 - Synthèse & Révision"
        },
        "exercices": {
            1: "Cas Electrix",
            2: "Cas Speedway",
            3: "Cas Autoloc",
            4: "Cas Alizeo",
            5: "Cas Fabric",
            6: "Cas Serena",
            7: "Cas Pietra",
            8: "Cas Belhotel",
            9: "Cas Schemler",
            10: "Examen 2021 (extraits)"
        }
    },
    "4": {
        "nom": "Gestion des RH",
        "prof": "Florent Noël",
        "keywords": ["RESSOURCES HUMAINES", "GRH", "SALARIE", "EMPLOI", "COMPETENCE"],
        "sessions": {
            1: "Amphi Intro - Intro GRH",
            2: "Marges de manœuvre fonction RH",
            3: "Organisation du travail",
            4: "Mobilisation des salariés",
            5: "GPEC",
            6: "Amphi de Clôture"
        },
        "exercices": {
            2: "Voir EPI",
            3: "Voir EPI",
            4: "Voir EPI",
            5: "Voir EPI"
        }
    },
    "5": {
        "nom": "Marketing",
        "prof": "J-L Brunstein & O. Sabri",
        "keywords": ["MARKETING", "MKG", "VENTE", "DISTRIBUTION", "PRIX", "MARCHE", "CONSOMMATEUR", "PRODUIT", "COMMUNICATION"],
        "sessions": {
            1: "Amphi Intro - Marketing & défis",
            2: "Démarche mkg & comportement conso",
            3: "Connaissance marché & études quanti",
            4: "Stratégie marketing",
            5: "Politique produit",
            6: "Politique prix & valeur",
            7: "Vente & distribution",
            8: "Communication & digital",
            9: "Présentation de projet",
            10: "Amphi Conclusion - Performance mkg"
        },
        "exercices": {
            2: "Cas Bague de fiançailles",
            3: "Cas PizzaWave",
            4: "Cas BMW",
            5: "Cas Dyson",
            6: "Cas Fadéo",
            7: "Cas Literie Germain",
            8: "Cas Inoui"
        }
    },
    "6": {
        "nom": "Projets, Innovation & Supply Chain",
        "prof": "Christine Triomphe",
        "keywords": ["SUPPLY CHAIN", "SCM", "INNOVATION", "PROJET", "LOGISTIQUE", "AGILE", "DESIGN"],
        "sessions": {
            1: "Cours 1 - Intro SCM & Projets",
            2: "SCM : Choix stratégiques",
            3: "Coordination SC étendue",
            4: "Projets conception nouveaux produits",
            5: "Outils gestion de projet (Business Case)",
            6: "Cours 2 - Management Innovation",
            7: "Innovation frugale",
            8: "Méthodes Agiles",
            9: "Design Thinking",
            10: "Open Innovation"
        },
        "exercices": {
            2: "Cas McDonald's",
            3: "Cas Amazon",
            4: "Cas TechnoCentre",
            5: "Cas Videogames",
            7: "Cas Kwid",
            8: "Cas Pearson",
            9: "Cas IDEO (Vidéo)",
            10: "Cas HyperLoop"
        }
    },
    "7": {
        "nom": "Finance d'entreprise",
        "prof": "Jérôme Caby",
        "keywords": ["FINANCE", "RENTABILITE", "SOLVABILITE", "SIG", "FLUX", "CONSOLID"],
        "sessions": {
            1: "Amphi 1 - Intro Analyse fi",
            2: "SIG & Rentabilité",
            3: "Bilan fonctionnel & Solvabilité",
            4: "Tableaux de flux (1/2)",
            5: "Tableaux de flux (2/2)",
            6: "Synthèse: Rentabilité/Solvabilité",
            7: "Cas synthèse Anglosaxon",
            8: "Plan de financement",
            9: "Diagnostic comptes consolidés",
            10: "Amphi 2 - Approfondissement/Synthèse"
        },
        "exercices": {
            2: "Cas PRAG",
            3: "Cas CAMBO",
            4: "Cas TUSI",
            5: "Cas TUSI",
            6: "Cas TURCO",
            7: "Cas Anandam",
            8: "Cas SMIN",
            9: "Cas Plastic Omnium"
        }
    },
    "8": {
        "nom": "Management des SI",
        "prof": "P. Eynaud & J-L Richet",
        "keywords": ["SYSTEME D'INFORMATION", " SI ", "GOUVERNANCE", "URBANISATION", "ALIGNEMENT"],
        "sessions": {
            1: "Place des SI dans organisations",
            2: "Gouvernance",
            3: "Urbanisation (1/2)",
            4: "Urbanisation (2/2)",
            5: "Alignement (1/2)",
            6: "Alignement (2/2)",
            7: "Cas synthèse Gouvernance",
            8: "Cas synthèse global"
        },
        "exercices": {
            1: "Cas n°1 introductif",
            2: "Cas n°2 gouvernance",
            3: "Cas n°3 urbanisation",
            4: "Cas n°3 urbanisation",
            5: "Cas n°4 alignement",
            6: "Cas n°4 alignement",
            7: "Cas n°5 synthèse",
            8: "Cas n°6 synthèse"
        }
    },
    "9": {
        "nom": "Contrôle de gestion",
        "prof": "Olivier de La Villarmois",
        "keywords": ["CONTROLE DE GESTION", "COUT", "BUDGET", "TABLEAUX DE BORD", "YIELD"],
        "sessions": {
            1: "Amphi 1 - Intro & Coûts",
            2: "Système calcul de coût",
            3: "Modèle Coût / Volume / Profit",
            4: "Synthèse coût complet",
            5: "Prix de cession interne",
            6: "Démarche budgétaire",
            7: "Analyse des écarts",
            8: "Yield Management",
            9: "Tableaux de bord & RSE",
            10: "Amphi 2 - Gestion stratégique coûts"
        },
        "exercices": {
            1: "Cas Lucky Duck",
            2: "Cas LM Hopital",
            3: "Cas Amazon & Auto Collection",
            4: "Cas Pelino 2",
            5: "Cas Data Meca",
            6: "Cas Mon premier BP",
            7: "Cas Quard-heure",
            8: "Cas Classotel",
            9: "Cas Business Model Canvas",
            10: "Cas La Cantina"
        }
    },
    "10": {
        "nom": "Organisations & Comportements",
        "prof": "Nathalie Raulet-Croset",
        "keywords": ["COMPORTEMENT", "ORGANISATION", "LEADERSHIP", "CONFLIT", "TELETRAVAIL", "HIERARCHIE"],
        "sessions": {
            1: "Amphi - Cadre analyse multi-niveaux",
            2: "Intro analyse comportements",
            3: "Org formelle vs informelle",
            4: "Changement organisationnel",
            5: "Autorité, influence, leadership",
            6: "Coopération",
            7: "Conflit & Négociation",
            8: "Télétravail & distance",
            9: "Entreprise sans hiérarchie ?",
            10: "Amphi Synthèse"
        },
        "exercices": {
            2: "Cas Trecca",
            3: "Cas PDT",
            4: "Cas ZYX",
            5: "Cas Assurance Plus",
            6: "Cas Le retour du héros",
            7: "Cas La Patrouille de France",
            8: "Cas Business Unit",
            9: "Cas Ingeserv",
            10: "Cas Chronoflex"
        }
    },
    "11": {
        "nom": "Stratégie de l'entreprise",
        "prof": "D. Chabaud & P. Garaudel",
        "keywords": ["STRATEGIE", "CONCURRENTIEL", "BUSINESS MODEL", "CORPORATE", "DIVERSIFICATION"],
        "sessions": {
            1: "Cours Introductif (Amphi)",
            2: "Cas d'examen précédent",
            3: "Analyse concurrentielle",
            4: "Stratégie Business & Inter",
            5: "Positionnement & Diversification",
            6: "Business Models",
            7: "Stratégie Corporate & Chaine valeur",
            8: "Synthèse",
            9: "Cours Conclusion (Amphi)"
        },
        "exercices": {
            2: "Cas Total",
            3: "Cas Transport Aérien",
            4: "Cas Netflix",
            5: "Cas Schindler",
            6: "Cas Blablacar",
            7: "Cas Engie",
            8: "Cas Danone"
        }
    },
    "12": {
        "nom": "Management International",
        "prof": "Pierre-Yves Lagroue",
        "keywords": ["INTERNATIONAL", "MONDE", "ETRANGER", "INTERCULTUREL", "ETHIQUE"],
        "sessions": {
            1: "Facteurs de l'internationalisation",
            2: "Modes d'entrée (1/2)",
            3: "Modes d'entrée (2/2)",
            4: "Éthique & RSE",
            5: "Management Interculturel",
            6: "Stratégies internationales",
            7: "Organisation & Management (1/2)",
            8: "Organisation & Management (2/2)"
        },
        "exercices": {}
    }
}

MOIS_FR = {
    'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
    'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
}

def clean_text(text):
    """Nettoie le texte (espaces insécables, etc)"""
    return text.replace('\xa0', ' ').strip()

def parse_french_date(date_str):
    parts = clean_text(date_str).lower().split()
    try:
        day = int(parts[1])
        month = MOIS_FR[parts[2]]
        year = int(parts[3])
        return year, month, day
    except Exception:
        return None

def detect_ue_from_text(text):
    text_upper = clean_text(text).upper()
    for ue_id, data in UE_DB.items():
        if clean_text(data['nom']).upper() in text_upper:
            return ue_id
        for kw in data.get('keywords', []):
            if kw in text_upper:
                return ue_id
    return None

def main():
    cal = Calendar()
    session = requests.Session()
    
    active_ue_on_slot = {} 
    ue_progress = {ue_id: 0 for ue_id in UE_DB.keys()}

    print("Démarrage du scraping (Mode 'Catch-All')...")

    # On scanne large
    for page in range(1, 25):
        url = f"{BASE_URL}&page={page}"
        print(f"Traitement page {page}...")
        
        try:
            response = session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            rows = soup.select('table.table tbody tr')
            if not rows: break

            current_date_tuple = None
            
            for row in rows:
                classes = row.get('class', [])
                
                # --- DATE ---
                if 'bg-slate-50' in classes:
                    date_div = row.find('div', class_='text-xl')
                    if date_div:
                        current_date_tuple = parse_french_date(date_div.get_text())
                
                # --- LIGNE DE COURS ---
                elif 'hover' in classes and current_date_tuple:
                    cols = row.find_all('td')
                    if len(cols) < 7: continue
                    
                    # 1. HORAIRES
                    time_text = clean_text(cols[0].get_text(separator=" "))
                    times = re.findall(r'\d{2}:\d{2}', time_text)
                    if len(times) < 2: continue
                    
                    start_hm = times[0].split(':')
                    end_hm = times[1].split(':')
                    slot_key = f"{start_hm[0]}:{start_hm[1]}"

                    # 2. INFO BRUTES
                    raw_ue_text = clean_text(cols[4].get_text())
                    subject_raw = clean_text(cols[2].get_text())
                    
                    ue_id = None
                    
                    # A. Detection Prioritaire
                    match = re.search(r'#(\d+)', raw_ue_text)
                    if match:
                        ue_id = match.group(1)
                        if any(x in subject_raw.upper() for x in ["OUVERTURE", "AMPHI 1", "INTRO"]):
                             ue_progress[ue_id] = 0
                        active_ue_on_slot[slot_key] = ue_id

                    # B. Detection Mots-clés
                    if not ue_id:
                        ue_id = detect_ue_from_text(subject_raw)
                        if ue_id:
                            active_ue_on_slot[slot_key] = ue_id

                    # C. Mémoire
                    if not ue_id:
                        ue_id = active_ue_on_slot.get(slot_key)

                    # 3. PRÉPARATION DE L'ÉVÉNEMENT
                    # Si UE trouvée
                    if ue_id:
                        ue_progress[ue_id] += 1
                        current_session_num = ue_progress[ue_id]
                        ue_data = UE_DB.get(ue_id, {})
                        max_sessions = len(ue_data.get("sessions", {}))
                        
                        # Session normale vs supplémentaire
                        if current_session_num <= max_sessions:
                            session_theme = ue_data.get("sessions", {}).get(current_session_num, subject_raw)
                            session_exercice = ue_data.get("exercices", {}).get(current_session_num, "")
                        else:
                            session_theme = f"Séance Supplémentaire : {subject_raw}"
                            session_exercice = ""

                        prof_name = ue_data.get("prof", "")
                        title = f"[UE {ue_id}] {ue_data.get('nom')}"
                        desc_header = f"Progression: Séance {current_session_num} sur {max_sessions}"

                    # Si UE NON trouvée (Mode Catch-All)
                    else:
                        title = f"[?] {subject_raw}"
                        prof_name = "Non identifié"
                        session_theme = "UE non reconnue par le script"
                        session_exercice = ""
                        desc_header = "⚠️ Ce cours n'a pas été reconnu automatiquement."

                    # 4. SALLE & EXAMENS
                    room_tag = cols[6].find('span', class_='badge')
                    room = clean_text(room_tag.get_text()) if room_tag else "Inconnu"
                    address = room
                    
                    is_exam = "EXAMEN" in subject_raw.upper() or "ARCUEIL" in room.upper()
                    if is_exam:
                        title = f"📝 EXAMEN - {title.replace('[?]', '[EXAMEN]')}"
                        session_theme = "Examen Final"
                        if "ARCUEIL" in room.upper():
                            address = "Maison des Examens, 7 Rue Ernest Renan, 94110 Arcueil"
                            room = "Maison des Examens"
                    elif "LIGNE" in room.upper():
                        room = "🖥️ En ligne"

                    # 5. CONSTRUCTION
                    y, m, d = current_date_tuple
                    dt_start = PARIS_TZ.localize(datetime(y, m, d, int(start_hm[0]), int(start_hm[1])))
                    dt_end = PARIS_TZ.localize(datetime(y, m, d, int(end_hm[0]), int(end_hm[1])))

                    e = Event()
                    e.name = title
                    e.begin = dt_start
                    e.end = dt_end
                    e.location = address
                    
                    desc = [
                        f"Thème: {session_theme}",
                    ]
                    if session_exercice:
                        desc.append(f"📚 À préparer: {session_exercice}")
                    
                    desc.append(f"👨‍🏫 Intervenant: {prof_name}")
                    desc.append(f"📍 Salle: {room}")
                    desc.append(f"ℹ️ Titre brut: {subject_raw}")
                    desc.append(desc_header)
                    
                    e.description = "\n".join(desc)
                    cal.events.add(e)
                    print(f" + Ajouté : {title} ({dt_start})")

        except Exception as e:
            print(f"Erreur page {page}: {e}")

    with open('planning.ics', 'w', encoding='utf-8') as f:
        f.writelines(cal.serialize_iter())
    print("Calendrier généré (inclus non-identifiés) !")

if __name__ == "__main__":
    main()
