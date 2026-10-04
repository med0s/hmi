"""Download the datasheets in datasheets_manifest.csv into ./datasheets.
Entries without a URL, and any download that fails or is not a real PDF, are listed in
datasheets/MISSING.md so they can be fetched by hand (or by Claude Code) from the vendor site."""
import csv, os, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "datasheets")
os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}
missing, ok = [], []

with open(os.path.join(HERE, "datasheets_manifest.csv"), newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        dest = os.path.join(OUT, row["file"])
        if os.path.exists(dest) and os.path.getsize(dest) > 10_000:
            ok.append(row["file"]); continue
        if not row["url"]:
            missing.append((row, "no direct URL")); continue
        try:
            req = urllib.request.Request(row["url"], headers=UA)
            data = urllib.request.urlopen(req, timeout=60).read()
            if not data.startswith(b"%PDF"):
                missing.append((row, "server did not return a PDF (login page or redirect)")); continue
            open(dest, "wb").write(data); ok.append(row["file"])
            print(f"OK   {row['file']}  ({len(data)//1024} KB)")
        except Exception as e:
            missing.append((row, f"download failed: {e}"))

with open(os.path.join(OUT, "MISSING.md"), "w", encoding="utf-8") as f:
    f.write("# Datasheets still needed\n\n| File | Part | Vendor | Reason | Notes |\n|---|---|---|---|---|\n")
    for row, why in missing:
        f.write(f"| {row['file']} | {row['part']} | {row['vendor']} | {why} | {row['notes']} |\n")
print(f"\n{len(ok)} downloaded/present, {len(missing)} missing -> datasheets/MISSING.md")
