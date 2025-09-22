# Trigonometrische Höhenbestimmung

Python Applikation für das Modul 5220 GeoSensorik und Monitoring für die Auswertung von TBHs

## Requirements

- [Git](https://git-scm.com/)
- IDE wie [Visual Studio Code](https://code.visualstudio.com/)
- [Anaconda Distribution](https://www.anaconda.com/products/distribution) oder [Miniconda](https://docs.conda.io/en/latest/miniconda.html)

## Repository lokal klonen

Mit Git in einem Terminal oder dem GitHub Desktop das GitHub Repository _thb-berechnung_ in ein lokales Verzeichnis klonen.

```shell
cd /path/to/workspace
# Clone Repository
git clone https://github.com/rbo-xyz/thb-berechnung
```

## Backend installieren

Öffne ein Terminal und wechsle in den _server_ Ordner.

1. Virtuelle Umgebung für Python mit allen Requirements aufsetzen.

```shell
# Erstelle ein neues Conda Environment und füge die Python Packges hinzu
conda create -n thb-auswertung python=3.10 -c conda-forge -y

conda install jupyterlab numpy Pandas tabulate weasyprint markdown -c conda-forge -y
```

## Funktionsweise

Die Applikation kann man auf zwei Arten benutzen.

Um nur das Prinzip einer THB verstehen zu können, wird emphohlen, das Jupyter-Notebook **TrigHoehenbestimmung_TESTDATA.ipynb** zu öffnen un bearbeiten. Dieses Arbeitet nur mit relativen Testdaten

Die Datei **TrigHoehenbestimmung_Auto.ipynb** ist konzipiert, um eine automatische Auswertung zu bewerkstelligen. Diese funktioniert nur auf dem Master-Desktop
