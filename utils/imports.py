import pandas as pd

def import_csv(file_path:str):
    """
    Importiert eine Vermessungs-CSV-Datei und bereitet die Daten für die trigonometrische Höhenbestimmung auf.

    Die Funktion:
    - Liest die CSV-Datei ein (mit Semikolon als Trennzeichen und MBCS-Encoding)
    - Entfernt Referenzstationen ("REF") aus den Daten
    - Wandelt Spalten in die passenden Datentypen um
    - Führt Distanzkorrekturen durch (PPM-Atmos)
    - Spaltet die Punktnummern in Startpunkt, Zielpunkt, Session, MessNr und ID
    - Entfernt unnötige Spalten, sodass nur die relevanten Messdaten übrig bleiben

    Parameters
    ----------
    file_path : str
        Pfad zur CSV-Datei, die importiert werden soll.

    Returns
    -------
    pandas.DataFrame or None
        Aufbereitetes DataFrame mit den Spalten:
        - "Datum" : Datum der Messung
        - "Uhrzeit" : Uhrzeit der Messung
        - "Standpkt" : Startpunkt der Messung
        - "Zielpkt" : Zielpunkt der Messung
        - "Lage" : Lage der Messung
        - "ID" : Eindeutige Mess-ID
        - "Hz-Winkel" : Horizontalwinkel
        - "V-Winkel" : Vertikalwinkel
        - "Ds" : korrigierte Schrägdistanz
        Im Fehlerfall wird `None` zurückgegeben und eine Fehlermeldung ausgegeben.
    """

    col2drop = ["Station", "Station (R)", "Station (H)", "Station (oH)", "Rechtswert", 
            "Hochwert", "orth. Höhe", "Längengrad ", "Breitengrad", "ell. Höhe", "Code",
            "Codebeschreibung", "Codegruppe", "Herkunft", "Horizontaldistanz",
            "Höhendifferenz", "Prisma", "Prismenkonstante", "EDM Typ", "EDM Mode", "ATR",
            "Exz. Quer", "Exz. Längs", "Exz. Höhe", "Antennenhöhe", "KQ 3D", "KQ 2D", "KQ 1D",
            "GDOP", "PDOP", "HDOP", "VDOP", "TDOP", "Mountpoint", "Autolinie", "Bildname"]
    
    col2drop_sec = ["indiv PPM", "Geom PPM", "Temperatur", "Luftdruck", "Total PPM", 
                "Instrumentenhöhe", "Reflektorhöhe", "Punktklasse",]
    
    col2drop_thr = ["PunktNr", "Ds-unkorr", "PPM-Atmos"]

    try:
        ## Read csv file: Points_Protokoll_IGEO ohne Header
        df = pd.read_csv(file_path, delimiter=";", encoding="mbcs")

        ## Löschung der Stationen
        df = df.astype({"Punktklasse": str})
        df = df.drop(df[df["Punktklasse"] == "REF"].index)

        ## Vorbereitung für die Distanzkorrektur
        df = df.astype({"PunktNr": str, "Lage": int, "Datum": str, "Uhrzeit": str, "Hz-Winkel": float, 
                        "V-Winkel": float, "Schrägdistanz": float, "Atmos PPM": float})
        df = df.rename(columns={"Schrägdistanz" : "Ds-unkorr", "Atmos PPM" : "PPM-Atmos"})

        ## Distanzkorrektur und Splicen der Punktnummer
        df.insert(7, "Ds",  df["Ds-unkorr"] + (((df["Ds-unkorr"]/1_000)*df["PPM-Atmos"])/1_000))
        df.insert(1, "Standpkt", df["PunktNr"].str[0:4])
        df.insert(2, "Zielpkt", df["PunktNr"].str[5:9])
        df.insert(3, "Session", df["PunktNr"].str[10:11])
        df.insert(5, "MessNr", df["PunktNr"].str[14:15])
        df.insert(6, "ID", df["PunktNr"].str[10:15])

        ## Datatyp setzten
        df = df.astype({"Standpkt": str, "Zielpkt": str, "Session": int, "MessNr": int})

        ## df aufraeumen
        col2drop.extend(col2drop_sec)
        col2drop.extend(col2drop_thr)
        df = df.drop(col2drop, axis=1)
        df = df.loc[:, ["Datum", "Uhrzeit", "Standpkt", "Zielpkt", "Session", "Lage", 
                        "MessNr", "ID", "Hz-Winkel", "V-Winkel", "Ds"]]

        ## Da Unnoetig
        df = df.drop(["Session", "MessNr"], axis=1)

        return df
    
    except Exception as e:
        print(f"Error importing CSV file: {e}")
        return None
    

def import_fix(file_path:str):
    """
    Importiert eine Fixpunkt-CSV-Datei (FP-Datei) und bereitet die Daten für die weitere Verarbeitung auf.

    Die Funktion:
    - Liest die CSV-Datei ein (mit Semikolon als Trennzeichen und MBCS-Encoding)
    - Setzt die Datentypen für die relevanten Spalten
    - Füllt fehlende Werte (NaN) mit 0 auf

    Parameters
    ----------
    file_path : str
        Pfad zur FP-CSV-Datei, die importiert werden soll.

    Returns
    -------
    pandas.DataFrame or None
        DataFrame mit den Spalten:
        - "PktNr" : Punktnummer (str)
        - "E-Koord" : Rechtswert (float)
        - "N-Koord" : Hochwert (float)
        - "Hoehe" : Höhe (float)
        - "Geoid" : Geoid-Höhe (float)
        - "Xi" : xi-Korrektur (float)
        - "Eta" : eta-Korrektur (float)
        Im Fehlerfall wird `None` zurückgegeben und eine Fehlermeldung ausgegeben.
    """

    try:
        df = pd.read_csv(file_path, delimiter=";", encoding="mbcs")
        df = df.astype({"PktNr": str, "E-Koord": float, "N-Koord": float, "Hoehe": float,
                        "Geoid": float, "Xi": float, "Eta": float})
        
        df = df.fillna(0)

        return df
    
    except Exception as e:
        print(f"Error importing FP-file: {e}")
        return None