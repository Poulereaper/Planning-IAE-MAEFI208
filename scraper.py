import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import re
import sys

# --- CONFIGURATION ---
# Le lien EXACT qui affiche tes cours (avec le filtre de ta promo)
# J'ai mis le filtre pour MAE 25.208 FIS basé sur ta demande, sur une plage large
BASE_URL = "https://planning.iae-paris.com/cours?formation=MAE+25.208+FIS&paginate=pages&view=list&filter=upcoming"

# Mapping des mois français pour la conversion
MOIS_FR = {
    'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
    'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
}

def parse_french_date(date_str):
    """Convertit 'Mardi 6 janvier 2026' en objet date (2026-01-06)"""
    parts = date_str.lower().split()
    # Format attendu: [jour_nom, jour_num, mois, annee]
    # Ex: ['mardi', '6', 'janvier', '2026']
    try:
        day = int(parts[1])
        month = MOIS_FR[parts[2]]
        year = int(parts[3])
        return datetime(year, month, day)
    except Exception as e:
        print(f"Erreur date: {date_str} - {e}")
        return None

def main():
    cal = Calendar()
    session = requests.Session()
    
    # On va scanner les pages 1 à 10 (largeur de sécurité)
    for page in range(1, 11):
        url = f"{BASE_URL}&page={page}"
        print(f"Scraping {url}...")
        
        try:
            response = session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            rows = soup.select('table.table tbody tr')
            
            if not rows:
                print("Plus de lignes trouvées, fin.")
                break

            current_date = None
            
            for row in rows:
                classes = row.get('class', [])
                
                # Cas 1 : C'est une ligne de DATE (bg-slate-50)
                if 'bg-slate-50' in classes:
                    date_div = row.find('div', class_='text-xl')
                    if date_div:
                        raw_date = date_div.get_text(strip=True)
                        current_date = parse_french_date(raw_date)
                        print(f"--> Date trouvée : {raw_date}")
                
                # Cas 2 : C'est une ligne de COURS (hover)
                elif 'hover' in classes and current_date:
                    cols = row.find_all('td')
                    if len(cols) < 5: continue
                    
                    # Extraction Heure (Col 0)
                    time_text = cols[0].get_text(separator=" ", strip=True) # "09:00 12:00"
                    times = re.findall(r'\d{2}:\d{2}', time_text)
                    
                    if len(times) >= 2:
                        start_str, end_str = times[0], times[1]
                        
                        # Extraction Matière (Col 2)
                        subject = cols[2].get_text(strip=True)
                        
                        # Extraction Salle (Col 6 - souvent dans un span badge)
                        room = "Inconnu"
                        if len(cols) > 6:
                            room_tag = cols[6].find('span', class_='badge')
                            if room_tag:
                                room = room_tag.get_text(strip=True)
                        
                        # Création de l'événement
                        e = Event()
                        e.name = f"{subject}"
                        e.begin = f"{current_date.strftime('%Y-%m-%d')} {start_str}:00"
                        e.end = f"{current_date.strftime('%Y-%m-%d')} {end_str}:00"
                        e.location = room
                        e.description = f"Cours IAE\nSalle: {room}"
                        
                        # Correction Fuseau Horaire (Paris)
                        # La lib 'ics' gère mal les TZ automatiques, on force le décalage basique
                        # L'idéal est de laisser l'iPhone gérer, mais il faut que le fichier soit propre.
                        # Pour simplifier ici, on enregistre en "floating time" (heure locale)
                        
                        cal.events.add(e)
                        print(f"   + Ajouté: {subject} ({start_str}-{end_str})")

        except Exception as e:
            print(f"Erreur critique sur page {page}: {e}")

    # Sauvegarde du fichier
    with open('planning.ics', 'w', encoding='utf-8') as f:
        f.writelines(cal.serialize_iter())
    print("Fichier planning.ics généré avec succès !")

if __name__ == "__main__":
    main()