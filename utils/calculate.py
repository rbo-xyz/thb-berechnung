import numpy as np
import pandas as pd

## << ----------------------------------------------------------------------------------- >>
## << ----------------------------------------------------------------------------------- >>

## Winkelfunktionen
def gon2rad(gon):
    """
    Wandelt einen Winkel von Gon in Radiant um.

    Parameters
    ----------
    gon : float
        Winkel im Gon.

    Returns
    -------
    float
        Winkel im Radiant.
    """
    return gon * np.pi / 200.0

def rad2gon(rad):
    """
    Wandelt einen Winkel von Radiant in Gon um.

    Parameters
    ----------
    rad : float
        Winkel im Radiant.

    Returns
    -------
    float
        Winkel im Gon.
    """
    return rad * 200.0 / np.pi

def rho():
    """
    Liefert den Umrechnungsfaktor von Gon in Radiant.

    Returns
    -------
    float
        Umrechnungsfaktor (π / 200).
    """
    return np.pi / 200

## << ----------------------------------------------------------------------------------- >>
## << ----------------------------------------------------------------------------------- >>

## Masterfunktion THB
def master_thb(df100, 
               df200, 
               df_aprox, 
               signal_A:float, 
               signal_B:float, 
               offset_A:float, 
               offset_B:float):
    """
    Führt die komplette Trigonometrische Höhenbestimmung (THB) aus und gibt ein zusammengeführtes Ergebnis-DataFrame
    sowie wichtige Kennwerte der Messung zurück.

    Die Funktion:
    - Filtert Start- und Endpunkte aus den Messdaten
    - Berechnet vorläufige Azimute
    - Korrigiert V-Winkel bei zweilagigen Messungen
    - Berücksichtigt Lotabweichungen und Kippachsenkorrekturen
    - Berechnet mittlere Schrägdistanz, Höhendifferenz und Refraktionskoeffizient
    - Bereitet das Ergebnis-DataFrame für die Ausgabe auf

    Parameters
    ----------
    df100 : pandas.DataFrame
        Messdaten der ersten Messung.
    df200 : pandas.DataFrame
        Messdaten der zweiten Messung.
    df_aprox : pandas.DataFrame
        Näherungskoordinaten zur Bestimmung von Azimut und Lotabweichungen.
    signal_A : float
        Höhe des Prismas am Punkt A.
    signal_B : float
        Höhe des Prismas am Punkt B.
    offset_A : float
        Instrumenten-Offset am Punkt A.
    offset_B : float
        Instrumenten-Offset am Punkt B.

    Returns
    -------
    df300 : pandas.DataFrame
        Zusammengeführtes Ergebnis-DataFrame mit den Spalten:
        - "ID Messung"  
        - "Schrägdistanz A --> B [m]"  
        - "Schrägdistanz B --> A [m]"  
        - "Mittlere Schrägdistanz [m]"  
        - "Höhendifferenz [m]"  
        - "Refraktionskoeffizient k"  

    infos : list of float/str
        Wichtige Kennwerte der Messung:
        - infos[0] : Startpunkt Nr. A
        - infos[1] : Endpunkt Nr. B
        - infos[2] : Höhendifferenz aus Näherungskoordinaten
        - infos[3] : Mittlere Höhendifferenz über Messung
        - infos[4] : Standardabweichung der Höhendifferenz
        - infos[5] : Mittlerer Refraktionskoeffizient k
        - infos[6] : Standardabweichung von k
        - infos[7] : Mittlere Schrägdistanz
        - infos[8] : Standardabweichung der Schrägdistanz
    """

    ### Filtern der Messdaten
    ## <-----------------------------------------------------------------------------------> 
    ## Filtern des Start und Endpunktes aus den ersten Messdaten
    start100 = df100["Standpkt"].values[0]
    end100 = df100["Zielpkt"].values[0]
    df100_start = df_aprox[df_aprox["PktNr"] == start100]
    df100_target = df_aprox[(df_aprox["PktNr"] == end100)]

    ## Filtern des Start und Endpunktes aus den zweiten Messdaten
    start200 = df200["Standpkt"].values[0]
    end200 = df200["Zielpkt"].values[0]
    df200_start = df_aprox[(df_aprox["PktNr"] == start200)]
    df200_target = df_aprox[(df_aprox["PktNr"] == end200)]

    ## Bestimmung des Azimutes für die jeweiligen Messfiles
    azi100 = azi_aprox(df100_start, df100_target)
    azi200 = azi_aprox(df200_start, df200_target)
    ## <-----------------------------------------------------------------------------------> 


    ### Korrektur der 2-lagigen Messung (V-Winkel Anpassen)
    ## <-----------------------------------------------------------------------------------> 
    df100.loc[df100["Lage"] == 2, "V-Winkel"] = 400 - df100["V-Winkel"]
    df200.loc[df200["Lage"] == 2, "V-Winkel"] = 400 - df200["V-Winkel"]
    ## <-----------------------------------------------------------------------------------> 


    ### Korrektur der Lotabweichung
    ## <----------------------------------------------------------------------------------->
    ## Auswahl der Lotkorekturen aus den Näherungskoordinaten
    xi_100 = df100_start["Xi"].values[0]
    eta_100 = df100_start["Eta"].values[0]

    xi_200 = df200_start["Xi"].values[0]
    eta_200 = df200_start["Eta"].values[0]

    df100["V-Winkel_korr"] = korr_lotabw(xi_100, eta_100, azi100, df100["V-Winkel"].values)
    df200["V-Winkel_korr"] = korr_lotabw(xi_200, eta_200, azi200, df200["V-Winkel"].values)
    ## <----------------------------------------------------------------------------------->


    ### Korrektur der Kippachse
    ## <----------------------------------------------------------------------------------->
    df100["Ds_Korrigiert"] , df100["V-Winkel_Korrigiert"] = korr_kippachse(df100["Ds"].values, offset_A, df100["V-Winkel_korr"].values)
    df200["Ds_Korrigiert"] , df200["V-Winkel_Korrigiert"] = korr_kippachse(df200["Ds"].values, offset_B, df200["V-Winkel_korr"].values)

    col2drop = ["Datum", "Lage", "Uhrzeit", "Standpkt", "Zielpkt", 
                "V-Winkel", "V-Winkel_korr", "Ds", "Hz-Winkel"]

    df100 = df100.drop(col2drop, axis=1, errors="ignore")
    df200 = df200.drop(col2drop, axis=1, errors="ignore")
    ## <----------------------------------------------------------------------------------->


    ### Vorbereiten des dfs für die Berechnung der Höhendifferenz
    ## <----------------------------------------------------------------------------------->
    df100 = df100.rename(columns={"Ds_Korrigiert" : "Ds-A2B",
                                  "V-Winkel_Korrigiert" : "V-Winkel-A2B"})
    
    df200 = df200.rename(columns={"Ds_Korrigiert" : "Ds-B2A",
                                  "V-Winkel_Korrigiert" : "V-Winkel-B2A"})
    
    df300 = pd.merge(df100, df200, on="ID", how="outer")

    df300["Ds-Mittel"] = 0.5 * (df300["Ds-A2B"] + df300["Ds-B2A"])

    df300 = df300.loc[:, ["ID", "Ds-A2B", "Ds-B2A", "Ds-Mittel", "V-Winkel-A2B", "V-Winkel-B2A"]]
    ## <----------------------------------------------------------------------------------->


    ### Berechnung der Höhendifferenz
    ## <----------------------------------------------------------------------------------->
    ## Berechnung der Höhendiferenz
    instrument_A = signal_A - offset_A
    instrument_B = signal_B - offset_B

    df300["delta_H"] = delta_h(df300["Ds-Mittel"].values,
                               df300["V-Winkel-A2B"].values,
                               df300["V-Winkel-B2A"].values,
                               instrument_A,
                               instrument_B,
                               signal_A,
                               signal_B)
    ## <----------------------------------------------------------------------------------->


    ### Berechnung der Refraktionskoefizienten
    ## <----------------------------------------------------------------------------------->
    df300["k"] = refraktion(df300["Ds-Mittel"].values,
                            df300["V-Winkel-A2B"].values,
                            df300["V-Winkel-B2A"].values)
    ## <----------------------------------------------------------------------------------->


    ### Vorbereiten des df für die Ausgabe
    ## <----------------------------------------------------------------------------------->
    col2drop = ["V-Winkel-A2B", "V-Winkel-B2A"]
    df300 = df300.drop(col2drop, axis=1, errors="ignore")
    df300 = df300.round({"Ds-A2B":4, "Ds-B2A":4, "Ds-Mittel":4, "delta_H":4, "k":2})

    df300 = df300.rename(columns={"ID" : "ID Messung",
                                  "Ds-A2B" : "Schrägdistanz A -- > B [m]",
                                  "Ds-B2A" : "Schrägdistanz B -- > A [m]",
                                  "Ds-Mittel" : "Mittlere Schrägdistanz [m]",
                                  "delta_H" : "Höhendifferenz [m]",
                                  "k" : "Refraktionskoeffizient k"})

    pktNr_A = start100
    pktNr_B = end100
    delta_h_aprox = round(np.abs(df100_target["Hoehe"].values[0] - df100_start["Hoehe"].values[0]),2)

    mean_delta_h = round(df300["Höhendifferenz [m]"].mean(), 5)
    std_delta_h = round(df300["Höhendifferenz [m]"].std(), 5)

    mean_k = round(df300["Refraktionskoeffizient k"].mean(), 5)
    std_k = round(df300["Refraktionskoeffizient k"].std(), 5)

    meand_sd = round(df300["Mittlere Schrägdistanz [m]"].mean(), 5)
    std_sd = round(df300["Mittlere Schrägdistanz [m]"].std(), 5)

    infos = [pktNr_A, pktNr_B, float(delta_h_aprox), float(mean_delta_h), float(std_delta_h), 
             float(mean_k), float(std_k), float(meand_sd), float(std_sd)]

    ## <----------------------------------------------------------------------------------->

    return df300, infos

