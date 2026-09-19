import json
import os
import csv
from datetime import datetime

folder = "candidates_data"

# Créer un fichier CSV
with open('resultats_complets.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['ID', 'Nom', 'Téléphone', 'Poste', 'Expérience', 'Temps Disponible', 'Motivation', 'Disponibilité', 'Heure Début', 'Heure Fin']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            if filename.endswith(".json"):
                with open(os.path.join(folder, filename), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    writer.writerow({
                        'ID': data.get('candidate_id', ''),
                        'Nom': data.get('first_name', ''),
                        'Téléphone': data.get('phone', ''),
                        'Poste': data.get('position', ''),
                        'Expérience': data.get('experience', ''),
                        'Temps Disponible': data.get('technical_skills', ''),
                        'Motivation': data.get('motivation', ''),
                        'Disponibilité': data.get('availability', ''),
                        'Heure Début': data.get('start_time', ''),
                        'Heure Fin': data.get('end_time', '')
                    })

print("✅ Fichier créé : resultats_complets.csv")