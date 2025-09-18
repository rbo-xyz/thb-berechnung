import tabulate as tl
from datetime import datetime
import os

def export_protocol(df300_new, 
                    info:list, 
                    visur:str, 
                    file_path:str,
                    data:list):
    """
    Exportiert ein Trigonometrisches Höhenbestimmungsprotokoll in eine formatierte Textdatei.

    Die Funktion erstellt ein Textprotokoll mit:
    - Tabellenübersicht der Messergebnisse (mit tabulate formatiert)
    - Header mit Visur-ID und Auswertungszeit
    - Footer mit Messparametern, Start- und Endpunkten, Höhendifferenz,
      mittlerer Schrägdistanz, Refraktionskoeffizient und Präanalyse-Komponenten

    Parameter:
    -----------
    df300_new : pandas.DataFrame
        DataFrame mit den berechneten Messwerten (Schrägdistanz, Höhendifferenz, Refraktionskoeffizient).
    info : list
        Liste mit Informationen über Start- und Endpunkte, Höhendifferenzen, Refraktionskoeffizienten
        und Präanalyse-Komponenten. Erwartetes Format:
        [pktNr_A, pktNr_B, delta_h_aprox, mean_delta_h, std_delta_h, mean_k, std_k, mean_sd, std_sd, genauigkeit_mm, präanalyse_komponenten]
    visur : str
        ID der Messung, wird für die Benennung der Ausgabedatei verwendet.
    file_path : str
        Pfad zum Ordner, in dem die Protokolldatei gespeichert werden soll.
    data : list
        Messparameterliste: [Signalhöhe Station A, Instrumentenoffset A, Signalhöhe Station B, Instrumentenoffset B]

    Rückgabe:
    ----------
    None
        Die Funktion schreibt das Protokoll als Textdatei in den angegebenen Ordner.
        Bei Fehlern wird eine Fehlermeldung ausgegeben.
    """

    try:
        current_time = datetime.now().strftime("%d.%m.%Y / %H:%M")

        formatting = (".4f", ".4f", ".4f", ".4f",".4f", ".4f",  ".2f")
        colalign = ["right", "center", "center", "center", "center", "center", "center"]
        tbl_str = tl.tabulate(df300_new, headers="keys", tablefmt="outline", floatfmt=formatting, colalign=colalign, showindex=True)

        header = ["Trigonometrische Höhenbestimmung - Protokoll der Auswertung",
                  f"Visur ID: {visur}, Ausgewertet am {current_time}",
                  "<<---------------------------------------------------------------->>\n"]

        footer = ["\n<<---------------------------------------------------------------->>",
                  "Angegebene Parameter der Messung:",
                  f" - Signalhöhe Station A: {data[0]} m",
                  f" - Instrumentenoffset Station A: {data[1]} m",
                  f" - Signalhöhe Station B: {data[2]} m",
                  f" - Instrumentenoffset Station B: {data[3]} m",
                  "<<---------------------------------------------------------------->>",
                  f"Startpunkt (A): {info[0]} // Endpunkt (B): {info[1]}",
                  f"Höhendifferenz berechnet aus Näherungskoordinaten: {info[2]} m",
                  f"Mittlere Schrägdistanz inkl. 1σ: {info[7]:.4f} m ± {info[8]:.4f} m",
                  f"Mittlere Höhendifferenz über Trig. Höhenbestimmung inkl. 1σ: {info[3]} m ± {info[4]} m",
                  f"Mittlerer Refraktionskoeffizient k inkl. 1σ: {info[5]:.2f} ± {info[6]:.2f}",
                  "<<---------------------------------------------------------------->>",
                  f"Die Präanalyse ergibt eine Genauigkeit der Höhenbestimmung von ca. {info[9]:.2f} mm // {info[9]/1000:.4f} m ",
                  "Die Komponenten der Präanalyse sind (in mm):",
                  f" - Distanzkomponente: {info[10][0]:.2f} mm",
                  f" - Zenitwinkelkomponente: {info[10][1]:.2f} mm",
                  f" - Refraktionskomponente: {info[10][2]:.2f} mm (wird bei gegenseitig gleichzeitiger Messung vernachlässigt)",
                  f" - Genauigkeit Instrumentenhöhe: {info[10][3]:.2f} mm",
                  f" - Genauigkeit Signalhöhe: {info[10][4]:.2f} mm",]


        full_text = "\n".join(header) + "\n"  + tbl_str + "\n" + "\n".join(footer)

        full_path = os.path.join(file_path, visur + "_Protokoll.txt")

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(full_text)

    except Exception as e:
        print(f"Fehler beim Exportieren der Protokolldatei: {e}")


def export2csv(df300_new, 
               info:list, 
               visur:str, 
               file_path:str,
               data:list):
    """
    Exportiert ein DataFrame zusammen mit einem einleitenden Header-Text als CSV-Datei.

    Parameters
    ----------
    df300_new : pandas.DataFrame
        Das zu exportierende DataFrame mit den Messergebnissen.
    info : list
        Liste mit zusätzlichen Informationen zur Auswertung (z. B. Start-/Endpunkt, Mittelwerte, Standardabweichungen).
    visur : str
        Identifikationsstring der Visur, wird auch für die Dateibenennung verwendet.
    file_path : str
        Pfad zum Verzeichnis, in dem die CSV-Datei gespeichert werden soll.
    data : list
        Liste mit Messparametern (z. B. Signal- und Instrumentenhöhen), die im Header berücksichtigt werden können.

    Returns
    -------
    None
        Die Funktion speichert die CSV-Datei auf der Festplatte. Es wird kein Wert zurückgegeben.

    Notes
    -----
    - Die CSV-Datei enthält in der ersten Zeile einen Header-Text mit Visur-ID und aktuellem Datum/Zeit.
    - Das DataFrame wird danach angehängt, ohne Indexspalte, mit Semikolon als Trennzeichen.
    - Bestehende Dateien mit gleichem Namen werden überschrieben.
    """

    try:
        current_time = datetime.now().strftime("%d.%m.%Y / %H:%M")
        header = f"Trigonometrische Höhenbestimmung Madrisa - VisurID: {visur}, Ausgewertet am {current_time}"

        full_path = os.path.join(file_path, visur + "_Auswertung.csv")

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(header)
            f.write("\n")

        df300_new.to_csv(full_path, mode="a", index=False, sep=";")

    except Exception as e:
        print(f"Fehler beim Exportieren der CSV-Datei: {e}")