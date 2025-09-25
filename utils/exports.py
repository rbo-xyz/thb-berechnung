import tabulate as tl
from datetime import datetime
import os

from pathlib import Path
import markdown
from weasyprint import HTML

from utils.plots import boxplot_beaut, scatterplot_vwinkel

def path_to_file_url(path):
    return "file:///" + str(path.resolve()).replace("\\", "/")

def export_protocol(df300_new,
                    infos_vis:list, 
                    infos_height:list, 
                    infos_k:list, 
                    infos_sd:list, 
                    visur:str, 
                    file_path:str, 
                    data:list):
    """
    Exportiert ein Trigonometrisches Höhenbestimmungsprotokoll als formatierte Textdatei.

    Die Funktion erstellt ein Protokoll mit:
    - Tabellenübersicht der Messergebnisse (tabulate-formatiert)
    - Header mit Visur-ID und Auswertungszeitpunkt
    - Footer mit Messparametern, Start- und Endpunkten, Höhendifferenz,
      mittlerer Schrägdistanz, Refraktionskoeffizient und Präanalyse-Komponenten

    Parameter:
    ----------
    df300_new : pandas.DataFrame
        DataFrame mit berechneten Messwerten (Schrägdistanz, Höhendifferenz, Refraktionskoeffizient).
    infos_vis : list
        Liste mit Informationen über Start-/Endpunkte und Präanalyse: 
        [pktNr_A, pktNr_B, Genauigkeit Präanalyse, Präanalyse-Komponenten].
    infos_height : list
        Statistische Kennwerte der Höhendifferenz.
    infos_k : list
        Statistische Kennwerte der Refraktionskoeffizienten.
    infos_sd : list
        Statistische Kennwerte der mittleren Schrägdistanz.
    visur : str
        ID der Messung; wird für die Benennung der Protokolldatei verwendet.
    file_path : str
        Pfad zum Verzeichnis, in dem das Protokoll gespeichert wird.
    data : list
        Messparameter: [Signalhöhe A, Offset A, Signalhöhe B, Offset B].

    Rückgabe:
    ---------
    None
        Das Protokoll wird als Textdatei gespeichert; es erfolgt keine Rückgabe.
    """

    try:
        current_time = datetime.now().strftime("%d.%m.%Y / %H:%M")

        formatting = (".4f", ".4f", ".4f", ".4f", ".4f", ".4f", ",.4f", ".4f", ".4f", ".4f", ".2f")
        colalign = ["right", "center", "center", "center", "center", "center", "center", "center", "center", "center"]
        tbl_str = tl.tabulate(df300_new, headers="keys", tablefmt="outline", floatfmt=formatting, colalign=colalign, showindex=True)

        header = ["Trigonometrische Höhenbestimmung - Protokoll der Auswertung",
                  f"Visur ID: {visur}, Ausgewertet am {current_time}",
                  "<<---------------------------------------------------------------->>\n"]

        footer = ["\n<<---------------------------------------------------------------->>",
                  "Angegebene Parameter der Messung:",
                  f" - Instrumentenhöhe Station A: {data[0] - data[1]} m",
                  f" - Offset Station A: {data[1]} m",
                  f" - Signalhöhe Station A: {data[0]} m",
                  "",
                  f" - Instrumentenhöhe Station B: {data[2] - data[3]} m",               
                  f" - Instrumentenoffset Station B: {data[3]} m",
                  f" - Signalhöhe Station B: {data[2]} m",
                  "",
                  f" - Startpunkt (A): {infos_vis[0]} // Endpunkt (B): {infos_vis[1]}",
                  "<<---------------------------------------------------------------->>",
                  "Höhenstatistiken der Auswertung:",
                  f"Höhendifferenz berechnet aus Näherungskoordinaten: {infos_height[0]} m",
                  f"Mittlere Höhendifferenz über Trig. Höhenbestimmung inkl. 1σ: {infos_height[1]} m ± {infos_height[2]} m",
                  f"Mittlere Höhendifferenz (Lage 1) inkl. 1σ: {infos_height[3]} m ± {infos_height[4]} m",
                  f"Mittlere Höhendifferenz (Lage 2) inkl. 1σ: {infos_height[5]} m ± {infos_height[6]} m",
                  "<<---------------------------------------------------------------->>",
                  "Schrägdistanzstatistik der Auswertung:",
                  f"Mittlere Schrägdistanz inkl. 1σ: {infos_sd[0]} m ± {infos_sd[1]} m",
                  f"Mittlere Schrägdistanz (Lage 1) inkl. 1σ: {infos_sd[2]} m ± {infos_sd[3]} m",
                  f"Mittlere Schrägdistanz (Lage 2) inkl. 1σ: {infos_sd[4]} m ± {infos_sd[5]} m",
                  "<<---------------------------------------------------------------->>",
                  "Refraktionskoeffizientenstatistik der Auswertung:",
                  f"Mittlerer Refraktionskoeffizient k inkl. 1σ: {infos_k[0]} ± {infos_k[1]}",
                  f"Mittlerer Refraktionskoeffizient k (Lage 1) inkl. 1σ: {infos_k[2]} ± {infos_k[3]}",
                  f"Mittlerer Refraktionskoeffizient k (Lage 2) inkl. 1σ: {infos_k[4]} ± {infos_k[5]}",
                  "<<---------------------------------------------------------------->>",
                  f"Die Präanalyse ergibt eine Genauigkeit der Höhenbestimmung von ca. {infos_vis[2]:.2f} mm // {infos_vis[2]/1000:.4f} m ",
                  "Die Komponenten der Präanalyse sind (in mm):",
                  f" - Distanzkomponente: {infos_vis[3][0]:.2f} mm",
                  f" - Zenitwinkelkomponente: {infos_vis[3][1]:.2f} mm",
                  f" - Refraktionskomponente: {infos_vis[3][2]:.2f} mm (wird bei gegenseitig gleichzeitiger Messung vernachlässigt)",
                  f" - Genauigkeit Instrumentenhöhe: {infos_vis[3][3]:.2f} mm",
                  f" - Genauigkeit Signalhöhe: {infos_vis[3][4]:.2f} mm",]


        full_text = "\n".join(header) + "\n"  + tbl_str + "\n" + "\n".join(footer)

        full_path = os.path.join(file_path, visur + "_Protokoll.txt")

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(full_text)

    except Exception as e:
        print(f"Fehler beim Exportieren der Protokolldatei: {e}")


