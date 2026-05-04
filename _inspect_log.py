import pandas as pd, json

xl = pd.read_excel(r"C:\Users\Devotion\.qclaw\workspace\life-os\2026工作日志.xlsx", sheet_name=None)
result = {}
for name, df in xl.items():
    result[name] = {"rows": len(df), "cols": list(df.columns)}

with open(r"C:\Users\Devotion\.qclaw\workspace\life-os\_inspect_log.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("Done")