import pandas as pd

def boxplot(df300,infos_height, visur:str):
    """
    Erstellt einen Boxplot der Abweichungen einzelner Höhenunterschiede
    vom Mittelwert, um die Streuung der Messungen zu visualisieren.

    Parameter
    ----------
    df300 : pandas.DataFrame
        DataFrame, das die Spalte "Höhendiff. [m]" enthält. 
        Diese Spalte beinhaltet die gemessenen Höhenunterschiede.

    infos_height : array-ähnlich (z. B. pandas.Series oder numpy.ndarray)
        Sammlung mit statistischen Kennwerten. Der Mittelwert der Höhen-
        unterschiede wird an Index [1] erwartet.

    visur : str
        Zusatztext, der im Titel des Boxplots erscheint (z. B. Name des Modells 
        oder der Messreihe).

    Rückgabewert
    ------------
    matplotlib.axes._axes.Axes
        Das Achsen-Objekt des erstellten Boxplots. 
        Kann weiter bearbeitet oder angezeigt werden.

    Beschreibung
    ------------
    - Berechnet die Abweichung jedes Höhenunterschieds zum Mittelwert.
    - Erstellt daraus einen Boxplot.
    - Der Plot zeigt die Streuung der Werte um den Mittelwert (Median nahe 0).
    - Die Y-Achse ist als "Δ Höhe [m]" beschriftet, der Titel enthält 
      den Zusatz `visur`.

    Beispiel
    --------
    >>> ax = boxplot(df300, infos_height, "Messreihe A")
    >>> ax.figure.show()
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