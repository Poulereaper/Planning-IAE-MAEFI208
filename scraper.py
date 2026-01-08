import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import re
import pytz
from collections import defaultdict

# --- CONFIGURATION ---
BASE_URL = "https://planning.iae-paris.com/cours?formation=MAE+25.208+FIS&paginate=pages&view=list&filter=all&start_date=2025-09-01"
PARIS_TZ = pytz.timezone('Europe/Paris')

MOIS_FR = {
    'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
    'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
}

# --- DONNÉES DU PROGRAMME PÉDAGOGIQUE (D'après le PDF) ---
UE_INFO = {
    "1": {
        "titre": "UE 1 - Environnement Économique de l'Entreprise",
        "prof": "Stéphane Saussier",
        "desc": "Objectifs : Rôle de l'entreprise, création de richesse, macro/microéconomie.\nÉvaluation : Animation cas (25%), Contrôle mi-parcours (25%), Examen (50%)."
    },
    "2": {
        "titre": "UE 2 - Droit des affaires",
        "prof": "Marianne Dournaux",
        "desc": "Objectifs : Droit des contrats, responsabilité civile, droit des sociétés, droit du travail.\nÉvaluation : Contrôle continu (50%), Contrôle terminal (50%)."
    },
    "3": {
        "titre": "UE 3 - Information comptable",
        "prof": "Stéphane Bellanger",
        "desc": "Objectifs : Modèle comptable IFRS, bilan, compte de résultat, tableaux de flux.\nÉvaluation : Exposés/Participation (25%), Contrôle mi-parcours (25%), Examen études de cas (50%)."
    },
    "4": {
        "titre": "UE 4 - Gestion des Ressources Humaines",
        "prof": "Florent Noël",
        "desc": "Objectifs : Stratégie RH, mobilisation des salariés, GPEC.\nÉvaluation : Préparation cas (50%), Examen final (50%)."
    },
    "5": {
        "titre": "UE 5 - Marketing",
        "prof": "Jean-Luc Brunstein & Ouidade Sabri",
        "desc": "Objectifs : Comportement consommateur, mix marketing, stratégie.\nÉvaluation : Contrôle continu (50%), Examen final (50%)."
    },
    "6": {
        "titre": "UE 6 - De l'idée au Marché (Projets, Innovation & Supply Chain)",
        "prof": "Christine Triomphe",
        "desc": "Objectifs : Supply Chain Management, gestion de projet, innovation frugale, design thinking.\nÉvaluation : Contrôle Continu (50%), Examen final (50%)."
    },
    "7": {
        "titre": "UE 7 - Finance d'entreprise",
        "prof": "Jérôme Caby",
        "desc": "Objectifs : Analyse financière, rentabilité, solvabilité, diagnostic.\nÉvaluation : Contrôle continu (50%), Examen (50%)."
    },
    "8": {
        "titre": "UE 8 - Management des systèmes d'information",
        "prof": "Philippe Eynaud & Jean-Loup Richet",
        "desc": "Objectifs : Gouvernance, urbanisation, alignement stratégique des SI.\nÉvaluation : Contrôle continu (50%), Examen final (50%)."
    },
    "9": {
        "titre": "UE 9 - Contrôle de gestion",
        "prof": "Olivier de La Villarmois",
        "desc": "Objectifs : Coûts complets, CVP, budgets, tableaux de bord.\nÉvaluation : Présentation cas (25%), Contrôle mi-parcours (25%), Examen (50%)."
    },
    "10": {
        "titre": "UE 10 - Organisations et comportements",
        "prof": "Nathalie Raulet-Croset",
        "desc": "Objectifs : Comportement organisationnel, leadership, changement.\nÉvaluation : Contrôle continu (50%), Examen (50%)."
    },
    "11": {
        "titre": "UE 11 - Stratégie de l'entreprise",
        "prof": "Didier Chabaud & Pierre Garaudel",
        "desc": "Objectifs : Analyse concurrentielle, Business models, stratégie corporate.\nÉvaluation : Voir règlement général."
    },
    "12": {
        "titre": "UE 12 - Management international",
        "prof": "Pierre-Yves Lagroue",
        "desc": "Objectifs : Internationalisation, éthique, management interculturel.\nÉvaluation : Contrôle continu (50%), Examen final (50%)."
    },
    # Ajout des thématiques ou séminaires si identifiés par un numéro dans le HTML
}

def parse_french_date(date_str):
    parts = date_str.lower().split()
    try:
        day = int(parts[1])
        month = MOIS_FR[parts[2]]
        year = int(parts[3])
        return year, month, day
    except Exception as e:
        print(f"Erreur date: {date_str} - {e}")
        return None