## << ----------------------------------------------------------------------------------- >>
## << ----------------------------------------------------------------------------------- >>


## SubFunctions THB
## <----------------------------------------------------------------------------------->

def korr_lotabw(xi: float, eta: float, azi: float, v_angle: float):
    """
    Berechnet die korrigierte Vertikalwinkelmessung unter Berücksichtigung der Lotabweichung.

    Die Funktion korrigiert einen gemessenen Vertikalwinkel `v_angle` um die Lotabweichung 
    in Längsrichtung, basierend auf den Korrekturwerten `xi` und `eta` und dem Azimut `azi`.

    Parameters
    ----------
    xi : float
        Korrekturwert in X-Richtung (in cc, 1cc = 0.1 mgon).
    eta : float
        Korrekturwert in Y-Richtung (in cc, 1cc = 0.1 mgon).
    azi : float
        Azimutwinkel des Messpunkts (in gon).
    v_angle : float
        Gemessener Vertikalwinkel (in gon).

    Returns
    -------
    float
        Korrigierter Vertikalwinkel in gon.

    Notes
    -----
    - Intern werden die Winkel von gon in Radiant umgerechnet.
    - xi und eta werden von cc (1cc = 0.1 mgon) in Radiant umgerechnet.
    - Die Lotabweichung in Längsrichtung wird berechnet und auf den Vertikalwinkel angewendet.
    - Ergebnis wird wieder von Radiant in gon zurückkonvertiert.
    """

    ## Umwandlung der Winkel von gon in rad
    v_angle = gon2rad(v_angle)
    azi = gon2rad(azi)

    # xi und eta umrechnen von cc (1cc = 0.1mgon) in rad
    xi = (xi / 10000) /200 * np.pi
    eta = (eta / 10000) /200 * np.pi

    # Berechnung der Lotabweichung in laengsrichtung aus xi und eta
    theta_v = xi * np.cos(azi) + eta * np.sin(azi)

    # Korrektur des Azimuts um Theta laengs
    v_angle_korr = v_angle + theta_v

    ## Umwandlung Winkel von rad in gon
    v_angle_korr = rad2gon(v_angle_korr)

    return v_angle_korr

