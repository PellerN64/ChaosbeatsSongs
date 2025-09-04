import zipfile, configparser, json, os, shutil

songs_dir = "songs"
icons_dir = "public/icons"
audio_dir = "public/audio"
manifest = []

os.makedirs(icons_dir, exist_ok=True)
os.makedirs(audio_dir, exist_ok=True)

for fname in os.listdir(songs_dir):
    if not fname.endswith(".cbs"):
        continue
    path = os.path.join(songs_dir, fname)
    song_id = os.path.splitext(fname)[0]

    icon_url = None
    preview_url = None

    with zipfile.ZipFile(path, "r") as z:
        info_cbi_path = None
        for name in z.namelist():
            if name.lower().endswith("info.cbi"):
                info_cbi_path = name
                break
        if not info_cbi_path:
            print(f"skipping {fname}: no info.cbi found")
            continue

        icon_path_in_zip = next((n for n in z.namelist() if n.lower().endswith("icon.png")), None)
        if icon_path_in_zip:
            out_icon_path = os.path.join(icons_dir, f"{song_id}.png")
            with z.open(icon_path_in_zip) as src, open(out_icon_path, "wb") as dst:
                shutil.copyfileobj(src, dst)
            icon_url = f"https://pellern64.github.io/ChaosbeatsSongs/icons/{song_id}.png"

        for file in z.namelist():
            if file.lower().endswith(".ogg"):
                song_audio_dir = os.path.join(audio_dir, song_id)
                os.makedirs(song_audio_dir, exist_ok=True)
                out_audio_path = os.path.join(song_audio_dir, os.path.basename(file))
                with z.open(file) as src, open(out_audio_path, "wb") as dst:
                    shutil.copyfileobj(src, dst)

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
                songfile = diff.get("songfile", None)
                if songfile:
                    preview_url = f"https://pellern64.github.io/ChaosbeatsSongs/audio/{song_id}/{songfile}"
                difficulties.append({
                    "id": section.split(".", 1)[1].lower(),
                    "name": diff.get("difficultyname", ""),
                    "chart": diff.get("chart", ""),
                    "songFile": f"https://pellern64.github.io/ChaosbeatsSongs/audio/{song_id}/{songfile}" if songfile else None
                })

        if not preview_url and "preview" in info:
            preview_file = info.get("preview")
            preview_url = f"https://pellern64.github.io/ChaosbeatsSongs/audio/{song_id}/{preview_file}" if preview_file else None

        manifest.append({
            "id": song_id,
            "title": info.get("name", "A Song"),
            "artist": info.get("artist", "Some Person"),
            "creator": info.get("creator", "Some Nobody"),
            "bpm": meta.get("bpm", None),
            "url": f"https://pellern64.github.io/ChaosbeatsSongs/{songs_dir}/{fname}",
            "preview": preview_url,
            "icon": icon_url,
            "difficulties": difficulties
        })

os.makedirs("public", exist_ok=True)
with open("public/manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
