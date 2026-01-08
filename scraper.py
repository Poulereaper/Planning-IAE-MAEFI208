import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import re
import pytz # Indispensable pour régler le problème de décalage horaire

# --- CONFIGURATION ---
# 1. On commence au 01/09/2025 pour avoir l'historique
# 2. filter=all pour tout avoir (pas juste 'upcoming')
BASE_URL = "https://planning.iae-paris.com/cours?formation=MAE+25.208+FIS&paginate=pages&view=list&filter=all&start_date=2025-09-01"

# Définition du fuseau horaire de Paris (gère l'heure d'été/hiver automatiquement)
PARIS_TZ = pytz.timezone('Europe/Paris')

MOIS_FR = {
    'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
    'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
}

def parse_french_date(date_str):
    """
    Convertit 'Mardi 6 janvier 2026' en tuple (annee, mois, jour)
    """
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
    cal = Calendar()
    session = requests.Session()
    
    # On scanne plus de pages car on récupère l'historique (ex: 20 pages)
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

            current_date_tuple = None # (year, month, day)
            
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
                    if len(cols) < 7: continue # On a besoin d'au moins 7 colonnes (0 à 6)
                    
                    # 1. HORAIRES
                    time_text = cols[0].get_text(separator=" ", strip=True)
                    times = re.findall(r'\d{2}:\d{2}', time_text)
                    
                    if len(times) >= 2:
                        start_hm = times[0].split(':') # ['18', '15']
                        end_hm = times[1].split(':')   # ['20', '15']
                        
                        # Construction des objets Date "Naïfs" (sans fuseau)
                        y, m, d = current_date_tuple
                        dt_start_naive = datetime(y, m, d, int(start_hm[0]), int(start_hm[1]))
                        dt_end_naive = datetime(y, m, d, int(end_hm[0]), int(end_hm[1]))
                        
                        # Localisation : On dit "Ces dates sont à Paris"
                        # La librairie ICS convertira ensuite en UTC automatiquement pour le fichier
                        dt_start = PARIS_TZ.localize(dt_start_naive)
                        dt_end = PARIS_TZ.localize(dt_end_naive)

                        # 2. MATIÈRE & UE
                        subject = cols[2].get_text(strip=True)
                        ue_text = cols[4].get_text(strip=True) # Récupération de la colonne UE (#5)
                        
                        full_title = subject
                        if ue_text:
                            full_title = f"{ue_text} - {subject}"

                        # 3. SALLE & EXAMENS
                        room = "Inconnu"
                        room_tag = cols[6].find('span', class_='badge')
                        if room_tag:
                            room = room_tag.get_text(strip=True)
                        
                        location_address = room # Par défaut, l'adresse est le nom de la salle
                        
                        # Logique Spéciale ARCUEIL
                        if "ARCUEIL" in room.upper():
                            full_title = f"[EXAMEN] {full_title}"
                            location_address = "Maison des Examens, 7 Rue Ernest Renan, 94110 Arcueil"
                            room = "Maison des Examens (Arcueil)"

                        # CRÉATION DE L'ÉVÉNEMENT
                        e = Event()
                        e.name = full_title
                        e.begin = dt_start
                        e.end = dt_end
                        e.location = location_address
                        e.description = f"Cours IAE\nSalle: {room}\nUE: {ue_text}"
                        
                        cal.events.add(e)
                        print(f"   + {full_title} ({dt_start.strftime('%H:%M')})")

        except Exception as e:
            print(f"Erreur sur page {page}: {e}")

    # Sauvegarde
    with open('planning.ics', 'w', encoding='utf-8') as f:
        f.writelines(cal.serialize_iter())

if __name__ == "__main__":
    main()
