"""
Life OS ↔ Notion CI 同步脚本
运行于 GitHub Actions，使用 NOTION_TOKEN 环境变量。

用法:
  python scripts/ci_sync_notion.py push    # Life OS JSON → Notion
  python scripts/ci_sync_notion.py pull    # Notion → Life OS JSON
  python scripts/ci_sync_notion.py sync    # 双向全量同步
"""
import json, urllib.request, urllib.error, os, sys
from datetime import datetime

# ── CI 环境路径 ───────────────────────────────────────────────
REPO_ROOT = os.environ.get('GITHUB_WORKSPACE', os.getcwd())
DATA_DIR = os.path.join(REPO_ROOT, 'public', 'data')
STATE_FILE = os.path.join(REPO_ROOT, 'scripts', '_sync_state_ci.json')
SCRIPTS_DIR = os.path.join(REPO_ROOT, 'scripts')

TK = os.environ.get('NOTION_TOKEN', '').strip()
if not TK:
    # SPIT: CONSOLE.FATAL — 无凭据
    print('❌ NOTION_TOKEN 环境变量未设置或为空', file=sys.stderr)
    sys.exit(1)

# ── Notion 数据库 ID 映射 ──────────────────────────────────────
NOTION_DB_IDS = {
    "📋 项目工坊": "9dc5a2b3-41d8-4c54-ac16-cb7f0a25f183",
    "📝 教案工作台": "7018c221-02f6-4788-a760-69391e1e0d0b",
    "✍️ 公众号工作室": "7da458f4-59ea-497e-9e1b-f00da2854680",
    "📚 阅读笔记": "3218e913-e5ad-4eb5-af2a-9371cf9ee12d",
    "💰 财务账本": "2a2d8ec6-ef63-44bf-a176-c0c5cec65198",
    "🎬 影视清单": "6169321c-e891-445f-b7a3-3b0f4b43400b",
    "📊 OKR 追踪": "02ad8b27-c7f0-47ab-81ed-40f9e67bdd9f",
}

# ── Universal Helpers ─────────────────────────────────────────

def notion_api(path, body=None, method='POST'):
    """Call Notion API v2025-09-03."""
    data = json.dumps(body, ensure_ascii=False).encode('utf-8') if body else None
    req = urllib.request.Request(
        f'https://api.notion.com/v1{path}', data=data,
        headers={
            'Authorization': f'Bearer {TK}',
            'Notion-Version': '2025-09-03',
            'Content-Type': 'application/json; charset=utf-8',
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return True, json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors='replace')[:300]
        return False, f"HTTP {e.code}: {body}"
    except Exception as e:
        return False, str(e)

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"mappings": {}, "last_push": None, "last_pull": None}