def main():
    session = requests.Session()
    all_courses = [] # Liste pour stocker tous les cours avant de générer l'ICS

    # 1. SCRAPING
    # On scanne les pages
    for page in range(1, 25):
        url = f"{BASE_URL}&page={page}"
        print(f"Scraping page {page}...")
        
        try:
            response = session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            rows = soup.select('table.table tbody tr')
            
            if not rows:
                print("Fin des résultats.")
                break

            current_date_tuple = None
            
            for row in rows:
                classes = row.get('class', [])
                
                # --- LIGNE DE DATE ---
                if 'bg-slate-50' in classes:
                    date_div = row.find('div', class_='text-xl')
                    if date_div:
                        raw_date = date_div.get_text(strip=True)
                        current_date_tuple = parse_french_date(raw_date)
                
                # --- LIGNE DE COURS ---
                elif 'hover' in classes and current_date_tuple:
                    cols = row.find_all('td')
                    if len(cols) < 7: continue 
                    
                    time_text = cols[0].get_text(separator=" ", strip=True)
                    times = re.findall(r'\d{2}:\d{2}', time_text)
                    
                    if len(times) >= 2:
                        start_hm = times[0].split(':')
                        end_hm = times[1].split(':')
                        
                        y, m, d = current_date_tuple
                        dt_start_naive = datetime(y, m, d, int(start_hm[0]), int(start_hm[1]))
                        dt_end_naive = datetime(y, m, d, int(end_hm[0]), int(end_hm[1]))
                        
                        dt_start = PARIS_TZ.localize(dt_start_naive)
                        dt_end = PARIS_TZ.localize(dt_end_naive)

                        original_subject = cols[2].get_text(strip=True)
                        ue_raw = cols[4].get_text(strip=True) # Ex: "#7" ou "7" ou vide
                        ue_clean = ue_raw.replace('#', '').strip()

                        room = "Inconnu"
                        room_tag = cols[6].find('span', class_='badge')
                        if room_tag:
                            room = room_tag.get_text(strip=True)

                        # On stocke les données brutes dans un dictionnaire
                        course_data = {
                            'start': dt_start,
                            'end': dt_end,
                            'original_subject': original_subject,
                            'ue_id': ue_clean,
                            'room': room,
                            'is_exam': False
                        }
                        
                        # Détection basique examen via salle
                        if "ARCUEIL" in room.upper() or "EXAMEN" in original_subject.upper():
                            course_data['is_exam'] = True
                            course_data['room'] = "Maison des Examens (Arcueil)"
                            course_data['location'] = "Maison des Examens, 7 Rue Ernest Renan, 94110 Arcueil"
                        else:
                            course_data['location'] = room

                        all_courses.append(course_data)

        except Exception as e:
            print(f"Erreur sur page {page}: {e}")

    # 2. POST-TRAITEMENT ET ENRICHISSEMENT
    print("Traitement et enrichissement des données...")
    
    # On groupe les cours par UE pour trouver le premier et le dernier
    courses_by_ue = defaultdict(list)
    for c in all_courses:
        if c['ue_id'] and c['ue_id'] in UE_INFO:
            courses_by_ue[c['ue_id']].append(c)
    
    # Pour chaque UE, on trie par date pour identifier ouverture/clôture
    for ue_id, courses in courses_by_ue.items():
        courses.sort(key=lambda x: x['start'])
        
        # Le premier est l'ouverture
        if courses:
            courses[0]['is_opening'] = True
        
        # Le dernier est la clôture (si ce n'est pas déjà marqué comme examen Arcueil, c'est probablement l'amphi de clôture)
        if courses and len(courses) > 1:
            courses[-1]['is_closing'] = True

    # 3. GÉNÉRATION ICS
    cal = Calendar()

    for data in all_courses:
        e = Event()
        e.begin = data['start']
        e.end = data['end']
        e.location = data.get('location', data['room'])
        
        # Récupération des infos enrichies
        ue_id = data['ue_id']
        info = UE_INFO.get(ue_id)
        
        title_prefix = ""
        description_lines = [f"Salle: {data['room']}"]

        if info:
            base_title = info['titre']
            description_lines.append(f"Intervenant: {info['prof']}")
            description_lines.append("-" * 10)
            description_lines.append(info['desc'])
        else:
            base_title = data['original_subject']
            if ue_id:
                base_title = f"UE #{ue_id} - {base_title}"

        # Gestion des tags spéciaux (Exam, Ouverture, Clôture)
        if data['is_exam']:
            title_prefix = "[EXAMEN] "
            description_lines.insert(0, "⚠️ EXAMEN FINAL")
        elif data.get('is_closing'):
            title_prefix = "[CLÔTURE] "
            description_lines.insert(0, "ℹ️ Probable Amphi de clôture / Dernière séance")
        elif data.get('is_opening'):
            title_prefix = "[OUVERTURE] "
            description_lines.insert(0, "ℹ️ Probable Amphi d'ouverture / Première séance")

        e.name = f"{title_prefix}{base_title}"
        e.description = "\n".join(description_lines)
        
        cal.events.add(e)

    # Sauvegarde
    output_filename = 'planning_enrichi.ics'
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.writelines(cal.serialize_iter())
    
    print(f"Terminé ! Fichier généré : {output_filename}")

if __name__ == "__main__":
    main()
