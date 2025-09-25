import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np

def boxplot(df300,infos_height, visur:str):
    """
    Erstellt einen Boxplot der Abweichungen der Höhendifferenzen vom Mittelwert mit Kennzeichnung von Ausreißern.

    Diese Funktion berechnet die Differenz der Höhendaten in `df300` zu einem vorgegebenen Mittelwert
    aus `infos_height`. Anschließend wird ein Boxplot erzeugt, in dem die Abweichungen dargestellt werden.
    Rote Punkte markieren echte Ausreißer basierend auf 1,5 * IQR-Regel, blaue Punkte markieren Werte außerhalb der Box,
    die aber keine echten Ausreißer sind. Die IDs der Messungen sowohl der echten als auch der unechten Ausreißer
    werden als Text unter dem Plot angezeigt.

    Parameter:
    ----------
    df300 : pandas.DataFrame
        DataFrame mit den Messdaten, mindestens mit den Spalten "Höhendiff. [m]" und "ID Messung".
    infos_height : Sequence
        Liste oder Tupel mit verschiedenen Höheninfos, wobei der Mittelwert der Höhenabweichungen unter Index 1 liegt.
    visur : str
        Beschreibung oder Name, der als Titelzusatz im Plot verwendet wird, z.B. zur Visualisierungsspezifikation.

    Rückgabe:
    ---------
    matplotlib.axes.Axes
        Das Achsenobjekt des erstellten Boxplots mit den markierten Ausreißern.

    Beispiel:
    ---------
    ax = boxplot(df300, infos_height, "Beispielvisualisierung")
    """

    # Verbesserungen zum Mittelwert berechnen
    mittelw = infos_height[1]

    verbesserung = df300["Höhendiff. [m]"] - mittelw
    verb_df = pd.DataFrame({"Verbesserung [m]": verbesserung})

    # Boxplot erstellen
    ax = verb_df.boxplot(column="Verbesserung [m]",grid=False, figsize=(6,4))
    ax.set_title(f"Abweichungen vom Mittelwert - {visur}")
    ax.set_ylabel("Δ Höhe [m]")
    ax.set_ylim(-0.05, 0.05)

    # Ausreißer identifizieren und plotten (rot)
    q1 = verb_df["Verbesserung [m]"].quantile(0.25)
    q3 = verb_df["Verbesserung [m]"].quantile(0.75)
    iqr = q3 - q1
    outliers = verb_df[(verb_df["Verbesserung [m]"] < q1 - 1.5*iqr) | 
                       (verb_df["Verbesserung [m]"] > q3 + 1.5*iqr)]
    
    outlier_ids = df300.loc[outliers.index, "ID Messung"].tolist()

    ax.scatter([1]*len(outliers), outliers["Verbesserung [m]"], color='red', zorder=5)

    # Unechte Ausreisser identifizieren und plotten (blau)
    outside_box = verb_df[(verb_df["Verbesserung [m]"] < q1) & (verb_df["Verbesserung [m]"] >= q1 - 1.5*iqr) |
                      (verb_df["Verbesserung [m]"] > q3) & (verb_df["Verbesserung [m]"] <= q3 + 1.5*iqr)]
    outside_ids = df300.loc[outside_box.index, "ID Messung"].tolist()
    ax.scatter([1]*len(outside_box), outside_box["Verbesserung [m]"], color='blue', zorder=4)


    # Ausreisser-IDs als Text unter dem Plot hinzufügen
    if outlier_ids:
        outlier_text = "Rote Ausreisser: " + ", ".join(f"{v:.2f} ({i})" 
                                                 for v, i in zip(outliers["Verbesserung [m]"], outlier_ids))
        ax.text(0.5, -0.15, outlier_text, transform=ax.transAxes, ha='center', va='top', fontsize=9, color='red',wrap=True)
    
    if outside_ids:
        outside_text = "Blaue Ausreisser: " + ", ".join(
        f"{v:.2f} ({i})" for v, i in zip(outside_box["Verbesserung [m]"], outside_ids)
)
        ax.text(0.5, -0.28, outside_text, transform=ax.transAxes, ha='center', va='top', 
            fontsize=9, color='blue', wrap=True)

    return ax

