# Life OS 模块数据关联建立

## 目标
将 OKR、项目管理、待办事项、日程管理四个模块从"各自独立"变为"数据层互联"。

## 完成内容

### 数据层
| 文件 | 变更 | 说明 |
|------|------|------|
| projects.json | 新建 | 4个项目，含 okr_ids 和 kr_refs |
| todos.json | 修改 | 28/107 已打上 project_id（关键词迁移） |
| events.json | 修改 | 7个事件增加 project_id/todo_id 可选字段 |

### UI 层
| 文件 | 变更 | 说明 |
|------|------|------|
| Projects.vue | 重写 | 从 JSON 加载，显示关联 OKR 名称 + 待办完成数 |
| Todos.vue | 修改 | 项目筛选下拉 + 列表项目徽章 + 编辑中项目选择 |
| OKR.vue | 修改 | 每个目标底部显示关联项目 + 待办进度 |

### 连接结构
```
OKR → Project ← Todo ← Calendar Event
(okr_ids)  (project_id)  (project_id/todo_id)
```

## 构建状态
- 构建成功 ✓
- 已 push 到 GitHub master ✓
- commit: b671c4c

## 下一步
- Dashboard 作为中枢统一展示四层关联
- Calendar.vue 利用新的 project_id 显示事件归属