def save_state(state):
    state["_updated"] = datetime.now().isoformat()
    os.makedirs(SCRIPTS_DIR, exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def write_sync_status(updated_categories):
    """写 sync-status.json，版本号递增。"""
    status_path = os.path.join(DATA_DIR, 'sync-status.json')
    current_ver = 0
    if os.path.exists(status_path):
        try:
            with open(status_path, 'r', encoding='utf-8') as f:
                current_ver = json.load(f).get('dataVersion', 0)
        except Exception:
            pass
    new_ver = current_ver + 1
    rec = {
        "lastSync": datetime.now().isoformat(),
        "dataVersion": new_ver,
        "source": "Notion",
        "updated": updated_categories,
    }
    with open(status_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    return rec

def get_existing_titles(db_id):
    """返回数据库中所有页面的标题集合 — 用于 Push 去重。"""
    pages = list_notion_pages(db_id)
    titles = set()
    for p in pages:
        t = p.get('properties', {}).get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', '')
        if t:
            titles.add(t)
    return titles


def list_notion_pages(db_id):
    """分页拉取数据库中所有 page（data_source query）。"""
    pages = []
    ds_ok, ds = notion_api(f'/databases/{db_id}', None, 'GET')
    if not ds_ok:
        print(f'  ⚠️  无法读取数据库 {db_id}: {ds}')
        return pages
    ds_id = ds['data_sources'][0]['id']
    cursor = None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        ok, r = notion_api(f'/data_sources/{ds_id}/query', body)
        if not ok:
            print(f'  ⚠️  查询失败: {r}')
            break
        pages.extend(r.get('results', []))
        if not r.get('has_more'):
            break
        cursor = r.get('next_cursor')
    return pages


# ═══════════════════════════════════════════════════════════
#  PUSH: Life OS JSON → Notion
# ═══════════════════════════════════════════════════════════

def push_projects(state):
    print('\n📋 项目工坊 ← projects.json')
    data = load_json('projects.json')
    db_id = NOTION_DB_IDS['📋 项目工坊']
    status_map = {'active': '🚀 进行中', 'planning': '📋 规划中', 'completed': '✅ 已完成', 'paused': '⏸️ 暂停'}
    type_map = {'teaching': '教学', 'content': '公众号', 'personal': '个人', 'research': '科研', 'programming': '编程'}

    existing = get_existing_titles(db_id)
    for proj in data:
        if proj['name'] in existing:
            print(f'  ⏭️  {proj["name"]} (已存在)')
            continue
        if f'project:{proj["id"]}' in state.get('mappings', {}):
            print(f'  ⏭️  {proj["name"]} (已同步)')
            continue

        total = len(proj.get('tasks', []))
        done = sum(1 for t in proj.get('tasks', []) if t.get('completed'))
        pct = round(done / total * 100) if total > 0 else 0

        props = {
            'Name': {'title': [{'text': {'content': proj['name']}}]}, 
            '状态': {'select': {'name': status_map.get(proj.get('status', ''), '🚀 进行中')}},
            '类型': {'select': {'name': type_map.get(proj.get('type', ''), '教学')}},
            '进度': {'number': pct},
            '关联OKR': {'rich_text': [{'text': {'content': ', '.join(proj.get('kr_ids', []))}}]},
            '描述': {'rich_text': [{'text': {'content': f'子任务: {total}/{done}'}}]},
        }
        if proj.get('deadline'):
            props['截止日期'] = {'date': {'start': proj['deadline']}}
        if proj.get('status') == 'active':
            props['优先级'] = {'select': {'name': '🔴 高'}}
        elif proj.get('status') == 'planning':
            props['优先级'] = {'select': {'name': '🟡 中'}}

        ok, r = notion_api('/pages', {
            'parent': {'type': 'database_id', 'database_id': db_id},
            'properties': props,
        })
        if ok:
            print(f'  ✅ {proj["name"]} → {r["id"][:8]}...')
            state['mappings'][f'project:{proj["id"]}'] = r['id']
        else:
            print(f'  ❌ {proj["name"]}: {r}')


def push_okrs(state):
    print('\n📊 OKR ← okr.json')
    data = load_json('okr.json')
    db_id = NOTION_DB_IDS['📊 OKR 追踪']
    area_map = {'work': '教学', 'side': '公众号', 'personal': '个人', 'research': '科研'}

    existing = get_existing_titles(db_id)
    for obj in data:
        if obj['title'] in existing:
            print(f'  ⏭️  {obj["title"]} (已存在)')
            continue
        if f'okr:{obj["id"]}' in state.get('mappings', {}):
            print(f'  ⏭️  {obj["title"]} (已同步)')
            continue

        krs = obj.get('key_results', [])
        avg = round(sum(kr.get('current', 0) / max(kr.get('target', 1), 1) * 100 for kr in krs) / len(krs)) if krs else 0
        kr_text = '\n'.join(
            f"{i+1}. {kr['title']} ({kr.get('current',0)}/{kr.get('target',0)}{kr.get('unit','')})"
            for i, kr in enumerate(krs)
        )
        props = {
            'Name': {'title': [{'text': {'content': obj['title']}}]},
            '类型': {'select': {'name': '季度OKR'}},
            '领域': {'select': {'name': area_map.get(obj.get('type', ''), '教学')}},
            '整体进度': {'number': avg},
            '关键结果': {'rich_text': [{'text': {'content': kr_text}}]},
            '年份': {'number': 2026},
        }
        ok, r = notion_api('/pages', {
            'parent': {'type': 'database_id', 'database_id': db_id},
            'properties': props,
        })
        if ok:
            print(f'  ✅ {obj["title"]} → {r["id"][:8]}...')
            state['mappings'][f'okr:{obj["id"]}'] = r['id']
        else:
            print(f'  ❌ {obj["title"]}: {r}')


def push_finance(state):
    print('\n💰 财务账本 ← finance.json')
    data = load_json('finance.json')
    db_id = NOTION_DB_IDS['💰 财务账本']
    type_map = {'expense': '📤 支出', 'income': '📥 收入'}
    cat_map = {'dining': '餐饮', 'office': '办公', 'shopping': '购物', 'entertainment': '娱乐',
               'transport': '交通', 'salary': '学习', 'books': '学习', 'housing': '居住', 'digital': '购物'}

    existing = get_existing_titles(db_id)
    for tx in data.get('transactions', []):
        if tx['description'] in existing:
            print(f'  ⏭️  {tx["description"]} (已存在)')
            continue

        props = {
            'Name': {'title': [{'text': {'content': tx['description']}}]}, 
            '类型': {'select': {'name': type_map.get(tx['type'], '📤 支出')}},
            '分类': {'select': {'name': cat_map.get(tx['category'], '其他')}},
            '金额': {'number': tx['amount']},
            '日期': {'date': {'start': tx['date']}},
        }
        if tx.get('notes'):
            props['备注'] = {'rich_text': [{'text': {'content': tx['notes']}}]}

        ok, r = notion_api('/pages', {
            'parent': {'type': 'database_id', 'database_id': db_id},
            'properties': props,
        })
        if ok:
            print(f'  ✅ {tx["description"]} {tx["amount"]}元')
            state['mappings'][f'finance:{tx["id"]}'] = r['id']
        else:
            print(f'  ❌ {tx["description"]}: {r}')


def push_reading(state):
    print('\n📚 阅读笔记 ← knowledge.json')
    data = load_json('knowledge.json')
    db_id = NOTION_DB_IDS['📚 阅读笔记']
    status_map = {'reading': '📖 在读', 'completed': '✅ 已读', 'want_to_read': '📚 想读', 'dropped': '🚫 弃读'}

    existing = get_existing_titles(db_id)
    for book in data.get('readingList', []):
        if book['title'] in existing:
            print(f'  ⏭️  {book["title"]} (已存在)')
            continue

        rating_name = ''
        if book.get('rating'):
            stars = min(book['rating'], 5)
            rating_name = ['⭐', '⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐⭐⭐'][stars - 1]

        props = {
            'Name': {'title': [{'text': {'content': book['title']}}]},
            '作者': {'rich_text': [{'text': {'content': book.get('author', '')}}]},
            '状态': {'select': {'name': status_map.get(book.get('status', ''), '📚 想读')}},
            '进度': {'number': book.get('progress', 0)},
        }
        if rating_name:
            props['评分'] = {'select': {'name': rating_name}}
        if book.get('startDate'):
            props['开始日期'] = {'date': {'start': book['startDate']}}
        if book.get('completedDate'):
            props['完成日期'] = {'date': {'start': book['completedDate']}}

        ok, r = notion_api('/pages', {
            'parent': {'type': 'database_id', 'database_id': db_id},
            'properties': props,
        })
        if ok:
            print(f'  ✅ {book["title"]}')
            state['mappings'][f'book:{book["id"]}'] = r['id']
        else:
            print(f'  ❌ {book["title"]}: {r}')


def push_media(state):
    print('\n🎬 影视清单 ← life.json')
    data = load_json('life.json')
    db_id = NOTION_DB_IDS['🎬 影视清单']
    type_map = {'tv': '📺 剧集', 'movie': '🎬 电影', 'anime': '🐣 动漫', 'documentary': '📖 纪录片'}
    status_map = {'watching': '👀 在看', 'completed': '✅ 已看', 'want_to_watch': '🔖 想看'}

    existing = get_existing_titles(db_id)
    for m in data.get('media', []):
        if m['title'] in existing:
            print(f'  ⏭️  {m["title"]} (已存在)')
            continue

        rating_name = ''
        if m.get('rating') and isinstance(m['rating'], int) and m['rating'] >= 1:
            stars = min(m['rating'], 5)
            rating_name = ['⭐', '⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐⭐⭐'][stars - 1]

        props = {
            'Name': {'title': [{'text': {'content': m['title']}}]},
            '类型': {'select': {'name': type_map.get(m.get('type', ''), '🎬 电影')}},
            '状态': {'select': {'name': status_map.get(m.get('status', ''), '🔖 想看')}},
        }
        if m.get('notes'):
            props['笔记'] = {'rich_text': [{'text': {'content': m['notes']}}]}
        if rating_name:
            props['评分'] = {'select': {'name': rating_name}}

        ok, r = notion_api('/pages', {
            'parent': {'type': 'database_id', 'database_id': db_id},
            'properties': props,
        })
        if ok:
            print(f'  ✅ {m["title"]}')
            state['mappings'][f'media:{m["id"]}'] = r['id']
        else:
            print(f'  ❌ {m["title"]}: {r}')


# ═══════════════════════════════════════════════════════════
#  PULL: Notion → Life OS JSON
# ═══════════════════════════════════════════════════════════

def pull_projects():
    print('\n📋 Pull: 项目工坊 → projects.json')
    pages = list_notion_pages(NOTION_DB_IDS['📋 项目工坊'])
    status_map = {'🚀 进行中': 'active', '📋 规划中': 'planning', '✅ 已完成': 'completed', '⏸️ 暂停': 'paused'}
    type_map = {'教学': 'teaching', '公众号': 'content', '编程': 'personal', '科研': 'research', '个人': 'personal'}

    projects = []
    seen = {}
    for pg in pages:
        props = pg.get('properties', {})
        title = props.get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', '')
        if not title or title in seen:
            continue

        status = status_map.get(props.get('状态', {}).get('select', {}).get('name', ''), 'active')
        p_type = type_map.get(props.get('类型', {}).get('select', {}).get('name', ''), 'teaching')
        progress = props.get('进度', {}).get('number', 0)

        deadline = None
        dd = props.get('截止日期')
        if isinstance(dd, dict):
            inner = dd.get('date')
            if isinstance(inner, dict) and inner:
                deadline = inner.get('start') or None

        proj = {
            'id': f'P{len(seen)+1:03d}', 'name': title,
            'type': p_type, 'status': status, 'deadline': deadline,
            'tasks': [], 'kr_ids': [],
        }
        seen[title] = proj

    projects = list(seen.values())

    save_json('projects.json', projects)
    print(f'  ✅ 同步 {len(projects)} 个项目')
    return len(projects)


def pull_finance():
    print('\n💰 Pull: 财务账本 → finance.json')
    pages = list_notion_pages(NOTION_DB_IDS['💰 财务账本'])
    type_map = {'📤 支出': 'expense', '📥 收入': 'income'}
    cat_map = {'餐饮': 'dining', '办公': 'office', '购物': 'shopping', '娱乐': 'entertainment',
               '交通': 'transport', '学习': 'books', '居住': 'housing'}

    seen = {}
    for pg in pages:
        props = pg.get('properties', {})
        desc = props.get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', '')
        if not desc or desc in seen:
            continue

        tx_type = type_map.get(props.get('类型', {}).get('select', {}).get('name', ''), 'expense')
        cat = cat_map.get(props.get('分类', {}).get('select', {}).get('name', ''), 'other')
        amt = props.get('金额', {}).get('number', 0)

        dt = ''
        dd = props.get('日期')
        if isinstance(dd, dict):
            inner = dd.get('date')
            if isinstance(inner, dict) and inner:
                dt = inner.get('start', '')

        seen[desc] = {
            'id': f'TR{len(seen)+1:03d}', 'date': dt or '', 'type': tx_type,
            'category': cat, 'amount': amt, 'description': desc,
            'month': (dt or '')[:7],
        }

    txs = list(seen.values())

    finance = load_json('finance.json')
    finance['transactions'] = txs
    save_json('finance.json', finance)
    print(f'  ✅ 同步 {len(txs)} 笔交易')
    return len(txs)


def pull_reading():
    print('\n📚 Pull: 阅读笔记 → knowledge.json')
    pages = list_notion_pages(NOTION_DB_IDS['📚 阅读笔记'])
    status_map = {'📖 在读': 'reading', '✅ 已读': 'completed', '📚 想读': 'want_to_read', '🚫 弃读': 'dropped'}

    seen = {}
    for pg in pages:
        props = pg.get('properties', {})
        title = props.get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', '')
        if not title or title in seen:
            continue

        author = ''
        rt = props.get('作者', {}).get('rich_text', [])
        if rt:
            author = rt[0].get('text', {}).get('content', '')
        status = status_map.get(props.get('状态', {}).get('select', {}).get('name', ''), 'want_to_read')
        progress = props.get('进度', {}).get('number', 0)

        rating = 0
        sel = props.get('评分', {}).get('select', {})
        if sel and sel.get('name'):
            rating = len(sel['name'])

        seen[title] = {
            'id': f'R{len(seen)+1:03d}', 'title': title, 'author': author,
            'type': 'book', 'status': status, 'progress': progress,
            'rating': rating, 'notes': '', 'startDate': None, 'completedDate': None, 'cover': '',
        }

    books = list(seen.values())

    knowledge = load_json('knowledge.json')
    knowledge['readingList'] = books
    save_json('knowledge.json', knowledge)
    print(f'  ✅ 同步 {len(books)} 本书')
    return len(books)


def pull_media():
    print('\n🎬 Pull: 影视清单 → life.json')
    pages = list_notion_pages(NOTION_DB_IDS['🎬 影视清单'])
    type_map = {'📺 剧集': 'tv', '🎬 电影': 'movie', '🐣 动漫': 'anime', '📖 纪录片': 'documentary'}
    status_map = {'👀 在看': 'watching', '✅ 已看': 'completed', '🔖 想看': 'want_to_watch'}

    media = []
    seen = {}
    for pg in pages:
        props = pg.get('properties', {})
        title = props.get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', '')
        if not title or title in seen:
            continue

        m_type = type_map.get(props.get('类型', {}).get('select', {}).get('name', ''), 'movie')
        status = status_map.get(props.get('状态', {}).get('select', {}).get('name', ''), 'want_to_watch')
        notes = ''
        rt = props.get('笔记', {}).get('rich_text', [])
        if rt:
            notes = rt[0].get('text', {}).get('content', '')

        rating = 0
        sel = props.get('评分', {}).get('select', {})
        if sel and sel.get('name'):
            rating = len(sel['name'])

        seen[title] = {
            'id': f'M{len(seen)+1:03d}', 'title': title, 'type': m_type,
            'status': status, 'progress': '', 'rating': rating, 'notes': notes,
            'startDate': None, 'completedDate': None, 'tags': [],
        }

    media = list(seen.values())

    life = load_json('life.json')
    life['media'] = media
    save_json('life.json', life)
    print(f'  ✅ 同步 {len(media)} 部影视')
    return len(media)


def pull_okrs():
    """📊 OKR 追踪 → okr.json"""
    print('\n📊 Pull: OKR → okr.json')
    pages = list_notion_pages(NOTION_DB_IDS['📊 OKR 追踪'])
    area_map = {'教学': 'work', '公众号': 'side', '个人': 'personal', '科研': 'research'}

    import re
    okrs = []
    seen = {}
    for pg in pages:
        props = pg.get('properties', {})
        title = props.get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', '')
        if not title or title in seen:
            continue

        area = area_map.get(props.get('领域', {}).get('select', {}).get('name', ''), 'work')
        year = props.get('年份', {}).get('number', 2026)
        overall = props.get('整体进度', {}).get('number', 0)

        # 解析 关键结果 rich_text → 结构化
        krs = []
        rt = props.get('关键结果', {}).get('rich_text', [])
        if rt:
            kr_text = rt[0].get('text', {}).get('content', '')
            for line in kr_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                m = re.match(r'^(\d+)\.\s+(.+?)\s+\((\d+)/(\d+)(\S+?)\)$', line)
                if m:
                    krs.append({
                        'id': f'K{len(krs)+1:03d}',
                        'title': m.group(2),
                        'current': int(m.group(3)),
                        'target': int(m.group(4)),
                        'unit': m.group(5),
                    })

        seen[title] = {
            'id': len(seen) + 1,
            'title': title,
            'description': '',
            'quarter': f'{year}-Q2',
            'status': 'active',
            'key_results': krs,
        }

    okrs = list(seen.values())

    save_json('okr.json', okrs)
    print(f'  ✅ 同步 {len(okrs)} 个 OKR')
    return len(okrs)


# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'push'

    os.makedirs(SCRIPTS_DIR, exist_ok=True)
    state = load_state()

    print(f'🔑 Token: {TK[:20]}...')
    print(f'📦 Mode: {mode}')
    print(f'📂 Repo: {REPO_ROOT}')

    if mode == 'push':
        print('=' * 60)
        print('PUSH: Life OS JSON → Notion')
        print('=' * 60)
        push_projects(state)
        push_okrs(state)
        push_finance(state)
        push_reading(state)
        push_media(state)
        state['last_push'] = datetime.now().isoformat()
        save_state(state)
        print(f'\n✅ Push 完成! 映射数: {len(state["mappings"])}')

    elif mode == 'pull':
        print('=' * 60)
        print('PULL: Notion → Life OS JSON')
        print('=' * 60)
        updated = []
        if pull_projects():
            updated.append('📋 项目')
        if pull_okrs():
            updated.append('📊 OKR')
        if pull_finance():
            updated.append('💰 财务')
        if pull_reading():
            updated.append('📚 阅读')
        if pull_media():
            updated.append('🎬 影视')
        state['last_pull'] = datetime.now().isoformat()
        save_state(state)
        status = write_sync_status(updated)
        print(f'\n✅ Pull 完成! sync-status v{status["dataVersion"]}')

    elif mode == 'sync':
        print('=' * 60)
        print('BIDIRECTIONAL SYNC')
        print('=' * 60)
        push_projects(state)
        push_okrs(state)
        push_finance(state)
        push_reading(state)
        push_media(state)
        updated = []
        if pull_projects():
            updated.append('📋 项目')
        if pull_okrs():
            updated.append('📊 OKR')
        if pull_finance():
            updated.append('💰 财务')
        if pull_reading():
            updated.append('📚 阅读')
        if pull_media():
            updated.append('🎬 影视')
        now = datetime.now().isoformat()
        state['last_push'] = now
        state['last_pull'] = now
        save_state(state)
        status = write_sync_status(updated)
        print(f'\n✅ 全量同步完成! sync-status v{status["dataVersion"]}')

    else:
        print(f'❌ 未知模式: {mode}。支持: push | pull | sync')
        sys.exit(2)