## <----------------------------------------------------------------------------------->

def korr_kippachse(dist_ab: float, offset_b: float, v_angle_korr: float):
    """
    Korrigiert die Distanz und den Vertikalwinkel aufgrund einer Kippachse am Prismamount.

    Die Funktion berechnet die korrigierte Distanz `dist_korr` und den
    korrigierten Vertikalwinkel `v_angle_korr_korr`, wenn der Prismahalter
    eine bestimmte Achse (Kippachse) hat. Dabei wird der Kosinussatz verwendet.

    Parameters
    ----------
    dist_ab : float
        Gemessene Distanz zwischen Messpunkt A und B (in Meter).
    offset_b : float
        Versatz des Prismamounts in Richtung der Kippachse (in Meter).
    v_angle_korr : float
        Vertikalwinkel nach vorheriger Lotabweichungskorrektur (in gon).

    Returns
    -------
    list of float
        [dist_korr, v_angle_korr_korr]
        - dist_korr : Korrigierte Distanz unter Berücksichtigung des Prismamount-Versatzes (in Meter)
        - v_angle_korr_korr : Vertikalwinkel nach Korrektur um den Winkel Beta (in gon)

    Notes
    -----
    - Winkel werden intern von gon in Radiant umgerechnet.
    - Die Korrektur erfolgt über den Kosinussatz und die Berechnung des Winkels Beta.
    - Das Ergebnis enthält die neue Distanz und den um Beta korrigierten Vertikalwinkel.
    """

    ## Umwandlung der Winkel von gon in rad
    v_angle_korr = gon2rad(v_angle_korr)

    # Berechnung der korrigierten Distanz aufgrund des speziellen Prismamounts (mit cosinussatz)
    dist_korr = np.sqrt(offset_b**2 + dist_ab**2 - (2*offset_b*dist_ab) * np.cos(v_angle_korr)) 

    # Berechnung des Winkels Beta zwischen der gemessenen Distanz und der Korrekturdistanz
    beta_ab = np.arccos((dist_ab**2 + dist_korr**2 - offset_b**2) / (2 * dist_ab * dist_korr)) 

    # Korrektur des Vertikalwinkels um Beta
    v_angle_korr_korr = v_angle_korr + beta_ab

    ## Umwandlung Winkel von rad in gon
    v_angle_korr_korr = rad2gon(v_angle_korr_korr)

    return [dist_korr, v_angle_korr_korr]

