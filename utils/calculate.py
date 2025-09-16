from math import *


def gon2rad(gon):
    return gon * pi / 200.0

def rad2gon(rad):
    return rad * 200.0 / pi

def korr_lotabw(xi, eta, azi, v_angle):
    v_angle = gon2rad(azi) # gon to rad
    azi = gon2rad(azi) # gon to rad
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

def cool (x):
    return f"de boppi und de michi sind {x}"