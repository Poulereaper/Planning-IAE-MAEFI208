import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime, timedelta
import re
import pytz

# --- CONFIGURATION ---
BASE_URL = "https://planning.iae-paris.com/cours?formation=MAE+25.208+FIS&paginate=pages&view=list&filter=all&start_date=2025-09-01"
PARIS_TZ = pytz.timezone('Europe/Paris')

# --- LOGIQUE DE RELAIS ---
UE_RELAY = {
    "1": "6", "3": "7", "7": "5", "6": "2", "2": "4"
}

# --- BASE DE DONNÉES PÉDAGOGIQUE ---
UE_DB = {
    "1": {
        "nom": "Environnement Économique",
        "prof": "Stéphane Saussier",
        "keywords": ["ECONOMI", "CROISSANCE", "PIB", "CARTEL", "SALARIALE"],
        "sessions": {
            1: "Amphi Ouverture - PIB & Croissance", 2: "Relation salariale & incitation",
            3: "L'entreprise et la production", 4: "Les frontières de l'entreprise",
            5: "Rôle de l'Etat & gestion publique", 6: "Les cartels",
            7: "Environnement & nouveaux modèles", 8: "Amphi de Fermeture"
        },
        "exercices": {}
    },
    "2": {
        "nom": "Droit des affaires",
        "prof": "Marianne Dournaux",
        "keywords": ["DROIT", "JURIDIQUE", "CONTRAT", "RESPONSABILIT", "SOCIETE", "CONCURRENCE"],
        "sessions": {
            1: "CM En ligne 1 - Intro matière", 2: "Intro générale au droit",
            3: "Droit des contrats (Formation)", 4: "Droit des contrats (Effets)",
            5: "Droit de la responsabilité civile", 6: "CM En ligne 2 - Éléments de cours",
            7: "Droit des sociétés (Formation)", 8: "Droit des sociétés (Cessions)",
            9: "Droit des sociétés (Crises)", 10: "Responsabilité des dirigeants",
            11: "Droit des biens", 12: "Droit de la concurrence",
            13: "Droit du travail", 14: "Entreprises en difficulté"
        },
        "exercices": {}
    },
    "3": {
        "nom": "Information comptable",
        "prof": "Stéphane Bellanger",
        "keywords": ["COMPTA", "FINANCIER", "ACTIF", "BILAN", "TRESORERIE", "RESULTAT"],
        "sessions": {
            1: "Amphi 1 - Contexte normatif", 2: "TD1 - Modèle comptable & états financiers",
            3: "TD2 - Actifs non courants", 4: "TD3 - Moyens de financement",
            5: "TD4 - Actifs courants", 6: "TD5 - Résultat activités ordinaires",
            7: "Amphi 2 - Actifs immatériels & Goodwill", 8: "TD6 - Obligations non financières",
            9: "TD7 - Flux de trésorerie", 10: "TD8 - Synthèse & Révision"
        },
        "exercices": {
            1: "Cas Electrix", 2: "Cas Speedway", 3: "Cas Autoloc", 4: "Cas Alizeo",
            5: "Cas Fabric", 6: "Cas Serena", 7: "Cas Pietra", 8: "Cas Belhotel",
            9: "Cas Schemler", 10: "Examen 2021 (extraits)"
        }
    },
    "4": {
        "nom": "Gestion des RH",
        "prof": "Florent Noël",
        "keywords": ["RESSOURCES HUMAINES", "GRH", "SALARIE", "EMPLOI", "COMPETENCE"],
        "sessions": {
            1: "Amphi Intro - Intro GRH", 2: "Marges de manœuvre fonction RH",
            3: "Organisation du travail", 4: "Mobilisation des salariés",
            5: "GPEC", 6: "Amphi de Clôture"
        },
        "exercices": {2: "Voir EPI", 3: "Voir EPI", 4: "Voir EPI", 5: "Voir EPI"}
    },
    "5": {
        "nom": "Marketing",
        "prof": "J-L Brunstein & O. Sabri",
        "keywords": ["MARKETING", "MKG", "VENTE", "DISTRIBUTION", "PRIX", "MARCHE", "CONSOMMATEUR"],
        "sessions": {
            1: "Amphi Intro - Marketing & défis", 2: "Démarche mkg & comportement conso",
            3: "Connaissance marché & études quanti", 4: "Stratégie marketing",
            5: "Politique produit", 6: "Politique prix & valeur",
            7: "Vente & distribution", 8: "Communication & digital",
            9: "Présentation de projet", 10: "Amphi Conclusion - Performance mkg"
        },
        "exercices": {
            2: "Cas Bague de fiançailles", 3: "Cas PizzaWave", 4: "Cas BMW",
            5: "Cas Dyson", 6: "Cas Fadéo", 7: "Cas Literie Germain", 8: "Cas Inoui"
        }
    },
    "6": {
        "nom": "Projets, Innovation & Supply Chain",
        "prof": "Christine Triomphe",
        "keywords": ["SUPPLY CHAIN", "SCM", "INNOVATION", "PROJET", "LOGISTIQUE", "AGILE"],
        "sessions": {
            1: "Cours 1 - Intro SCM & Projets", 2: "SCM : Choix stratégiques",
            3: "Coordination SC étendue", 4: "Projets conception nouveaux produits",
            5: "Outils gestion de projet (Business Case)", 6: "Cours 2 - Management Innovation",
            7: "Innovation frugale", 8: "Méthodes Agiles",
            9: "Design Thinking", 10: "Open Innovation"
        },
        "exercices": {
            2: "Cas McDonald's", 3: "Cas Amazon", 4: "Cas TechnoCentre",
            5: "Cas Videogames", 7: "Cas Kwid", 8: "Cas Pearson",
            9: "Cas IDEO (Vidéo)", 10: "Cas HyperLoop"
        }
    },
    "7": {
        "nom": "Finance d'entreprise",
        "prof": "Jérôme Caby",
        "keywords": ["FINANCE", "RENTABILITE", "SOLVABILITE", "SIG", "FLUX", "CONSOLID"],
        "sessions": {
            1: "Amphi 1 - Intro Analyse fi", 2: "SIG & Rentabilité",
            3: "Bilan fonctionnel & Solvabilité", 4: "Tableaux de flux (1/2)",
            5: "Tableaux de flux (2/2)", 6: "Synthèse: Rentabilité/Solvabilité",
            7: "Cas synthèse Anglosaxon", 8: "Plan de financement",
            9: "Diagnostic comptes consolidés", 10: "Amphi 2 - Approfondissement/Synthèse"
        },
        "exercices": {
            2: "Cas PRAG", 3: "Cas CAMBO", 4: "Cas TUSI", 5: "Cas TUSI",
            6: "Cas TURCO", 7: "Cas Anandam", 8: "Cas SMIN", 9: "Cas Plastic Omnium"
        }
    },
    # UE 8, 9, 10, 11, 12... (A compléter si nécessaire)
    "12": {
        "nom": "Management International",
        "prof": "Pierre-Yves Lagroue",
        "keywords": ["INTERNATIONAL", "MONDE", "ETRANGER"],
        "sessions": {1: "Facteurs", 2: "Modes Entrée 1", 3: "Modes Entrée 2"},
        "exercices": {}
    }
}

