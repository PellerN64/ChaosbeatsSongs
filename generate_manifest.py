import zipfile, configparser, json, os

songs_dir = "songs"
manifest = []

for fname in os.listdir(songs_dir):
    if not fname.endswith(".cbs"):
        continue
    path = os.path.join(songs_dir, fname)

    with zipfile.ZipFile(path, "r") as z:
        if "info.cbi" not in z.namelist():
            continue

        with z.open("info.cbi") as f:
            parser = configparser.ConfigParser()
            parser.read_string(f.read().decode("utf-8"))

        info = parser["Info"]
        meta = parser["Meta"] if "Meta" in parser else {}

        difficulties = []
        for section in parser.sections():
            if section.startswith("Difficulties."):
                diff = parser[section]
                difficulties.append({
                    "id": section.split(".", 1)[1].lower(),
                    "name": diff.get("DifficultyName", ""),
                    "chart": diff.get("Chart", ""),
                    "songFile": diff.get("SongFile", None)
                })

        manifest.append({
            "id": os.path.splitext(fname)[0],
            "title": info.get("Name", ""),
            "artist": info.get("Artist", ""),
            "creator": info.get("Creator", ""),
            "bpm": meta.get("BPM", None),
            "url": f"https://pellern64.github.io/ChaosbeatsSongs/main/{songs_dir}/{fname}",
            "preview": info.get("Preview", info.get("Song", None)),
            "difficulties": difficulties
        })

with open("manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
