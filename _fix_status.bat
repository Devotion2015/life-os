@echo off
cd /d "C:\Users\Devotion\.qclaw\workspace\life-os"
git add public\data\todos.json
git commit -m "fix: auto-detect completed status from completed_date"
git push
