# 国际象棋分析后端服务

这是一个基于 FastAPI 和 Stockfish 引擎的国际象棋分析后端服务，提供棋局分析功能。

## 技术栈

- **FastAPI**: 高性能的 Python Web 框架
- **Stockfish**: 强大的开源国际象棋引擎
- **SQLAlchemy**: ORM 数据库工具
- **PostgreSQL**: 关系型数据库

## 功能特性

- 棋局分析 API
- FEN 字符串解析
- 最佳走法推荐
- 局面评估

## 安装步骤

1. 克隆仓库

```bash
git clone https://github.com/sophiesongge/chess-analysis-backend.git
cd chess-analysis-backend

2. python -m venv venv
source venv/bin/activate  # MacOS/Linux

3. pip install fastapi uvicorn sqlalchemy python-chess psycopg2-binary

4. # MacOS
brew install stockfish

# Ubuntu
sudo apt install stockfish

5. createdb chess_analysis

6. uvicorn app.main:app --reload

服务将在 http://localhost:8000 启动，API 文档可在 http://localhost:8000/docs 查看。

## API 端点
- GET / : 服务状态检查
- POST /analyze : 分析棋局位置
  - 参数: {"fen": "棋局FEN字符串", "depth": 分析深度}

7. 