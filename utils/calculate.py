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
    Führt die vollständige trigonometrische Höhenbestimmung zwischen zwei Punkten durch.

    Die Funktion verarbeitet zwei Messdatensätze (df100, df200) sowie Näherungskoordinaten (df_aprox),
    korrigiert Lotabweichungen und Kippachse, berechnet mittlere Schrägdistanz, Höhendifferenz
    und Refraktionskoeffizient und erstellt ein bereinigtes DataFrame mit den Ergebnissen.
    Zusätzlich werden Präanalysekomponenten für eine Genauigkeitsschätzung ermittelt.

    Verarbeitungsschritte:
    ---------------------
    1. Filtern von Start- und Endpunkten aus den Messdaten.
    2. Berechnung der Azimute für beide Messungen.
    3. Anpassung der V-Winkel für 2-lagige Messungen.
    4. Korrektur der Lotabweichungen anhand der Näherungskoordinaten.
    5. Korrektur der Kippachse mit Prismamount-Offsets.
    6. Berechnung der mittleren Schrägdistanz.
    7. Berechnung der Höhendifferenz zwischen den Punkten.
    8. Berechnung der Refraktionskoeffizienten.
    9. Rundung, Spaltenbereinigung und Umbenennung für die Ausgabe.
    10. Berechnung von Präanalysekomponenten zur Genauigkeitsschätzung.

    Parameter:
    ----------
    df100 : pandas.DataFrame
        Messdatensatz der ersten Messreihe (Spalten u.a. 'Standpkt', 'Zielpkt', 'V-Winkel', 'Ds', 'Lage').
    df200 : pandas.DataFrame
        Messdatensatz der zweiten Messreihe.
    df_aprox : pandas.DataFrame
        Näherungskoordinaten der Messpunkte (Spalten 'PktNr', 'Xi', 'Eta', 'Hoehe').
    signal_A : float
        Signalhöhe an Station A [m].
    signal_B : float
        Signalhöhe an Station B [m].
    offset_A : float
        Instrumentenoffset an Station A [m].
    offset_B : float
        Instrumentenoffset an Station B [m].

    Rückgabe:
    ---------
    df300 : pandas.DataFrame
        Bereinigtes DataFrame mit den Spalten:
        ['ID Visur', 'ID Messung', 'Lage', "d' (schräg) A-->B [m]", "d' (schräg) B-->A [m]",
         "d' (mittel, schräg) [m]", 'V-Winkel A-->B [gon]', 'V-Winkel B-->A [gon]',
         'Höhendiff. [m]', 'Refraktionskoeff. k'].
    infos_vis : list
        [Startpunkt, Endpunkt, Genauigkeit Präanalyse, Präanalyse-Komponenten [d_komp, z_komp, k_komp, i_komp, s_komp]]
    infos_height : list
        Statistische Kennwerte der Höhendifferenz: [delta_h_aprox, mean_delta_h, std_delta_h,
        mean_delta_h_lage1, std_delta_h_lage1, mean_delta_h_lage2, std_delta_h_lage2].
    infos_k : list
        Statistische Kennwerte der Refraktionskoeffizienten: [mean_k, std_k,
        mean_k_lage1, std_k_lage1, mean_k_lage2, std_k_lage2].
    infos_sd : list
        Statistische Kennwerte der mittleren Schrägdistanz: [mean_sd, std_sd,
        mean_sd_lage1, std_sd_lage1, mean_sd_lage2, std_sd_lage2].
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
    df100.loc[df100["Lage"] == "2", "V-Winkel"] = 400 - df100["V-Winkel"]
    df200.loc[df200["Lage"] == "2", "V-Winkel"] = 400 - df200["V-Winkel"]
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
    df100["Ds_Korrigiert"] , df100["V-Winkel_Korrigiert"] = korr_kippachse(df100["Ds"].values, offset_B, df100["V-Winkel_korr"].values)
    df200["Ds_Korrigiert"] , df200["V-Winkel_Korrigiert"] = korr_kippachse(df200["Ds"].values, offset_A, df200["V-Winkel_korr"].values)

    col2drop = ["Datum", "Uhrzeit", "Standpkt", "Zielpkt", 
                "V-Winkel", "V-Winkel_korr", "Ds", "Hz-Winkel"]

    df100 = df100.drop(col2drop, axis=1, errors="ignore")
    df200 = df200.drop(col2drop, axis=1, errors="ignore")
    ## <----------------------------------------------------------------------------------->


    ### Vorbereiten des dfs für die Berechnung der Höhendifferenz
    ## <----------------------------------------------------------------------------------->
    df100 = df100.rename(columns={"Ds_Korrigiert" : "Ds-A2B",
                                  "V-Winkel_Korrigiert" : "V-Winkel-A2B",
                                  "Lage" : "Lage-A2B"})
    
    df200 = df200.rename(columns={"Ds_Korrigiert" : "Ds-B2A",
                                  "V-Winkel_Korrigiert" : "V-Winkel-B2A",
                                  "Lage" : "Lage-B2A"})

    df300 = pd.merge(df100, df200, on="ID", how="outer")

    df300["Ds-Mittel"] = 0.5 * (df300["Ds-A2B"] + df300["Ds-B2A"])

    df300["Lage"] = np.where(df300["Lage-A2B"] == df300["Lage-B2A"],
                             df300["Lage-A2B"],
                             "FEHLER")

    df300 = df300.loc[:, ["ID", "Lage", "Ds-A2B", "Ds-B2A", "Ds-Mittel", "V-Winkel-A2B", "V-Winkel-B2A"]]
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

    # Werte für Präanalyse / vor Spaltenlöschung
    dist_h_m = df300["Ds-A2B"].values[0] * np.sin(df300["V-Winkel-A2B"].values[0] * rho())
    dist_s_mm = df300["Ds-A2B"].values[0] * 1000

    d_komp = np.cos(df300["V-Winkel-A2B"].values[0] * rho()) * (0.6 + (dist_s_mm/1000000))
    z_komp = (np.sin(df300["V-Winkel-A2B"].values[0] * rho()) * dist_s_mm) * (0.15/1000)/200*np.pi
    ## k-komponente kann bei gleichzeitig gegenseiteger Messung vernachlässigt werden
    k_komp = (-1 * ( (dist_h_m)**2 / (2 * 6_370_000) ) * 0.06 ) * 1000
    i_komp = 1
    s_komp = 1


    # col2drop = ["V-Winkel-A2B", "V-Winkel-B2A"]
    df300 = df300.drop(col2drop, axis=1, errors="ignore")
    df300 = df300.round({"Ds-A2B":4, 
                         "Ds-B2A":4, 
                         "Ds-Mittel":4, 
                         "V-Winkel-A2B":5, 
                         "V-Winkel-B2A":5, 
                         "delta_H":4, 
                         "k":2})

    df300 = df300.rename(columns={"ID" : "ID Messung",
                                  "Ds-A2B" : "d' (schräg) A-->B [m]",
                                  "Ds-B2A" : "d' (schräg) B-->A [m]",
                                  "Ds-Mittel" : "d' (mittel, schräg) [m]",
                                  "V-Winkel-A2B" : "V-Winkel A-->B [gon]",
                                  "V-Winkel-B2A" : "V-Winkel B-->A [gon]",
                                  "delta_H" : "Höhendiff. [m]",
                                  "k" : "Refraktionskoeff. k"})

    df300 = df300.loc[:, ["ID Messung",
                          "Lage", 
                          "d' (schräg) A-->B [m]", 
                          "d' (schräg) B-->A [m]", 
                          "d' (mittel, schräg) [m]", 
                          "V-Winkel A-->B [gon]", 
                          "V-Winkel B-->A [gon]",
                          "Höhendiff. [m]",
                          "Refraktionskoeff. k"]]

    ## Statistiken
    pktNr_A = start100
    pktNr_B = end100
    delta_h_aprox = round(np.abs(df100_target["Hoehe"].values[0] - df100_start["Hoehe"].values[0]),2)

    mean_delta_h = round(df300["Höhendiff. [m]"].mean(), 4)
    std_delta_h = round(df300["Höhendiff. [m]"].std(), 4)

    df400 = df300[df300["Lage"] == "1"]
    df500 = df300[df300["Lage"] == "2"]

    mean_delta_h_lage1 = round(df400["Höhendiff. [m]"].mean(), 4)
    std_delta_h_lage1 = round(df400["Höhendiff. [m]"].std(), 4)

    mean_delta_h_lage2 = round(df500["Höhendiff. [m]"].mean(), 4)
    std_delta_h_lage2 = round(df500["Höhendiff. [m]"].std(), 4)

    mean_k = round(df300["Refraktionskoeff. k"].mean(), 2)
    std_k = round(df300["Refraktionskoeff. k"].std(), 2)

    mean_k_lage1 = round(df400["Refraktionskoeff. k"].mean(), 2)
    std_k_lage1 = round(df400["Refraktionskoeff. k"].std(), 2)

    mean_k_lage2 = round(df500["Refraktionskoeff. k"].mean(), 2)
    std_k_lage2 = round(df500["Refraktionskoeff. k"].std(), 2)

    mean_sd = round(df300["d' (mittel, schräg) [m]"].mean(), 4)
    std_sd = round(df300["d' (mittel, schräg) [m]"].std(), 4)

    mean_sd_lage1 = round(df400["d' (mittel, schräg) [m]"].mean(), 4)
    std_sd_lage1 = round(df400["d' (mittel, schräg) [m]"].std(), 4)

    mean_sd_lage2 = round(df500["d' (mittel, schräg) [m]"].mean(), 4)
    std_sd_lage2 = round(df500["d' (mittel, schräg) [m]"].std(), 4)

    praeanalyse = round(np.sqrt(d_komp**2 + z_komp**2 + i_komp**2 + s_komp**2) / np.sqrt(2), 2)
    praeanalyse_komp = [d_komp, z_komp, k_komp, i_komp, s_komp]

    ## Letzte kontrolle des df
    visur = f"Visur_{start100}-{end100}"

    df300["ID Visur"] = visur

    df300 = df300.loc[:, ["ID Visur",
                          "ID Messung",
                          "Lage", 
                          "d' (schräg) A-->B [m]", 
                          "d' (schräg) B-->A [m]", 
                          "d' (mittel, schräg) [m]", 
                          "V-Winkel A-->B [gon]", 
                          "V-Winkel B-->A [gon]",
                          "Höhendiff. [m]",
                          "Refraktionskoeff. k"]]

    ## Ausgabe
    infos_vis = [pktNr_A, 
                 pktNr_B,
                 float(praeanalyse), 
                 praeanalyse_komp]
                 
    infos_height = [float(delta_h_aprox),
                   float(mean_delta_h), 
                   float(std_delta_h), 
                   float(mean_delta_h_lage1),
                   float(std_delta_h_lage1),
                   float(mean_delta_h_lage2),
                   float(std_delta_h_lage2)]

    infos_k = [float(mean_k), 
               float(std_k),
               float(mean_k_lage1),
               float(std_k_lage1),
               float(mean_k_lage2),
               float(std_k_lage2)]

    infos_sd = [float(mean_sd), 
                float(std_sd),
                float(mean_sd_lage1),
                float(std_sd_lage1),
                float(mean_sd_lage2),
                float(std_sd_lage2)]


    ## <----------------------------------------------------------------------------------->

    return df300, infos_vis, infos_height, infos_k, infos_sd

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
    xi = (xi / 10_000) /200 * np.pi
    eta = (eta / 10_000) /200 * np.pi

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