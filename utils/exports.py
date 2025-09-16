def export_protocol(visur:str, df, file_path:str):

    try:
        
        print(f"Protokolldatei erfolgreich exportiert nach {file_path}")

    except Exception as e:
        print(f"Fehler beim Exportieren der Protokolldatei: {e}")