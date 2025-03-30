#!/usr/bin/env python3
import os
import subprocess
from flask import Flask, render_template_string, request

app = Flask(__name__)

# Absoluter Pfad zum Python-Skript, das im Manual-Modus gestartet werden soll
HOME_DIR = os.path.expanduser("~")
MOTOR_CONTROL_SCRIPT = os.path.join(HOME_DIR, "workspace_head", "motor_control_4.py")

# HTML-Template mit vier Buttons zur Modusauswahl
HTML_TEMPLATE = """
<!doctype html>
<html lang="de">
  <head>
    <meta charset="utf-8">
    <title>Robodom Steuerung</title>
  </head>
  <body>
    <h1>Modus auswählen</h1>
    <form action="/mode" method="post">
      <button name="mode" value="exploring" type="submit">Exploring</button>
      <button name="mode" value="manual" type="submit">Manual</button>
      <button name="mode" value="face-detection" type="submit">Face-Detection</button>
      <button name="mode" value="music" type="submit">Music</button>
    </form>
  </body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/mode", methods=["POST"])
def mode():
    selected_mode = request.form.get("mode")
    
    if selected_mode == "manual":
        # Starte das motor_control_4.py-Skript im Hintergrund
        subprocess.Popen(["python3", MOTOR_CONTROL_SCRIPT])
        message = "Manual Mode gestartet."
    elif selected_mode == "exploring":
        message = "Exploring Mode ausgewählt. (Noch nicht implementiert)"
    elif selected_mode == "face-detection":
        message = "Face-Detection Mode ausgewählt. (Noch nicht implementiert)"
    elif selected_mode == "music":
        message = "Music Mode ausgewählt. (Noch nicht implementiert)"
    else:
        message = "Unbekannter Modus."
        
    return f"{message} <br><br><a href='/'>Zurück</a>"

if __name__ == "__main__":
    # Starte den Flask-Webserver auf allen Netzwerkschnittstellen an Port 8069
    app.run(host="0.0.0.0", port=8069)
