from math import *


def gon2rad(gon):
    return gon * pi / 200.0

def rad2gon(rad):
    return rad * 200.0 / pi

def korr_lotabw(xi, eta, azi, v_angle):
    v_angle = gon2rad(azi) # gon to rad
    azi = gon2rad(azi) # gon to rad
    # xi und eta umrechnen von cc (1cc = 0.1mgon) in rad
    xi = (xi / 10000) /200 * pi
    eta = (eta / 10000) /200 * pi

    theta_v = xi * cos(azi) + eta * sin(azi) # Berechnung der Lotabweichung in laengsrichtung aus xi und eta
    v_angle_korr = v_angle + theta_v # Korrektur des Azimuts um Theta laengs
    v_angle_korr = rad2gon(v_angle_korr) # rad to gon

    return v_angle_korr


def korr_kippachse(dist_ab,offset_b, v_angle_korr):
    azi_korr = gon2rad(v_angle_korr) # gon to rad
    dist_korr = sqrt(offset_b**2 + dist_ab**2 - 2*offset_b*dist_ab-cos(v_angle_korr)) # Berechnung der korrigierten Distanz aufgrund des speziellen Prismamounts (mit cosinussatz)
    beta_ab = acos((dist_ab**2+dist_korr**2-offset_b**2)/2*dist_ab*dist_korr) # Berechnung des Winkels Beta zwischen der gemessenen Distanz und der Korrekturdistanz
    v_angle_korr_korr = v_angle_korr + beta_ab # Korrektur des Azimuts um Beta
    v_angle_korr_korr = rad2gon(v_angle_korr_korr) # rad to gon

    return dist_korr, v_angle_korr_korr



def delta_h(mittel_dist, v_angle_korr_korr_ab, v_angle_korr_korr_ba, instr_height_a, instr_height_b, signal_height_a, signal_height_b):
    v_angle_korr_korr_ab = gon2rad(v_angle_korr_korr_ab) # gon to rad
    v_angle_korr_korr_ba = gon2rad(v_angle_korr_korr_ba) # gon to rad
    delta_h = 0.5* (mittel_dist *(sin((pi/2)-v_angle_korr_korr_ab))-cos(pi-v_angle_korr_korr_ba)+(instr_height_a-instr_height_b)+(signal_height_a-signal_height_b)) # Berechnung der Höhendifferenz

    return delta_h


def refraktion(mittel_dist, delta_h, v_angle_korr_korr_ab, v_angle_korr_korr_ba):
    v_angle_korr_korr_ab = gon2rad(v_angle_korr_korr_ab) # gon to rad
    v_angle_korr_korr_ba = gon2rad(v_angle_korr_korr_ba) # gon to rad
    k = 1-((v_angle_korr_korr_ab+v_angle_korr_korr_ba-pi)*6370000/(mittel_dist*sin(v_angle_korr_korr_ab))) # Berechnung des Refraktionskoeffizienten

    return k

def cool (x):
    return f"de boppi und de michi sind {x}"


## Berechnung Azimut aus Näherungskoordinaten
def azi_aprox(df_start, df_end):
    """
    Berechnet das Näherungsazimut zwischen zwei Punkten auf Grundlage ihrer
    Ost- und Nordkoordinaten.

    Die Funktion liest die Koordinaten aus zwei DataFrames (`df_start` und 
    `df_end`), ermittelt die Richtungsdifferenzen in Ost- und Nordrichtung 
    und gibt das Azimut in Gon (Neugrad) zurück. Dabei werden Sonderfälle 
    für reine Nord-, Süd-, Ost- oder Westrichtungen berücksichtigt.

    Parameter
    ----------
    df_start : pandas.DataFrame
        DataFrame mit den Startkoordinaten. Muss die Spalten "E-Koord" und 
        "N-Koord" enthalten.
    df_end : pandas.DataFrame
        DataFrame mit den Endkoordinaten. Muss ebenfalls die Spalten 
        "E-Koord" und "N-Koord" enthalten.

    Rueckgabewert
    -------------
    float
        Azimut in Gon (Neugrad), gemessen von Norden im Uhrzeigersinn.
    """

    ## Auswahl der Koordinaten aus dem DF
    E1 = df_start["E-Koord"].values[0]
    N1 = df_start['N-Koord'].values[0]
    E2 = df_end['E-Koord'].values[0]
    N2 = df_end['N-Koord'].values[0]

    ## Berechnung des Azimutes aus den Näherungskoordinaten
    delta_East = E2 - E1
    delta_North = N2 - N1
    if delta_East == 0 and delta_North > 0:
        azimuth = 0.0
    elif delta_East == 0 and delta_North < 0:
        azimuth = 200.0
    elif delta_East > 0 and delta_North == 0:
        azimuth = 100.0
    elif delta_East < 0 and delta_North == 0:
        azimuth = 300.0
    elif delta_East > 0 and delta_North > 0:
        azimuth = rad2gon(asin(delta_East / delta_North))
    elif delta_East < 0 and delta_North > 0:
        azimuth = rad2gon(asin(delta_North / delta_East)) + 300.0
    elif delta_East < 0 and delta_North < 0:
        azimuth = rad2gon(asin(delta_North / delta_East)) + 100.0
    elif delta_East > 0 and delta_North < 0:
        azimuth = rad2gon(asin(delta_East / delta_North)) + 200.0

    return azimuth