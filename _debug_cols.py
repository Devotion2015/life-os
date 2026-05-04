import pandas as pd
df = pd.read_excel(r"C:\Users\Devotion\.qclaw\workspace\life-os\2026工作日志.xlsx", sheet_name="工作计划")
print("完成情况 unique values:")
print(df["完成情况"].value_counts(dropna=False))
print("\n优先级 unique values:")
print(df["优先级"].value_counts(dropna=False))
print("\n完成日期 sample (first 5 non-null):")
print(df[df["完成日期"].notna()][["计划任务", "完成情况", "完成日期"]].head())