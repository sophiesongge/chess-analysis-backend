# 国际象棋分析后端

这是一个基于 FastAPI 和 Stockfish 的国际象棋分析后端服务，提供棋局分析、最佳走法推荐、开局识别以及棋局存储功能。

## 功能特性

- 棋局分析
- 最佳走法推荐
- 开局识别
- 走法评估
- 棋局存储与检索
- 棋手管理

## 环境要求

- Python 3.8+
- PostgreSQL 数据库
- Stockfish 引擎

## 安装步骤

1. 克隆仓库

```bash
git clone https://github.com/yourusername/chess_analysis_backend.git
cd chess_analysis_backend

2. python -m venv venv
source venv/bin/activate  # MacOS/Linux

3. 安装依赖：pip install -r requirements.txt
pip install fastapi uvicorn sqlalchemy python-chess psycopg2-binary

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
## 安装与运行

### 环境要求

- Python 3.8+
- pip

### 安装依赖

```bash
pip install -r requirements.txt

8. 前端集成实例：
// 开局识别API调用
const identifyOpening = async (fen: string) => {
  try {
    const response = await axios.post(`${API_URL}/api/identify-opening`, { fen });
    return response.data;
  } catch (error) {
    console.error('开局识别错误:', error);
    throw error;
  }
};

// 使用示例
const handleIdentifyOpening = async () => {
  const result = await identifyOpening(chess.fen());
  console.log(`开局: ${result.name} (${result.code})`);
};

9. PostgreSQL数据库设置

安装：brew install postgresql
启动：brew services start postgresql
创建数据库：createdb chess_analysis
如果需要使用特定用户和密码，可以执行一下命令：psql postgres
在 PostgreSQL 命令行中执行：
CREATE USER chess_user WITH PASSWORD 'your_password';
CREATE DATABASE chess_analysis;
GRANT ALL PRIVILEGES ON DATABASE chess_analysis TO chess_user;
\q

配置数据库连接：
在 app/config.py 中，设置数据库连接字符串：
SQLALCHEMY_DATABASE_URL = "postgresql://chess_user:your_password@localhost/chess_analysis"
替换为您的实际数据库连接信息。

创建 .env文件并设置数据库连接信息：
POSTGRES_SERVER=localhost
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=chess_analysis
如果使用默认设置（系统用户名，无密码），则无需创建 .env 文件。

初始化数据库表
运行初始化脚本创建数据库表：
python scripts/create_db.py

10. 
## API 文档
启动服务后，可以访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
## API 端点
### 棋局分析
- POST /analyze - 分析棋局位置
- POST /best-move - 获取最佳走法
- POST /api/identify-opening - 识别开局
- POST /api/evaluate-move - 评估特定走法
### 棋局管理
- POST /api/save-game 或 POST /games - 保存棋局
- GET /api/games - 获取所有棋局列表
- GET /api/games/{game_id} - 获取特定棋局详情
### 棋手管理
- POST /api/player-suggestions - 获取棋手名称建议

## 请求示例
### 保存棋局
POST /games
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "moveHistory": ["e4", "e5", "Nf3", "Nc6"],
  "name": "我的第一盘棋",
  "whitePlayer": "Magnus Carlsen",
  "blackPlayer": "Hikaru Nakamura"
}

分析棋局
POST /analyze
{
  "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
  "depth": 20
}

## 数据库模型
### 棋局 (Game)
- id : 主键
- name : 棋局名称
- fen : 棋局 FEN 字符串
- pgn : 棋局 PGN 记录
- white_player_id : 白方棋手 ID
- black_player_id : 黑方棋手 ID
- created_at : 创建时间
### 棋手 (Player)
- id : 主键
- name : 棋手名称
- created_at : 创建时间
## 贡献指南
1. Fork 仓库
2. 创建特性分支 ( git checkout -b feature/amazing-feature )
3. 提交更改 ( git commit -m 'Add some amazing feature' )
4. 推送到分支 ( git push origin feature/amazing-feature )
5. 创建 Pull Request


11. 运行后端服务：uvicorn app.main:app --reload
