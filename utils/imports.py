import pandas as pd

def import_csv(file_path:str):

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
        df = df.drop(["Session", "Lage", "MessNr"], axis=1)

        return df
    
    except Exception as e:
        print(f"Error importing CSV file: {e}")
        return None
    

def import_fix(file_path:str):

    try:
        df = pd.read_csv(file_path, delimiter=";", encoding="mbcs")
        df = df.astype({"PktNr": str, "E-Koord": float, "N-Koord": float, "Hoehe": float,
                        "Geoid": float, "Xi": float, "Eta": float})

        return df
    
    except Exception as e:
        print(f"Error importing FP-file: {e}")
        return None