MOIS_FR = {
    'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
    'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
}

def clean_text(text):
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

    print("Démarrage du scraping (Mode Relais & Split 4h)...")

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
                if 'bg-slate-50' in classes:
                    date_div = row.find('div', class_='text-xl')
                    if date_div:
                        current_date_tuple = parse_french_date(date_div.get_text())
                
                elif 'hover' in classes and current_date_tuple:
                    cols = row.find_all('td')
                    if len(cols) < 7: continue
                    
                    # 1. ANALYSE HORAIRE & DURÉE
                    time_text = clean_text(cols[0].get_text(separator=" "))
                    times = re.findall(r'\d{2}:\d{2}', time_text)
                    if len(times) < 2: continue
                    
                    start_hm = times[0].split(':')
                    end_hm = times[1].split(':')
                    
                    h_start = int(start_hm[0])
                    m_start = int(start_hm[1])
                    h_end = int(end_hm[0])
                    m_end = int(end_hm[1])
                    
                    # Durée en minutes
                    duration_minutes = (h_end * 60 + m_end) - (h_start * 60 + m_start)
                    
                    # Est-ce un bloc de 4h qui cache 2 cours ?
                    is_double_session = (duration_minutes >= 230) # >= 3h50
                    
                    # Liste des sous-créneaux à traiter (1 ou 2)
                    sub_slots = []
                    
                    if is_double_session:
                        # On coupe en deux : Partie 1 (Start -> Start+2h), Partie 2 (Start+2h -> End)
                        mid_h = h_start + 2
                        sub_slots.append( ( (h_start, m_start), (mid_h, m_start) ) )
                        sub_slots.append( ( (mid_h, m_start), (h_end, m_end) ) )
                        print("   -> Bloc de 4h détecté : Division en 2 séances !")
                    else:
                        sub_slots.append( ( (h_start, m_start), (h_end, m_end) ) )

                    # BOUCLE SUR LES SOUS-CRÉNEAUX (1 ou 2 fois)
                    for (s_h, s_m), (e_h, e_m) in sub_slots:
                        slot_key = f"{s_h:02d}:{s_m:02d}"
                        
                        # 2. IDENTIFICATION
                        raw_ue_text = clean_text(cols[4].get_text())
                        subject_raw = clean_text(cols[2].get_text())
                        ue_id = None
                        
                        match = re.search(r'#(\d+)', raw_ue_text)
                        if match:
                            ue_id = match.group(1)
                            if any(x in subject_raw.upper() for x in ["OUVERTURE", "AMPHI 1", "INTRO"]):
                                ue_progress[ue_id] = 0
                            active_ue_on_slot[slot_key] = ue_id

                        if not ue_id: ue_id = detect_ue_from_text(subject_raw)
                        if ue_id: active_ue_on_slot[slot_key] = ue_id

                        if not ue_id:
                            mem_id = active_ue_on_slot.get(slot_key)
                            if mem_id:
                                max_sessions_mem = len(UE_DB[mem_id]["sessions"])
                                if ue_progress[mem_id] >= max_sessions_mem:
                                    next_ue = UE_RELAY.get(mem_id)
                                    if next_ue: ue_id = next_ue
                                    active_ue_on_slot[slot_key] = ue_id
                                else:
                                    ue_id = mem_id

                        if not ue_id: continue

                        # 3. VERIF FINALE & PROGRESSION
                        ue_data = UE_DB.get(ue_id, {})
                        max_sessions = len(ue_data.get("sessions", {}))
                        
                        if ue_progress[ue_id] >= max_sessions: continue

                        ue_progress[ue_id] += 1
                        current_session_num = ue_progress[ue_id]
                        
                        session_theme = ue_data.get("sessions", {}).get(current_session_num, subject_raw)
                        session_exercice = ue_data.get("exercices", {}).get(current_session_num, "")
                        prof_name = ue_data.get("prof", "")
                        title = f"[UE {ue_id}] {ue_data.get('nom')}"
                        
                        # 4. INFO SALLE & TYPE
                        room_tag = cols[6].find('span', class_='badge')
                        room = clean_text(room_tag.get_text()) if room_tag else "Inconnu"
                        address = room
                        type_cours = "TD" # Par défaut

                        # Logique Amphi / Distanciel
                        current_duration = (e_h*60 + e_m) - (s_h*60 + s_m)
                        if current_duration != 120 and not is_double_session: # Si pas 2h pile
                            type_cours = "Amphi / Conférence"
                        
                        if "AMPHI" in subject_raw.upper() or "OUVERTURE" in subject_raw.upper():
                            type_cours = "Amphi"

                        if "LIGNE" in room.upper():
                            room = "🖥️ En ligne"
                            type_cours += " (Distanciel)"
                        
                        is_exam = "EXAMEN" in subject_raw.upper() or "ARCUEIL" in room.upper()
                        if is_exam:
                            title = f"📝 EXAMEN - {title}"
                            session_theme = "Examen Final"
                            type_cours = "Examen"
                            if "ARCUEIL" in room.upper():
                                address = "Maison des Examens, 7 Rue Ernest Renan, 94110 Arcueil"
                                room = "Maison des Examens"

                        # 5. CONSTRUCTION EVENT
                        y, m, d = current_date_tuple
                        dt_start = PARIS_TZ.localize(datetime(y, m, d, s_h, s_m))
                        dt_end = PARIS_TZ.localize(datetime(y, m, d, e_h, e_m))

                        e = Event()
                        e.name = title
                        e.begin = dt_start
                        e.end = dt_end
                        e.location = address
                        
                        desc = [f"Thème: {session_theme}"]
                        if session_exercice: desc.append(f"📚 À préparer: {session_exercice}")
                        desc.append(f"👨‍🏫 Intervenant: {prof_name}")
                        desc.append(f"📍 Salle: {room}")
                        desc.append(f"📌 Type: {type_cours}")
                        desc.append(f"Progression: Séance {current_session_num} sur {max_sessions}")
                        
                        e.description = "\n".join(desc)
                        cal.events.add(e)
                        print(f" + Ajouté : {title} ({current_session_num}/{max_sessions}) [{type_cours}]")

        except Exception as e:
            print(f"Erreur page {page}: {e}")

    with open('planning.ics', 'w', encoding='utf-8') as f:
        f.writelines(cal.serialize_iter())
    print("Calendrier généré !")

if __name__ == "__main__":
    main()
