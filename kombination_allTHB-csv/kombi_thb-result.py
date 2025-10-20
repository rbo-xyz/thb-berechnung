import csv
import pandas as pd
import glob
from pathlib import Path

# Pfad zu deinen CSV-Dateien anpassen
# z. B. alle Dateien in einem Ordner: "daten/*.csv"
base_path = Path(r"C:\Users\r.boppart\FHNW\E-BSc Feldkurs 2025 - VP 5220 GeoSensorik&Monitoring_M365 - Madrisa\500_Auswertung\10_THB-Messungen\Auswertung_Python")

parent_folders = []
folder_paths = []
csv_file = []

for folder in sorted([f for f in base_path.iterdir() if f.is_dir()]):
    csv_files = sorted([f for f in folder.glob("*_Auswertung.csv")])
    csv_file.extend(csv_files)
    parent_folders.append(folder.name) 
    folder_paths.append(str(folder))         

with open("kombination_allTHB-csv/gugus.txt", "w") as f:
    f.write(str(csv_file))

dfs = []
for file in csv_file:
    # Ueberspringe die erste Zeile (Infozeile), nutze zweite Zeile als Header
    df = pd.read_csv(file, sep=";", skiprows=1)
    dfs.append(df)

# Alles zusammenfuegen
combined = pd.concat(dfs, ignore_index=True)

## Neuer pfad
new_folder_path = Path("C:/Users/r.boppart/FHNW/E-BSc Feldkurs 2025 - VP 5220 GeoSensorik&Monitoring_M365 - Madrisa/500_Auswertung/10_THB-Messungen/Auswertung_Python/_all-data/20250925_Kombi_All-Data.csv")

# Als neues CSV speichern
combined.to_csv(new_folder_path, sep=";", index=False)
