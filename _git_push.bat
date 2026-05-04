@echo off
cd /d "C:\Users\Devotion\.qclaw\workspace\life-os"
git add src/views/Todos.vue
git commit -m "fix: field name mismatch (title->text) and duplicate stats panel"
git push
