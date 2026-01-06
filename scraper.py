import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import re
import pytz

# --- CONFIGURATION ---
BASE_URL = "https://planning.iae-paris.com/cours?formation=MAE+25.208+FIS&paginate=pages&view=list&filter=all&start_date=2025-09-01"
PARIS_TZ = pytz.timezone('Europe/Paris')

# --- BASE DE DONNÉES PÉDAGOGIQUE (Extraite du PDF) ---
# Format: "UE_ID": { "nom", "prof", "sessions": { 1: "Theme", 2: "Theme"... } }
# Les clés de sessions sont séquentielles (1, 2, 3...) suivant l'ordre chronologique
UE_DB = {
    "1": {
        "nom": "Environnement Économique",
        "prof": "Stéphane Saussier",
        "sessions": {
            1: "Amphi Ouverture - PIB & Croissance",
            2: "Relation salariale & incitation",
            3: "L'entreprise et la production",
            4: "Les frontières de l'entreprise",
            5: "Rôle de l'Etat & gestion publique",
            6: "Les cartels",
            7: "Environnement & nouveaux modèles",
            8: "Amphi de Fermeture"
        }
    },
    "2": {
        "nom": "Droit des affaires",
        "prof": "Marianne Dournaux",
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
        }
    },
    "3": {
        "nom": "Information comptable",
        "prof": "Stéphane Bellanger",
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
        }
    },
    "4": {
        "nom": "Gestion des RH",
        "prof": "Florent Noël",
        "sessions": {
            1: "Amphi Intro - Intro GRH",
            2: "Marges de manœuvre fonction RH",
            3: "Organisation du travail",
            4: "Mobilisation des salariés",
            5: "GPEC",
            6: "Amphi de Clôture"
        }
    },
    "5": {
        "nom": "Marketing",
        "prof": "J-L Brunstein & O. Sabri",
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
        }
    },
    "6": {
        "nom": "Projets, Innovation & Supply Chain",
        "prof": "Christine Triomphe",
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
        }
    },
    "7": {
        "nom": "Finance d'entreprise",
        "prof": "Jérôme Caby",
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
        }
    },
    "8": {
        "nom": "Management des SI",
        "prof": "P. Eynaud & J-L Richet",
        "sessions": {
            1: "Place des SI dans organisations",
            2: "Gouvernance",
            3: "Urbanisation (1/2)",
            4: "Urbanisation (2/2)",
            5: "Alignement (1/2)",
            6: "Alignement (2/2)",
            7: "Cas synthèse Gouvernance",
            8: "Cas synthèse global"
        }
    },
    "9": {
        "nom": "Contrôle de gestion",
        "prof": "Olivier de La Villarmois",
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
        }
    },
    "10": {
        "nom": "Organisations & Comportements",
        "prof": "Nathalie Raulet-Croset",
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
        }
    },
    "11": {
        "nom": "Stratégie de l'entreprise",
        "prof": "D. Chabaud & P. Garaudel",
        "sessions": {
            1: "Cours Introductif (Amphi)", # Déduit de la méthode péda
            2: "Cas d'examen précédent",
            3: "Analyse concurrentielle",
            4: "Stratégie Business & Inter",
            5: "Positionnement & Diversification",
            6: "Business Models",
            7: "Stratégie Corporate & Chaine valeur",
            8: "Synthèse",
            9: "Cours Conclusion (Amphi)"
        }
    },
    "12": {
        "nom": "Management International",
        "prof": "Pierre-Yves Lagroue",
        "sessions": {
            1: "Facteurs de l'internationalisation",
            2: "Modes d'entrée (1/2)",
            3: "Modes d'entrée (2/2)",
            4: "Éthique & RSE",
            5: "Management Interculturel",
            6: "Stratégies internationales",
            7: "Organisation & Management (1/2)",
            8: "Organisation & Management (2/2)"
        }
    }
}

MOIS_FR = {
    'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
    'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
}

def parse_french_date(date_str):
    parts = date_str.lower().split()
    try:
        day = int(parts[1])
        month = MOIS_FR[parts[2]]
        year = int(parts[3])
        return year, month, day
    except Exception:
        return None

