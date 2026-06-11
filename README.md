# 竞彩赔率优化器 (Odds Optimizer)

基于凯利准则的竞彩投注优化工具，自动计算最优盈亏比投注方案。

## 功能特点

- 实时抓取竞彩赔率数据
- 基于凯利准则计算最优投注比例
- 支持多种风险偏好（保守/适中/激进）
- 按预算生成最优投注组合
- EV评分排序，优先推荐高赔率正EV赛事

## 快速开始

### 使用 Docker

```bash
docker-compose up
```

访问 http://localhost:5173

### 本地开发

**后端：**

```bash
cd backend
pip install -e .
playwright install chromium
uvicorn app.main:app --reload
```

**前端：**

```bash
cd frontend
npm install
npm run dev
```

## API 文档

启动后端后访问 http://localhost:8000/docs

### 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/matches/ | 获取今日赛事 |
| GET | /api/matches/{match_id} | 获取赛事详情 |
| POST | /api/optimize/ | 生成最优投注方案 |
| GET | /api/history/ | 获取投注历史 |

### 优化请求示例

```json
{
  "budget": 500,
  "risk_level": "moderate",
  "max_matches": 5,
  "min_odds": 1.5,
  "max_odds": 20.0
}
```

## 核心算法

### 凯利准则 (Kelly Criterion)

```
f* = (p * b - q) / b
```

- `f*` = 最优投注比例
- `p` = 胜率估计
- `b` = 赔率 - 1
- `q` = 1 - p

### EV评分

```
score = EV * log(odds)
```

优先推荐：
1. 正期望值 (EV > 0)
2. 高赔率 (更多上行空间)

### 风险级别

| 级别 | 凯利比例 | 描述 |
|------|----------|------|
| 保守 | 25% | 四分之一凯利，低波动 |
| 适中 | 50% | 半凯利，平衡风险收益 |
| 激进 | 75% | 四分之三凯利，追求高回报 |

## 技术栈

- **后端**: Python 3.11+, FastAPI, Playwright, SQLite
- **前端**: React 18, TypeScript, Tailwind CSS, Vite
- **算法**: Kelly Criterion, Expected Value

## 项目结构

```
odds-optimizer/
├── backend/
│   ├── app/
│   │   ├── api/           # API 端点
│   │   ├── engine/        # 核心算法
│   │   ├── scrapers/      # 数据抓取
│   │   ├── models.py      # 数据模型
│   │   ├── database.py    # 数据库
│   │   └── main.py        # 应用入口
│   └── tests/             # 测试
├── frontend/
│   ├── src/
│   │   ├── components/    # React 组件
│   │   ├── lib/           # API 客户端
│   │   └── App.tsx        # 主应用
│   └── package.json
├── docker-compose.yml
└── README.md
```

## 风险说明

本工具仅供参考，不构成投注建议。彩票有风险，投注需谨慎。