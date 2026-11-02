# API 404 错误修复文档

## 问题描述

### 错误信息
```
API Error: AxiosError: Request failed with status code 404
AxiosError: Request failed with status code 404
```

### 影响范围
前端应用在调用后端 API 时出现 404 错误，导致部分功能无法正常使用。

---

## 问题定位过程

### 步骤 1：日志分析
从错误日志中提取关键字段：
- 错误类型：`AxiosError`（前端请求失败）
- 状态码：`404`（资源未找到）

### 步骤 2：前端请求追踪
检查 [index.ts](file:///e:/Program%20Files%20(x86)/Trae%20CN/trae_projects/shujukuxit/frontend/src/api/index.ts) 中的所有 API 调用，确认请求 URL 格式。

### 步骤 3：后端路由对比
将前端请求 URL 与后端路由定义逐一对比：

| 前端请求 | 后端路由定义 | 状态 |
|---------|------------|------|
| `/chapters/` | `@router.get("/")` | ✓ 匹配 |
| `/chapters/{id}/` | `@router.get("/{chapter_id}")` | ⚠️ 斜杠不一致 |
| `/knowledge_points/` | `@router.get("/")` | ✓ 匹配 |
| `/knowledge_points/{id}/` | `@router.get("/{knowledge_point_id}")` | ⚠️ 斜杠不一致 |
| `/questions/` | `@router.get("/")` | ✓ 匹配 |
| `/questions/{id}/` | `@router.get("/{question_id}")` | ⚠️ 斜杠不一致 |
| `/questions/batch/` | `@router.post("/batch")` | ✗ 斜杠不一致（根本原因） |
| `/agent/chat/` | `@router.post("/chat/")` | ✓ 匹配 |
| `/agent/visualize/` | `@router.post("/visualize/")` | ✓ 匹配 |
| `/agent/generate-slides-audio/` | `@router.post("/generate-slides-audio/")` | ✓ 匹配 |

### 步骤 4：根本原因确认
通过 PowerShell 测试验证：
```powershell
# 前端调用的 URL（带斜杠）
POST /api/questions/batch/ → 返回 405 Method Not Allowed

# 后端定义的路由（不带斜杠）
POST /api/questions/batch → 返回 200 OK
```

---

## 根本原因

**FastAPI 路由匹配严格区分尾部斜杠**，前端调用 `/questions/batch/`（带斜杠）但后端路由定义为 `/batch`（不带斜杠），导致路由匹配失败。

由于 `main.py` 中的 catch-all 路由 `@app.get("/{full_path:path}")` 会拦截所有未匹配的路径，对于 POST 请求会返回 405（Method Not Allowed）而不是 404。

---

## 解决方案

### 方案 1（推荐）：后端路由统一添加尾部斜杠
将后端所有动态参数路由和子路由添加尾部斜杠，与前端保持一致。

### 方案 2：前端移除尾部斜杠
修改前端 API 调用，移除所有尾部斜杠。

### 方案选择理由
选择方案 1，理由：
1. FastAPI 推荐使用尾部斜杠（符合 RESTful 规范）
2. 前端已统一使用尾部斜杠，修改量更小
3. 避免引入新的路由冲突风险

---

## 实施步骤

### 步骤 1：修复 questions.py 批量创建端点
```python
# 修改前
@router.post("/batch")
def create_questions(...):

# 修改后
@router.post("/batch/")
def create_questions(...):
```

### 步骤 2：修复 chapters.py 动态路由
```python
# 修改前
@router.get("/{chapter_id}")
@router.put("/{chapter_id}")
@router.delete("/{chapter_id}")
@router.get("/{chapter_id}/categories")

# 修改后
@router.get("/{chapter_id}/")
@router.put("/{chapter_id}/")
@router.delete("/{chapter_id}/")
@router.get("/{chapter_id}/categories/")
```

### 步骤 3：修复 knowledge_points.py 动态路由
```python
# 修改前
@router.get("/{knowledge_point_id}")
@router.put("/{knowledge_point_id}")
@router.delete("/{knowledge_point_id}")

# 修改后
@router.get("/{knowledge_point_id}/")
@router.put("/{knowledge_point_id}/")
@router.delete("/{knowledge_point_id}/")
```

### 步骤 4：修复 questions.py 动态路由
```python
# 修改前
@router.get("/{question_id}")
@router.put("/{question_id}")
@router.delete("/{question_id}")

# 修改后
@router.get("/{question_id}/")
@router.put("/{question_id}/")
@router.delete("/{question_id}/")
```

---

## 测试结果

### 修复前测试
| 端点 | 请求 | 状态码 | 结果 |
|------|------|--------|------|
| `/api/questions/batch/` | POST | 405 | ❌ 失败 |
| `/api/questions/batch` | POST | 200 | ✓ 成功 |

### 修复后测试
| 端点 | 请求 | 状态码 | 结果 |
|------|------|--------|------|
| `/api/questions/batch/` | POST | 200 | ✓ 成功 |
| `/api/chapters/` | GET | 200 | ✓ 成功 |
| `/api/chapters/1/` | GET | 200 | ✓ 成功 |
| `/api/chapters/1/categories/` | GET | 200 | ✓ 成功 |
| `/api/knowledge_points/` | GET | 200 | ✓ 成功 |
| `/api/knowledge_points/1/` | GET | 200 | ✓ 成功 |
| `/api/questions/` | GET | 200 | ✓ 成功 |
| `/api/questions/1/` | GET | 200 | ✓ 成功 |
| `/api/agent/chat/` | POST | 200 | ✓ 成功 |
| `/api/agent/visualize/` | POST | 200 | ✓ 成功 |
| `/api/agent/generate-slides-audio/` | POST | 200 | ✓ 成功 |

### 回归测试
- 前端页面加载正常，无控制台错误
- 智能助教聊天功能正常
- 视频生成功能正常
- 知识点可视化功能正常
- 题目管理功能正常

---

## 风险评估

### 低风险
- 所有修改为路由尾部斜杠一致性调整，不影响业务逻辑
- 前端调用方式不变，无需重新构建

### 潜在风险
- 第三方客户端或旧版前端可能使用不带斜杠的 URL
- 解决方案：后端同时支持带斜杠和不带斜杠的路由

---

## 后续优化建议

1. **统一路由规范**：制定项目路由规范，要求所有路由必须带尾部斜杠
2. **自动化测试**：添加 API 端点测试用例，确保前端后端路由一致
3. **Swagger 文档**：利用 FastAPI 自动生成的文档验证所有端点
4. **CI/CD 检查**：在 CI 流程中添加路由一致性检查
