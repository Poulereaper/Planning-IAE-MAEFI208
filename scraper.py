import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import re
import pytz

# --- CONFIGURATION ---
# Historique complet (01/09/2025) + Filtre 'all'
BASE_URL = "https://planning.iae-paris.com/cours?formation=MAE+25.208+FIS&paginate=pages&view=list&filter=all&start_date=2025-09-01"
PARIS_TZ = pytz.timezone('Europe/Paris')

# --- BASE DE DONNÉES DU PROGRAMME (Issue du PDF) ---
UE_DETAILS = {
    "1": {
        "nom": "Environnement Économique de l'Entreprise",
        "prof": "Stéphane Saussier",
        "obj": "Comprendre le rôle de l'entreprise (macro/micro) et ses décisions de production."
    },
    "2": {
        "nom": "Droit des affaires",
        "prof": "Marianne Dournaux",
        "obj": "Connaissances juridiques élémentaires, droit comme outil d'organisation."
    },
    "3": {
        "nom": "Information comptable",
        "prof": "Stéphane Bellanger",
        "obj": "Modèle comptable international et compréhension des états financiers."
    },
    "4": {
        "nom": "Gestion des Ressources Humaines",
        "prof": "Florent Noël",
        "obj": "Lien stratégie/RH, enjeux de la GRH et modèles existants."
    },
    "5": {
        "nom": "Marketing",
        "prof": "J.-L. Brunstein & O. Sabri",
        "obj": "Processus marketing, de l'étude des besoins à la stratégie."
    },
    "6": {
        "nom": "Management Projets, Innovation & SC",
        "prof": "Christine Triomphe",
        "obj": "Supply Chain Management et pilotage de la création de valeur/innovation."
    },
    "7": {
        "nom": "Finance d'entreprise",
        "prof": "Jérôme Caby",
        "obj": "Analyse financière, rentabilité et solvabilité."
    },
    "8": {
        "nom": "Management des SI",
        "prof": "P. Eynaud & J.-L. Richet",
        "obj": "Outils SI et TIC comme leviers du changement organisationnel."
    },
    "9": {
        "nom": "Contrôle de gestion",
        "prof": "Olivier de La Villarmois",
        "obj": "Outils de pilotage: proposition de valeur vs structure de coûts."
    },
    "10": {
        "nom": "Organisations et comportements",
        "prof": "Nathalie Raulet-Croset",
        "obj": "Comportements individuels et collectifs (sociologie/psychosociologie)."
    },
    "11": {
        "nom": "Stratégie de l'entreprise",
        "prof": "D. Chabaud & P. Garaudel",
        "obj": "Concepts et outils de la stratégie face aux enjeux actuels."
    },
    "12": {
        "nom": "Management international",
        "prof": "Pierre-Yves Lagroue",
        "obj": "Facteurs des affaires internationales et stratégies d'internationalisation."
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
    except Exception as e:
        return None

def main():
    cal = Calendar()
    session = requests.Session()
    
    # MEMOIRE : Pour se souvenir quelle UE est à quelle heure
    # Ex: {'18:15': '5', '20:15': '6'}
    ue_memory_by_slot = {}

    print("Démarrage du scraping avec enrichissement des données...")

    # On scanne large pour l'historique
    for page in range(1, 25):
        url = f"{BASE_URL}&page={page}"
        print(f"Lecture page {page}...")
        
        try:
            response = session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            rows = soup.select('table.table tbody tr')
            
            if not rows:
                break

            current_date_tuple = None
            
            for row in rows:
                classes = row.get('class', [])
                
                # --- DATE ---
                if 'bg-slate-50' in classes:
                    date_div = row.find('div', class_='text-xl')
                    if date_div:
                        current_date_tuple = parse_french_date(date_div.get_text(strip=True))
                
                # --- COURS ---
                elif 'hover' in classes and current_date_tuple:
                    cols = row.find_all('td')
                    if len(cols) < 7: continue
                    
                    # 1. ANALYSE HORAIRE
                    time_text = cols[0].get_text(separator=" ", strip=True)
                    times = re.findall(r'\d{2}:\d{2}', time_text)
                    if len(times) < 2: continue
                    
                    start_hm = times[0].split(':') # ['18', '15']
                    end_hm = times[1].split(':')
                    
                    start_time_key = f"{start_hm[0]}:{start_hm[1]}" # Clé de mémoire "18:15"

                    # Dates avec Fuseau Paris
                    y, m, d = current_date_tuple
                    dt_start = PARIS_TZ.localize(datetime(y, m, d, int(start_hm[0]), int(start_hm[1])))
                    dt_end = PARIS_TZ.localize(datetime(y, m, d, int(end_hm[0]), int(end_hm[1])))

                    # 2. IDENTIFICATION DE L'UE
                    raw_ue_text = cols[4].get_text(strip=True) # Ex: "#5" ou vide
                    ue_number = None

                    # A-t-on un numéro explicite ?
                    match = re.search(r'#(\d+)', raw_ue_text)
                    if match:
                        ue_number = match.group(1)
                        # On met à jour la mémoire pour ce créneau horaire
                        ue_memory_by_slot[start_time_key] = ue_number
                    else:
                        # Pas de numéro, on regarde la mémoire pour ce créneau
                        ue_number = ue_memory_by_slot.get(start_time_key)

                    # 3. RÉCUPÉRATION DES DÉTAILS DU PDF
                    details = UE_DETAILS.get(ue_number, {})
                    
                    subject_name = cols[2].get_text(strip=True)
                    prof_name = details.get("prof", "")
                    obj_desc = details.get("obj", "")
                    
                    # Titre Propre
                    if details:
                        final_title = f"[UE {ue_number}] {details['nom']}"
                    else:
                        final_title = subject_name # Fallback si pas d'UE trouvée

                    # 4. SALLE & CAS SPÉCIAUX (Examens)
                    room_tag = cols[6].find('span', class_='badge')
                    room = room_tag.get_text(strip=True) if room_tag else "Inconnu"
                    address = room

                    # Logique Examens Arcueil
                    if "ARCUEIL" in room.upper():
                        final_title = f"📝 EXAMEN - {final_title}"
                        address = "Maison des Examens, 7 Rue Ernest Renan, 94110 Arcueil"
                        room = "Maison des Examens"
                    
                    # Logique Amphi d'ouverture (souvent en ligne)
                    if "Ouverture" in subject_name or "Amphi" in subject_name:
                         final_title = f"📢 {final_title} (Amphi)"

                    # 5. CONSTRUCTION DE L'EVENT
                    e = Event()
                    e.name = final_title
                    e.begin = dt_start
                    e.end = dt_end
                    e.location = address
                    
                    description = []
                    if prof_name: description.append(f"👨‍🏫 Prof: {prof_name}")
                    if room: description.append(f"📍 Salle: {room}")
                    if obj_desc: description.append(f"🎯 Objectif: {obj_desc}")
                    description.append(f"ℹ️ Info brute: {subject_name}")
                    
                    e.description = "\n".join(description)
                    
                    cal.events.add(e)
                    print(f"   + {final_title} ({start_time_key})")

        except Exception as e:
            print(f"Erreur page {page}: {e}")

    with open('planning.ics', 'w', encoding='utf-8') as f:
        f.writelines(cal.serialize_iter())
    print("Calendrier généré avec succès.")

if __name__ == "__main__":
    main()
