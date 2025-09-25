from utils.imports import import_csv, import_fix
from utils.calculate import master_thb
from utils.exports import export_protocol, export2csv, export_protocol_md_pdf

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def auto_auswertung2025(index:int,
                        base_path,
                        InstrHoehe:str,
                        fix:str
                        ):

    ## <----------------------------------------------------------------------------------->
    ## Erstellung der Pfadliste zu den unterschiedlichen Daten (Props an ChatGPT)
    # Basis-Pfad als Path-Objekt
    csv_first = []
    csv_second = []
    parent_folders = []
    folder_paths = []

    # Iteriere über alle Unterordner
    for folder in sorted([f for f in base_path.iterdir() if f.is_dir()]):
        
        ## Ignoriere den Ordner "_all-data"
        if folder.name == "_all-data":
            continue

        csv_files = sorted([f for f in folder.glob("*.csv")])

        if len(csv_files) >= 2:
            csv_first.append(str(csv_files[0]))
            csv_second.append(str(csv_files[1]))
            parent_folders.append(folder.name)       # Ordnername
            folder_paths.append(str(folder))         # Pfad des Ordners
        else:
            print(f"Warnung: Weniger als 2 CSV-Dateien in {folder.name}")

    ## <----------------------------------------------------------------------------------->
    ## Setze die Liste zum aktuellen index
    mess1_A2B = csv_first[index]
    mess2_B2A = csv_second[index]

    path_protokoll = folder_paths[index]
    visurnummer = parent_folders[index]
    ## <----------------------------------------------------------------------------------->

    # ## Prüfung der Visurnummer und Ausgabe
    # max_index = len(csv_first)-1
    # print(f"Es wurden {max_index+1} Visuren gefunden. // Der Range der Indizies sind 0 bis {max_index}.")
    # print(f"Verarbeite Visur: {visurnummer}")

    ## <----------------------------------------------------------------------------------->
    ## Import der Instrumentenparameter und als Parameter setzen
    df001 = pd.read_csv(InstrHoehe, delimiter=";", encoding="mbcs")

    df001_new = df001[df001["Nr"] == index]

    signalhoehe_A = df001_new["signal_A"].values[0]
    offset_A = df001_new["offset_A"].values[0]
    signalhoehe_B = df001_new["signal_B"].values[0]
    offset_B = df001_new["offset_B"].values[0]

    data = [signalhoehe_A, offset_A, signalhoehe_B, offset_B]
    ## <----------------------------------------------------------------------------------->

    # string_ausgabe = f"""
    # Signalhöhe A: {signalhoehe_A} m
    # Offset A: {offset_A} m
    # Signalhöhe B: {signalhoehe_B} m
    # Offset B: {offset_B} m
    # """

    # print(string_ausgabe)

    ## <----------------------------------------------------------------------------------->
    ## Berechnungen
    ## Import der ersten csv-Datei mit den Messdaten
    df100 = import_csv(mess1_A2B)

    ## Import der zweiten csv-Datei mit den Messdaten
    df200 = import_csv(mess2_B2A)

    ## Import der Näherungskoordinaten
    df_aprox = import_fix(fix)

    ## Höhenberechnung
    df300_new, infos_vis, infos_height, infos_k, infos_sd = master_thb(df100, 
                                                                       df200, 
                                                                       df_aprox, 
                                                                       signalhoehe_A, 
                                                                       signalhoehe_B, 
                                                                       offset_A, offset_B)
    
    ## <----------------------------------------------------------------------------------->

    # ## Test des dfs
    # print(df300_new)

    ## Export der Protokolldatei
    export_protocol(df300_new,
                    infos_vis, 
                    infos_height, 
                    infos_k, 
                    infos_sd, 
                    visurnummer, 
                    path_protokoll, 
                    data)
    ## <----------------------------------------------------------------------------------->

    ## Export der csv-Datei
    export2csv(df300_new,
               infos_vis, 
               infos_height, 
               infos_k, 
               infos_sd, 
               visurnummer, 
               path_protokoll, 
               data)
    ## <----------------------------------------------------------------------------------->

    ## Export der Protokolldatei als md und pdf
    export_protocol_md_pdf(df300_new,
                           infos_vis, 
                           infos_height, 
                           infos_k, 
                           infos_sd, 
                           visurnummer, 
                           path_protokoll, 
                           data)
    ## <----------------------------------------------------------------------------------->

    return df300_new, visurnummer


def img_paths(base_path):
    imgs_scatter = []
    imgs_boxplot = []

    # Iteriere über alle Unterordner
    for folder in sorted([f for f in base_path.iterdir() if f.is_dir()]):

        ## Ignoriere den Ordner "_all-data"
        if folder.name == "_all-data":
            continue
        img_boxplot = sorted([f for f in folder.glob("*Boxplot_Höhendifferenz.png")])
        img_scatter = sorted([f for f in folder.glob("*Scatterplot_Verteilung_Winkel.png")])

        imgs_boxplot.extend(img_boxplot)
        imgs_scatter.extend(img_scatter)

    return imgs_scatter, imgs_boxplot


import matplotlib.pyplot as plt

def save_image_grid(image_paths, output_path, cols=4, figsize_per_image=(4,4)):
    n = len(image_paths)
    rows = (n + cols - 1) // cols

    fig, axs = plt.subplots(rows, cols, figsize=(figsize_per_image[0]*cols, figsize_per_image[1]*rows))
    axs = axs.flatten()

    for ax in axs[n:]:
        fig.delaxes(ax)

    for i, img_path in enumerate(image_paths):
        img = plt.imread(str(img_path))
        axs[i].imshow(img)
        axs[i].axis('off')  # Keine Achsen anzeigen

    plt.tight_layout()
    fig.savefig(output_path, bbox_inches='tight')
    plt.close(fig)