## <----------------------------------------------------------------------------------->

def delta_h(mittel_dist:float,
            v_angle_korr_korr_ab:float,
            v_angle_korr_korr_ba:float, 
            instr_height_a:float, 
            instr_height_b:float, 
            signal_height_a:float, 
            signal_height_b:float):
    """
    Berechnet die Höhendifferenz zwischen zwei Punkten aus doppelseitigen Vertikalwinkelmessungen.

    Die Funktion nutzt die korrigierten Vertikalwinkel in beiden Richtungen (AB und BA),
    die mittlere Distanz zwischen den Punkten sowie Instrument- und Signalhöhen, um die
    absolute Höhendifferenz delta_h zu bestimmen.

    Parameters
    ----------
    mittel_dist : float
        Mittlere Schrägdistanz zwischen den Punkten A und B (in Meter).
    v_angle_korr_korr_ab : float
        Vertikalwinkel von A nach B, bereits um Lotabweichung und Kippachse korrigiert (in gon).
    v_angle_korr_korr_ba : float
        Vertikalwinkel von B nach A, bereits um Lotabweichung und Kippachse korrigiert (in gon).
    instr_height_a : float
        Instrumenthöhe am Punkt A (in Meter).
    instr_height_b : float
        Instrumenthöhe am Punkt B (in Meter).
    signal_height_a : float
        Signalhöhe am Punkt A (in Meter).
    signal_height_b : float
        Signalhöhe am Punkt B (in Meter).

    Returns
    -------
    float
        Absolute Höhendifferenz zwischen Punkt A und B (in Meter).

    Notes
    -----
    - Die Vertikalwinkel werden intern von gon in Radiant umgerechnet.
    - Berechnung erfolgt gemäß der doppelseitigen Höhenbestimmung:
      delta_h = 0.5 * (mittel_dist * (sin(π/2 - v_angle_AB) - sin(π/2 - v_angle_BA))
                        + (instr_height_a - instr_height_b)
                        + (signal_height_a - signal_height_b))
    - Ergebnis wird als positiver Wert (absolut) zurückgegeben.
    """


    ## Umwandlung der Winkel von gon in rad
    v_angle_korr_korr_ab = gon2rad(v_angle_korr_korr_ab)
    v_angle_korr_korr_ba = gon2rad(v_angle_korr_korr_ba)

    # Berechnung der Höhendifferenz
    delta_h = 0.5 * (mittel_dist * ( np.sin((np.pi/2)-v_angle_korr_korr_ab) - np.sin((np.pi/2)-v_angle_korr_korr_ba)) + (instr_height_a-instr_height_b) + (signal_height_a-signal_height_b))

    return np.abs(delta_h)

## <----------------------------------------------------------------------------------->

