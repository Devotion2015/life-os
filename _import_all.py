import pandas as pd, json
from datetime import datetime

df = pd.read_excel(r"C:\Users\Devotion\.qclaw\workspace\life-os\2026工作日志.xlsx", sheet_name="工作计划")

priority_map = {"高": "high", "中": "medium", "低": "low"}
status_map = {"x": "completed", "已完成": "completed"}

def fmt_date(v):
    if pd.isna(v) or str(v).strip() == "":
        return ""
    if isinstance(v, datetime):
        return v.strftime("%Y-%m-%d")
    return str(v).strip()

todos = []
for idx, row in df.iterrows():
    task = row.get("计划任务", "")
    if pd.isna(task) or str(task).strip() == "":
        continue
    
    status_str = str(row.get("完成情况", "")).strip()
    status = status_map.get(status_str, "pending")
    
    pri_str = str(row.get("优先级", "中")).strip()
    priority = priority_map.get(pri_str, "medium")
    
    todos.append({
        "id": idx + 1,
        "text": str(task).strip(),
        "status": status,
        "priority": priority,
        "source": "金山文档工作计划",
        "semester": str(row.get("学期", "")).strip() if not pd.isna(row.get("学期", "")) else "",
        "start": fmt_date(row.get("开始时间", "")),
        "deadline": fmt_date(row.get("截止时间", "")),
        "completed_date": fmt_date(row.get("完成日期", "")),
        "notes": str(row.get("备注", "")).strip() if not pd.isna(row.get("备注", "")) else ""
    })

print(f"Total imported: {len(todos)}")
print(f"  Completed: {sum(1 for t in todos if t['status'] == 'completed')}")
print(f"  Pending: {sum(1 for t in todos if t['status'] == 'pending')}")
print(f"  High: {sum(1 for t in todos if t['priority'] == 'high')}")
print(f"  Medium: {sum(1 for t in todos if t['priority'] == 'medium')}")
print(f"  Low: {sum(1 for t in todos if t['priority'] == 'low')}")

out_path = r"C:\Users\Devotion\.qclaw\workspace\life-os\public\data\todos.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(todos, f, ensure_ascii=False, indent=2)
print(f"\nSaved to {out_path}")