def export2csv(df300_new,
               infos_vis:list, 
               infos_height:list, 
               infos_k:list, 
               infos_sd:list, 
               visur:str, 
               file_path:str, 
               data:list):
    """
    Exportiert ein DataFrame zusammen mit einem einleitenden Header-Text als CSV-Datei.

    Die CSV-Datei enthält:
    - Header-Zeile mit Visur-ID und Auswertungsdatum/-zeit
    - Messergebnisse aus df300_new ohne Indexspalte, Semikolon-getrennt
    - Bestehende Dateien mit gleichem Namen werden überschrieben

    Parameter:
    ----------
    df300_new : pandas.DataFrame
        DataFrame mit den Messergebnissen.
    infos_vis : list
        Liste mit zusätzlichen Informationen zur Auswertung.
    infos_height : list
        Statistische Kennwerte der Höhendifferenz.
    infos_k : list
        Statistische Kennwerte der Refraktionskoeffizienten.
    infos_sd : list
        Statistische Kennwerte der mittleren Schrägdistanz.
    visur : str
        Identifikationsstring der Visur; wird auch für die Dateibenennung verwendet.
    file_path : str
        Pfad zum Verzeichnis, in dem die CSV-Datei gespeichert wird.
    data : list
        Messparameter: [Signalhöhe A, Offset A, Signalhöhe B, Offset B].

    Rückgabe:
    ---------
    None
        Die CSV-Datei wird auf der Festplatte gespeichert; es erfolgt keine Rückgabe.
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


def export_protocol_md_pdf(df300_new,
                           infos_vis:list, 
                           infos_height:list, 
                           infos_k:list, 
                           infos_sd:list, 
                           visur:str, 
                           file_path:str, 
                           data:list):
    """
    Exportiert ein Trigonometrisches Höhenbestimmungsprotokoll als Markdown- und PDF-Datei.

    Funktionen:
    - Markdown-Formatierung mit Tabellenübersicht der Messergebnisse
    - Header mit Visur-ID und Auswertungszeit
    - Footer mit Messparametern, statistischen Kennwerten und Präanalyse-Komponenten
    - PDF-Erstellung über WeasyPrint (Markdown -> HTML -> PDF)
    - PDF im Querformat (A4), saubere Schriftart (Arial) und Zeilenabstand

    Parameter:
    ----------
    df300_new : pandas.DataFrame
        DataFrame mit den berechneten Messwerten.
    infos_vis : list
        Liste mit Informationen über Start-/Endpunkte und Präanalyse: 
        [pktNr_A, pktNr_B, Genauigkeit Präanalyse, Präanalyse-Komponenten].
    infos_height : list
        Statistische Kennwerte der Höhendifferenz.
    infos_k : list
        Statistische Kennwerte der Refraktionskoeffizienten.
    infos_sd : list
        Statistische Kennwerte der mittleren Schrägdistanz.
    visur : str
        ID der Messung; wird für die Benennung der Dateien verwendet.
    file_path : str
        Pfad zum Verzeichnis, in dem Markdown- und PDF-Dateien gespeichert werden.
    data : list
        Messparameter: [Signalhöhe A, Offset A, Signalhöhe B, Offset B].

    Rückgabe:
    ---------
    None
        Das Protokoll wird als Markdown- und PDF-Datei gespeichert; es erfolgt keine Rückgabe.
    """

    try:
        current_time = datetime.now().strftime("%d.%m.%Y / %H:%M")


        # Markdown-kompatible Tabelle
        tbl_str = tl.tabulate(
            df300_new,
            headers="keys",
            tablefmt="github",
            showindex=True,
            floatfmt=(".4f", ".4f", ".4f", ".4f", ".4f", ".4f", ".4f", ".4f", ".4f", ".4f", ".2f")
        )

        header = [
            f"# Trigonometrische Höhenbestimmung - Protokoll der Auswertung",
            f"**Visur ID:** {visur}  ",
            f"**Ausgewertet am:** {current_time}",
            "---"
        ]

        footer = [
            "---",
            "## Angegebene Parameter der Messung",
            f" - Instrumentenhöhe Station A: {data[0] - data[1]} m",
            f" - Offset Station A: {data[1]} m",
            f" - Signalhöhe Station A: {data[0]} m",
            f" - Instrumentenhöhe Station B: {data[2] - data[3]} m",               
            f" - Instrumentenoffset Station B: {data[3]} m",
            f" - Signalhöhe Station B: {data[2]} m",
            f" - Startpunkt (A): {infos_vis[0]} // Endpunkt (B): {infos_vis[1]}",
            "---",
            "## Höhenstatistiken",
            f"- Höhendifferenz (Näherungskoordinaten): {infos_height[0]} m",
            f"- Mittlere Höhendifferenz inkl. 1σ: {infos_height[1]} m ± {infos_height[2]} m",
            f"- Mittlere Höhendifferenz (Lage 1) inkl. 1σ: {infos_height[3]} m ± {infos_height[4]} m",
            f"- Mittlere Höhendifferenz (Lage 2) inkl. 1σ: {infos_height[5]} m ± {infos_height[6]} m",
            "---",
            "## Schrägdistanzstatistik",
            f"- Mittlere Schrägdistanz inkl. 1σ: {infos_sd[0]} m ± {infos_sd[1]} m",
            f"- Mittlere Schrägdistanz (Lage 1) inkl. 1σ: {infos_sd[2]} m ± {infos_sd[3]} m",
            f"- Mittlere Schrägdistanz (Lage 2) inkl. 1σ: {infos_sd[4]} m ± {infos_sd[5]} m",
            "---",
            "## Refraktionskoeffizienten",
            f"- Mittlerer Refraktionskoeffizient inkl. 1σ: {infos_k[0]} ± {infos_k[1]}",
            f"- Mittlerer Refraktionskoeffizient (Lage 1) inkl. 1σ: {infos_k[2]} ± {infos_k[3]}",
            f"- Mittlerer Refraktionskoeffizient (Lage 2) inkl. 1σ: {infos_k[4]} ± {infos_k[5]}",
            "---",
            "## Präanalyse",
            f"#### Genauigkeit der Höhenbestimmung (1σ): {infos_vis[2]:.2f} mm // {infos_vis[2]/1000:.4f} m ",
            "#### Die Komponenten der Präanalyse in 1σ (in mm):",
            f"- Distanzkomponente: {infos_vis[3][0]:.2f} mm",
            f"- Zenitwinkelkomponente: {infos_vis[3][1]:.2f} mm",
            f"- Refraktionskomponente: {infos_vis[3][2]:.2f} mm (bei gleichzeitiger Messung vernachlässigt)",
            f"- Genauigkeit Instrumentenhöhe: {infos_vis[3][3]:.2f} mm",
            f"- Genauigkeit Signalhöhe: {infos_vis[3][4]:.2f} mm"
        ]

        # Markdown zusammenbauen
        full_md = "\n".join(header) + "\n\n" + tbl_str + "\n\n" + "\n".join(footer)

        # Pfade für Markdown und PDF
        md_path = os.path.join(file_path, visur + "_Protokoll.md")
        pdf_path = os.path.join(file_path, visur + "_Protokoll.pdf")

        ## Bilder für Protokoll erstellen
        boxplot_path = Path(os.path.join(file_path, visur + "_Boxplot_Höhendifferenz.png"))
        scatterplot_path = Path(os.path.join(file_path, visur + "_Scatterplot_Verteilung_Winkel.png"))

        ax1 = boxplot_beaut(df300_new, visur)
        ax1.figure.savefig(boxplot_path, bbox_inches='tight', dpi=300)

        ax2 = scatterplot_vwinkel(df300_new, visur)
        ax2.figure.savefig(scatterplot_path, bbox_inches='tight', dpi=300)

        ## Bilder im HTML-String hinzufügen
        img_html = f"""
        <div style='margin-top:30px;'>
          <h2 style='text-align:center;'>Visualisierung der Messergebnisse</h2>
          <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
            <div style='width:48%; text-align: center;'>
              <img src="{path_to_file_url(boxplot_path)}" style="max-width:100%; max-height:550px; object-fit: contain;" />
            </div>
            <div style='width:48%; text-align: center;'>
              <img src="{path_to_file_url(scatterplot_path)}" style="max-width:100%; max-height:550px; object-fit: contain;" />
            </div>
          </div>
        </div>
        """

        # Markdown speichern
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(full_md)

        # HTML für WeasyPrint mit Querformat und dynamischen Spalten
        html_text = f"""
        <html>
        <head>
        <style>
        @page {{
            size: A4 landscape;
            margin: 20mm;
            @bottom-left {{
                content: "{visur}_Protokoll.md";
                font-size: 8pt;
            }}
            @bottom-right {{
                content: "Seite " counter(page) " / " counter(pages);
                font-size: 8pt;
            }}
        }}
        body {{
            font-family: Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.4;
        }}
        table {{
            border-collapse: collapse;
            font-size: 8pt; 
        }}
        th, td {{
            padding: 4px 6px;
            border: 1px solid #333;
            text-align: center;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        </style>
        </head>
        <body>
        {markdown.markdown(full_md, extensions=['tables'])}
        {img_html}
        </body>
        </html>
        """

        # PDF erzeugen
        HTML(string=html_text).write_pdf(pdf_path)

    except Exception as e:
        print(f"Fehler beim Exportieren der Protokolldatei: {e}")