def refraktion(mittel_dist:float, 
               v_angle_korr_korr_ab:float, 
               v_angle_korr_korr_ba:float):
    """
    Berechnet den Refraktionskoeffizienten zwischen zwei Punkten auf Basis doppelseitiger Vertikalwinkelmessungen.

    Die Funktion verwendet die korrigierten Vertikalwinkel von A nach B und B nach A sowie
    die mittlere Distanz zwischen den Punkten, um den Refraktionskoeffizienten k zu bestimmen.
    Der Refraktionskoeffizient beschreibt die atmosphärische Beeinflussung der gemessenen Höhendifferenz.

    Parameters
    ----------
    mittel_dist : float
        Mittlere Schrägdistanz zwischen den Punkten A und B (in Meter).
    delta_h : float
        Gemessene Höhendifferenz zwischen Punkt A und B (in Meter).
    v_angle_korr_korr_ab : float
        Vertikalwinkel von A nach B, bereits um Lotabweichung und Kippachse korrigiert (in gon).
    v_angle_korr_korr_ba : float
        Vertikalwinkel von B nach A, bereits um Lotabweichung und Kippachse korrigiert (in gon).

    Returns
    -------
    float
        Refraktionskoeffizient k (dimensionslos).

    Notes
    -----
    - Die Vertikalwinkel werden intern von gon in Radiant umgerechnet.
    - Berechnung erfolgt nach der Formel:
      k = 1 - ((v_angle_AB + v_angle_BA - π) * 6_370_000 / (mittel_dist * sin(v_angle_AB)))
      wobei 6_370_000 m als mittlerer Erdradius verwendet wird.
    """

    ## Umwandlung der Winkel von gon in rad
    v_angle_korr_korr_ab = gon2rad(v_angle_korr_korr_ab)
    v_angle_korr_korr_ba = gon2rad(v_angle_korr_korr_ba)

    # Berechnung des Refraktionskoeffizienten
    k = 1 - ( (v_angle_korr_korr_ab + v_angle_korr_korr_ba - np.pi) * 6_370_000 / (mittel_dist * np.sin(v_angle_korr_korr_ab) )) 

    return k

## <----------------------------------------------------------------------------------->

def cool():
    """
    Gibt einen humorvollen Text über die Programmier- und GeoSensorikfähigkeiten zurück.

    Returns
    -------
    str
        Ein lustiger Satz

    Notes
    -----
    - Diese Funktion hat keine Eingabeparameter.
    - Dient nur zur Unterhaltung oder Demonstration.
    """
    return f"de boppi und de michi sind absoluti programmiermaschine und GeoSensorikgötter"

## <----------------------------------------------------------------------------------->

def azi_aprox(df_start, df_end):
    """
    Berechnet eine ungefähre Azimutrichtung zwischen zwei Punkten auf Basis ihrer Koordinaten.

    Die Funktion nimmt Start- und End-DataFrames mit Koordinatenwerten und berechnet
    den Azimut von Start nach Endpunkt. Negative Azimute werden auf den Bereich 0–400 gon angepasst.

    Parameters
    ----------
    df_start : pandas.DataFrame
        DataFrame des Startpunkts, muss mindestens die Spalte "E-Koord" und "N-Koord" enthalten.
    df_end : pandas.DataFrame
        DataFrame des Endpunkts, muss mindestens die Spalte "E-Koord" und "N-Koord" enthalten.

    Returns
    -------
    float
        Berechneter Azimut in gon (0–400 gon) als einzelner Wert.

    Notes
    -----
    - Berechnung erfolgt über arctan2 der Differenzen der Koordinaten.
    - Negative Werte werden durch Addition von 400 gon korrigiert, um den Standardbereich zu gewährleisten.
    - `rho()` wird als Umrechnungsfaktor von Radiant in gon verwendet.
    """

    ## Auswahl der Koordinaten aus den dfs
    E1 = df_start["E-Koord"].values[0]
    N1 = df_start['N-Koord'].values[0]
    E2 = df_end['E-Koord'].values[0]
    N2 = df_end['N-Koord'].values[0]

    ## Berechnung des Azimutes inklusive Fehlerbaehandlung
    azi_prov = np.arctan2(E2 -E1, N2 - N1) / rho()
    azimuth = np.where(azi_prov > 0, azi_prov, azi_prov + 400)

    return azimuth

## <----------------------------------------------------------------------------------->