def main():
    cal = Calendar()
    session = requests.Session()
    
    # --- MÉMOIRE ---
    # Pour savoir quel cours est actif sur quel créneau (ex: '18:15' -> UE '7')
    active_ue_on_slot = {} 
    
    # Pour savoir à quelle séance on est pour chaque UE (ex: UE '7' -> Séance 3)
    ue_progress = {ue_id: 0 for ue_id in UE_DB.keys()}

    print("Démarrage du scraping intelligent...")

    # On scanne une large plage pour reconstituer l'historique
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
                        current_date_tuple = parse_french_date(date_div.get_text(strip=True))
                
                # --- LIGNE DE COURS ---
                elif 'hover' in classes and current_date_tuple:
                    cols = row.find_all('td')
                    if len(cols) < 7: continue
                    
                    # 1. HORAIRES
                    time_text = cols[0].get_text(separator=" ", strip=True)
                    times = re.findall(r'\d{2}:\d{2}', time_text)
                    if len(times) < 2: continue
                    
                    start_hm = times[0].split(':') # 18:15
                    end_hm = times[1].split(':')
                    slot_key = f"{start_hm[0]}:{start_hm[1]}"

                    # 2. IDENTIFICATION DE L'UE
                    raw_ue_text = cols[4].get_text(strip=True)
                    subject_raw = cols[2].get_text(strip=True)
                    
                    ue_id = None
                    is_explicit_start = False

                    # A. Cas Explicite (Le site affiche #UE)
                    match = re.search(r'#(\d+)', raw_ue_text)
                    if match:
                        ue_id = match.group(1)
                        # Si c'est un "Amphi 1" ou "Ouverture", on reset le compteur
                        if "OUVERTURE" in subject_raw.upper() or "AMPHI 1" in subject_raw.upper() or "INTRO" in subject_raw.upper():
                             ue_progress[ue_id] = 0
                             is_explicit_start = True
                        
                        # On met à jour la mémoire du créneau
                        active_ue_on_slot[slot_key] = ue_id

                    # B. Cas Implicite (Pas de #, on regarde la mémoire)
                    else:
                        ue_id = active_ue_on_slot.get(slot_key)

                    # Si aucune UE identifiée, on passe (ou on crée un event générique)
                    if not ue_id:
                        continue

                    # 3. GESTION PROGRESSION & FIN DE COURS
                    # On incrémente le compteur pour cette UE
                    ue_progress[ue_id] += 1
                    current_session_num = ue_progress[ue_id]
                    
                    ue_data = UE_DB.get(ue_id, {})
                    max_sessions = len(ue_data.get("sessions", {}))

                    # STOPPER FINANCE (ou autre) si on dépasse le nombre de séances prévues
                    if current_session_num > max_sessions:
                        # On considère que le cours est fini, on ne l'ajoute pas
                        # et on libère le slot mémoire pour éviter les erreurs futures
                        if active_ue_on_slot.get(slot_key) == ue_id:
                            del active_ue_on_slot[slot_key]
                        continue

                    # 4. ENRICHISSEMENT DONNÉES
                    session_theme = ue_data.get("sessions", {}).get(current_session_num, subject_raw)
                    prof_name = ue_data.get("prof", "")
                    
                    title = f"[UE {ue_id}] {ue_data.get('nom', 'Matière Inconnue')}"
                    
                    # 5. SALLE & EXAMENS
                    room_tag = cols[6].find('span', class_='badge')
                    room = room_tag.get_text(strip=True) if room_tag else "Inconnu"
                    address = room
                    
                    if "ARCUEIL" in room.upper():
                        title = f"📝 EXAMEN - {title}"
                        address = "Maison des Examens, 7 Rue Ernest Renan, 94110 Arcueil"
                        session_theme = "Examen Final"
                    elif "LIGNE" in room.upper():
                        room = "🖥️ En ligne"

                    # 6. CRÉATION EVENT
                    y, m, d = current_date_tuple
                    dt_start = PARIS_TZ.localize(datetime(y, m, d, int(start_hm[0]), int(start_hm[1])))
                    dt_end = PARIS_TZ.localize(datetime(y, m, d, int(end_hm[0]), int(end_hm[1])))

                    e = Event()
                    e.name = f"{title} ({current_session_num}/{max_sessions})"
                    e.begin = dt_start
                    e.end = dt_end
                    e.location = address
                    
                    desc = [
                        f"Thème: {session_theme}",
                        f"Intervenant: {prof_name}",
                        f"Salle: {room}",
                        f"Progression: Séance {current_session_num} sur {max_sessions}"
                    ]
                    e.description = "\n".join(desc)
                    
                    cal.events.add(e)
                    print(f" + {title} - {session_theme} ({dt_start})")

        except Exception as e:
            print(f"Erreur page {page}: {e}")

    with open('planning.ics', 'w', encoding='utf-8') as f:
        f.writelines(cal.serialize_iter())
    print("Calendrier généré !")

if __name__ == "__main__":
    main()
