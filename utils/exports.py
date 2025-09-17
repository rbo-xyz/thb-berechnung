import tabulate as tl
from datetime import datetime

def export_protocol(df300_new, 
                    info:list, 
                    visur:str, 
                    file_path:str):
    """
    Exportiert das Protokoll der trigonometrischen Höhenbestimmung als ASCII-Textdatei.

    Die Funktion erstellt eine formatierte Tabelle mit allen Messwerten, fügt Header-Informationen 
    (Visur-ID, Auswertungsdatum) und Footer-Informationen (Start-/Endpunkt, Höhendifferenz, 
    mittlere Schrägdistanz, Refraktionskoeffizient) hinzu und speichert alles in einer Datei.

    Parameters
    ----------
    df300_new : pandas.DataFrame
        DataFrame mit den final berechneten Messwerten. Erwartete Spalten:
        - "ID Messung"
        - "Schrägdistanz A --> B [m]"
        - "Schrägdistanz B --> A [m]"
        - "Mittlere Schrägdistanz [m]"
        - "Höhendifferenz [m]"
        - "Refraktionskoeffizient k"
    info : list
        Liste mit wichtigen Kennwerten der Messung, z.B.:
        - info[0] : Startpunkt (A)
        - info[1] : Endpunkt (B)
        - info[2] : Höhendifferenz aus Näherungskoordinaten
        - info[3] : Mittlere Höhendifferenz
        - info[4] : Standardabweichung Höhendifferenz
        - info[5] : Mittlerer Refraktionskoeffizient k
        - info[6] : Standardabweichung k
        - info[7] : Mittlere Schrägdistanz
        - info[8] : Standardabweichung Schrägdistanz
    visur : str
        ID der Visur (Messung), die im Header der Protokolldatei angezeigt wird.
    file_path : str
        Pfad zur Ausgabedatei, in die das Protokoll geschrieben wird.

    Returns
    -------
    None
        Die Funktion speichert die formatierte Tabelle direkt in der angegebenen Datei.
        Im Fehlerfall wird eine Meldung auf der Konsole ausgegeben.
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

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_text)

    except Exception as e:
        print(f"Fehler beim Exportieren der Protokolldatei: {e}")