## <<----------------------------------------------------------------------------------------------------------->>

def boxplot_beaut(df300, visur: str):
    """
    Erstellt einen ansprechenden Boxplot der Differenzen der Höhendaten zum Mittelwert in Zentimetern.

    Die Funktion berechnet die Abweichung der Höhendaten in `df300` zur mittleren Höhe aus `infos_height` in cm
    und visualisiert diese als farblich angepassten Boxplot. Rote Punkte markieren starke Ausreißer (1,5*IQR-Regel),
    blaue Punkte leichte Ausreißer (Werte außerhalb der Box, aber innerhalb 1,5*IQR). 
    Unterhalb des Plots werden statistische Kennwerte (Median, Q1, Q3) und eine Tabelle mit IDs und Werten der Ausreißer 
    mit farblich codierter Schrift angezeigt. Dabei ist die Grafik vertikal ausgelegt und nutzt abgestimmte Achsenbeschriftungen.

    Parameter:
    ----------
    df300 : pandas.DataFrame
        DataFrame mit Messdaten, mindestens mit den Spalten "Höhendiff. [m]" und "ID Messung".
    infos_height : Sequence
        Liste oder Tupel mit Höheninformationen, wobei der Mittelwert der Differenzen unter Index 1 liegt.
    visur : str
        Beschriftung bzw. Bezeichner, der als X-Achsen-Beschriftung im Plot verwendet wird.

    Rückgabe:
    ---------
    matplotlib.axes.Axes
        Das Achsenobjekt des erzeugten Boxplots.

    Beispiel:
    ---------
    ax = boxplot_beaut(df300, infos_height, "Visur Nummer 5")
    """
    
    ## <<------------------------------------------------------------------------->>
    ## Verbesserung = Differenz jeder Messung zum Mittelwert
    # mittelw = infos_height[1]
    mittelw = df300["Höhendiff. [m]"].mean()

    verbesserung = (df300["Höhendiff. [m]"] - mittelw) * 100
    verb_df = pd.DataFrame({"Verbesserung [cm]": verbesserung})

    ## <<------------------------------------------------------------------------->>
    ## Grundgerüst des Plotes
    fig, ax = plt.subplots(figsize=(4, 8))

    bp = ax.boxplot(
        verb_df["Verbesserung [cm]"],                                                    # Daten
        patch_artist=True,                                                              # Boxen gefuellt darstellen
        widths=0.6,                                                                     # Breite der Box
        medianprops=dict(color="black", linewidth=1.5),                                 # Medianlinie
        whiskerprops=dict(color="gray", linewidth=1.2),                                 # Whisker
        capprops=dict(color="gray", linewidth=1.2),                                     # Caps
        boxprops=dict(color="gray", linewidth=1.2),                                     # Boxrahmen
        flierprops=dict(marker="o", markersize=5, markerfacecolor="gray", alpha=0.5))   # Standard-Ausreisserpunkte

    ## Farbe der Box
    for patch in bp["boxes"]:
        patch.set_facecolor("#a6cee3")
        patch.set_alpha(0.8)

    # Null-Linie einzeichnen
    ax.axhline(0, color="gray", linestyle="--", linewidth=1)

    # Titel & Achsen
    ax.set_title(f"Diff. zum Mittelwert", fontsize=14, pad=20)
    ax.set_ylabel("Δ Höhe [cm]", fontsize=12)
    ax.set_xticks([1])
    ax.set_xticklabels([f"{visur}"], fontsize=12)
    ax.set_ylim(-10, 10)

    ax.yaxis.set_major_locator(plt.MultipleLocator(1))
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    ## <<------------------------------------------------------------------------->>
    ## Daten auslesen für Ausreisser-Markierung
    q1 = verb_df["Verbesserung [cm]"].quantile(0.25)
    q3 = verb_df["Verbesserung [cm]"].quantile(0.75)
    iqr = q3 - q1

    # "starke" Ausreisser ermitteln (1.5*IQR Regel)
    outliers = verb_df[
        (verb_df["Verbesserung [cm]"] < q1 - 1.5*iqr) |
        (verb_df["Verbesserung [cm]"] > q3 + 1.5*iqr)
    ]
    outlier_ids = df300.loc[outliers.index, "ID Messung"].tolist()

    # "starke" Ausreiser rot markieren
    ax.scatter([1]*len(outliers), outliers["Verbesserung [cm]"], color="red", zorder=5)

    # "leichte" Ausreisser (zwischen Whisker und 1.5*IQR)
    outside_box = verb_df[
        ((verb_df["Verbesserung [cm]"] < q1) & (verb_df["Verbesserung [cm]"] >= q1 - 1.5*iqr)) |
        ((verb_df["Verbesserung [cm]"] > q3) & (verb_df["Verbesserung [cm]"] <= q3 + 1.5*iqr))
    ]
    outside_ids = df300.loc[outside_box.index, "ID Messung"].tolist()

    # "leichte" Ausreisser blau markieren
    ax.scatter([1]*len(outside_box), outside_box["Verbesserung [cm]"], color="blue", zorder=4)

    
    ## <<------------------------------------------------------------------------->>
    ## Daten auslesen für Statistik-Tabelle
    median = verb_df["Verbesserung [cm]"].median()
    mean = verb_df["Verbesserung [cm]"].mean()
    stats_data = [[
        f"Median: {median:.1f} cm",
        f"Q1: {q1:.1f} cm",
        f"Q3: {q3:.1f} cm"
    ]]

    # Neue Achse fuer Kennwerte unterhalb der Tabelle
    stats_ax = fig.add_axes([0.15, -0.06, 0.8, 0.1])
    stats_ax.axis("off")
    stats_ax.table(cellText=stats_data, loc="center", cellLoc="center").scale(1, 1.2)

    ## <<------------------------------------------------------------------------->>
    ## Datentabelle unter dem Boxplot
    # Texte bauen: "ID (Wert m)"
    red_entries = [f"{i} ({v:.1f} cm)" for v, i in zip(outliers["Verbesserung [cm]"], outlier_ids)]
    blue_entries = [f"{i} ({v:.1f} cm)" for v, i in zip(outside_box["Verbesserung [cm]"], outside_ids)]

    # # Alle Eintraege sammeln, mit Farbinfos
    # entries = [(txt, "red") for txt in red_entries] + [(txt, "blue") for txt in blue_entries]

    # Layout: 4 Spalten, so viele Zeilen wie noetig
    ncols = 4
    # nrows = int(np.ceil(len(entries) / ncols))

    # Rote Eintraege
    red_nrows = int(np.ceil(len(red_entries) / ncols))
    red_table_data = [[""]*ncols for _ in range(red_nrows)]
    red_colors = [["black"]*ncols for _ in range(red_nrows)]
    for idx, txt in enumerate(red_entries):
        r, c = divmod(idx, ncols)
        red_table_data[r][c] = txt
        red_colors[r][c] = "red"

    # Blaue Eintraege
    blue_nrows = int(np.ceil(len(blue_entries) / ncols))
    blue_table_data = [[""]*ncols for _ in range(blue_nrows)]
    blue_colors = [["black"]*ncols for _ in range(blue_nrows)]
    for idx, txt in enumerate(blue_entries):
        r, c = divmod(idx, ncols)
        blue_table_data[r][c] = txt
        blue_colors[r][c] = "blue"

    # Gesamttabelle: rote zuerst, dann blaue
    table_data = red_table_data + blue_table_data
    cell_colors = red_colors + blue_colors

    # Achse fuer Tabelle einfuegen (extra kleiner Bereich unterhalb der Grafik)
    tab_ax = fig.add_axes([0.15, -0.13, 0.8, 0.1])
    tab_ax.axis("off")

    # Tabelle erzeugen
    table = tab_ax.table(cellText=table_data, loc="center", cellLoc="center")

    # Farben der Schrift setzen
    for (row, col), cell in table.get_celld().items():
        if row < len(table_data) and col < ncols:
            cell.get_text().set_color(cell_colors[row][col])
            cell.set_fontsize(9)



    # Layout anpassen
    fig.tight_layout()
    plt.close(fig)

    return ax

