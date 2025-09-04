import zipfile, configparser, json, os

songs_dir = "songs"
manifest = []

for fname in os.listdir(songs_dir):
    if not fname.endswith(".cbs"):
        continue
    path = os.path.join(songs_dir, fname)

    with zipfile.ZipFile(path, "r") as z:
        info_cbi_path = None
        for name in z.namelist():
            if name.lower().endswith("info.cbi"):
                info_cbi_path = name
                break
        if not info_cbi_path:
            print(f"skipping {fname}: no info.cbi found")
            continue

        with z.open(info_cbi_path) as f:
            parser = configparser.ConfigParser()
            parser.optionxform = str.lower
            try:
                parser.read_string(f.read().decode("utf-8-sig"))
            except Exception as e:
                print(f"skipping {fname}: failed to parse info.cbi ({e})")
                continue

        if "info" not in parser:
            print(f"skipping {fname}: [Info] section missing")
            continue
        info = parser["info"]
        meta = parser["meta"] if "meta" in parser else {}

        difficulties = []
        for section in parser.sections():
            if section.lower().startswith("difficulties."):
                diff = parser[section]
                difficulties.append({
                    "id": section.split(".", 1)[1].lower(),
                    "name": diff.get("difficultyname", ""),
                    "chart": diff.get("chart", ""),
                    "songFile": diff.get("songfile", None)
                })

        manifest.append({
            "id": os.path.splitext(fname)[0],
            "title": info.get("name", ""),
            "artist": info.get("artist", ""),
            "creator": info.get("creator", ""),
            "bpm": meta.get("bpm", None),
            "url": f"https://pellern64.github.io/ChaosbeatsSongs/{songs_dir}/{fname}",
            "preview": info.get("preview", info.get("songfile", None)),
            "difficulties": difficulties
        })

with open("manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