## <<----------------------------------------------------------------------------------------------------------->>

def scatterplot_vwinkel(df, visur:str, max_streuung:float=0.004):
    """
    Erstellt einen Scatterplot der Vertikalwinkel (V-Winkel) von A nach B und B nach A zentriert um deren Mittelwerte.

    Die Funktion visualisiert die Verteilung der Vertikalwinkel aus dem DataFrame `df` für zwei Richtungen:
    A → B und B → A. Die Winkelwerte werden auf zwei vertikalen Linien bei x=1/3 und x=2/3 geplottet. 
    Die Punkte sind farblich nach der Lage (Spalte "Lage") unterschieden. Zusätzlich werden die Mittelwerte 
    beider Winkel mit roten gestrichelten Linien eingezeichnet. Die y-Achsenbereiche werden um den jeweiligen 
    Mittelwert mit einer einstellbaren maximalen Streuung `max_streuung` gesetzt. Es gibt zwei y-Achsen, 
    um beide Winkel unabhängig zu skaliert darzustellen.

    Parameter:
    ----------
    df : pandas.DataFrame
        DataFrame mit den Messdaten, der die Spalten "V-Winkel A-->B [gon]", "V-Winkel B-->A [gon]" und "Lage" enthalten muss.
    visur : str
        Beschreibung oder Bezeichnung, die im Plottitel genutzt werden kann.
    max_streuung : float, optional (Standard: 0.004)
        Maximale Streuung (plus/minus) um den Mittelwert für die Skalierung der y-Achsen in Gon.

    Rückgabe:
    ---------
    matplotlib.axes.Axes
        Das Achsenobjekt des erstellten Scatterplots (primäre Achse für A→B-Winkel).

    Beispiel:
    ---------
    ax = scatterplot_vwinkel(df300, "Beispielvisur", max_streuung=0.005)
    """

    ## Berechnung der Mittelwerte und Werte
    mean_ab = df["V-Winkel A-->B [gon]"].mean()
    mean_ba = df["V-Winkel B-->A [gon]"].mean()
    value_ab = df["V-Winkel A-->B [gon]"]
    value_ba = df["V-Winkel B-->A [gon]"]

    ## Erstellung der X-Koordinaten für die Y-Koordinatne (=Winkel)
    x_a_b = np.ones(len(df)) * (1 / 3)
    x_b_a = np.ones(len(df)) * (2 / 3)

    ## Farbzuteilung nach Fernrohlage
    colors = df["Lage"].map({"1": "blue", "2": "orange"})

    ## Erstellung des Plotes
    fig, ax1 = plt.subplots(figsize=(8, 8))
    ax2 = ax1.twinx()

    ## Scatterplot für beide Gruppen
    scatter1 = ax1.scatter(x_a_b, 
                           value_ab, 
                           c=colors, 
                           marker='o', 
                           s=80,
                           alpha=0.6, 
                           edgecolors='black', 
                           zorder=3)

    scatter2 = ax2.scatter(x_b_a, 
                           value_ba, 
                           c=colors, 
                           marker='o', 
                           s=80,
                           alpha=0.6, 
                           edgecolors='black',
                           zorder=3)

    ## Mittelwertlinien
    ax1.axhline(mean_ab, color='red', lw=1.8, ls='--', zorder=2)
    ax2.axhline(mean_ba, color='red', lw=1.8, ls='--', zorder=2)

    ## X-Achse einstellen
    ax1.set_xlim(0, 1)
    ax1.set_xticks([(1 / 3), (2 / 3)])
    ax1.set_xticklabels(["A → B", "B → A"], fontsize=14)
    ax1.set_xlabel('')

    ## Y-Ticks einstellen, Um den Mittelwert +/- Streuung
    ab_ticks = np.round(np.arange(mean_ab - max_streuung, mean_ab + max_streuung, 0.001), 5)
    ba_ticks = np.round(np.arange(mean_ba - max_streuung, mean_ba + max_streuung, 0.001), 5)

    ## Min/Max der Y-Achse 
    y_min_ab = ab_ticks[0]
    y_max_ab = ab_ticks[-1]
    y_min_ba = ba_ticks[0]
    y_max_ba = ba_ticks[-1]

    ## Achswerte einstellen
    ax1.set_ylim(y_min_ab, y_max_ab)
    ax1.set_yticks(ab_ticks)
    ax2.set_ylim(y_min_ba, y_max_ba)
    ax2.set_yticks(ba_ticks)

    ## Y-Werte-Beschriftung schräg stellen
    ax1.set_yticklabels([f"{y:.5f} gon" for y in ab_ticks], rotation=45)
    ax2.set_yticklabels([f"{y:.5f} gon" for y in ba_ticks], rotation=-45)

    ## Achsenbeschriftung
    ax1.set_ylabel("V-Winkel A → B [gon]", fontsize=13)
    ax2.set_ylabel("V-Winkel B → A [gon]", fontsize=13)

    ##Beschriftung extra
    # ax1.text(0, mean_ab + 0.0001, "+0,1 mgon", fontsize=11, color='green', ha='center', rotation=22)
    # ax1.text(0, mean_ab - 0.0001, "-0,1 mgon", fontsize=11, color='green', ha='center', rotation=22)
    # ax1.text(1, mean_ba + 0.0001, "+0,1 mgon", fontsize=11, color='green', ha='center', rotation=-22)
    # ax1.text(1, mean_ba - 0.0001, "-0,1 mgon", fontsize=11, color='green', ha='center', rotation=-22)

    ## Mittelwert Rot
    # ax1.text(-0.01, mean_ab, f"Ø {mean_ab:.5f} gon", fontsize=10, color='red', rotation=45, va='center', ha='right')
    # ax1.text(0.92, mean_ba, f"Ø {mean_ba:.5f} gon", fontsize=12, color='red', rotation=0, va='center', ha='left')

    ## Raster
    for t in ab_ticks:
        ax1.axhline(t, color='green', lw=0.8, ls='--', alpha=0.7, zorder=1)

    ## Vertikalline in der Mitte
    ax1.axvline(0.5, color='grey', lw=1.2, ls=':', alpha=0.5)

    ## Legende farblich nach Gruppen
    blue_patch = mpatches.Patch(color='blue', label='Lage 1')
    orange_patch = mpatches.Patch(color='orange', label='Lage 2')
    plt.legend(handles=[blue_patch, orange_patch], loc="upper left")

    ## Setze des Titels

    plt.suptitle(f"Winkel zentriert um den jeweiligen Mittelwert. \nPro Rastereinheit entsteht ein Abstand vom 0.1 mgon (Streuung: ±{max_streuung*100} mgon)", fontsize=12, y=-0.01)
    plt.title(f"Streuung der Vertikalwinkel -- {visur}", fontsize=16, pad=16)
    # ax1.set_title(f"Streuung der Vertikalwinkel\n--- zentriert um den jeweiligen Mittelwert ---\nEinheit pro Raster: 0.1 mgon (Max: ±{max_streuung*100} mgon) ---\nVisurnummer {visurnummer}", fontsize=15, pad=16)
    # ax1.set_title("hallo")

    fig.tight_layout()
    plt.close(fig)
    
    return ax1