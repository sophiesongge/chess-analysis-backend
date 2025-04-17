from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.services.stockfish_service import StockfishService
from app.services.opening_service import OpeningService
from app.services.game_service import GameService
from app.db.init_db import init_db

class AnalysisRequest(BaseModel):
    fen: str
    depth: int = 20

# 创建一个带有/api前缀的路由器
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 创建服务实例
stockfish_service = StockfishService()
opening_service = OpeningService()

@app.get("/")
def read_root():
    return {"message": "Chess Analysis API"}

@app.get("/analyze")
def analyze_position_get():
    return {
        "message": "请使用 POST 方法发送 FEN 字符串进行分析",
        "example": {
            "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        }
    }

@app.post("/analyze")
def analyze_position(request: AnalysisRequest, db: Session = Depends(get_db)):
    try:
        result = stockfish_service.analyze_position(request.fen, request.depth)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/best-move")
def get_best_move(request: AnalysisRequest):
    try:
        result = stockfish_service.get_best_move(request.fen)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 修改开局识别路由，添加/api前缀
@app.post("/api/identify-opening")
def identify_opening(request: AnalysisRequest):
    try:
        result = opening_service.identify_opening(request.fen)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 保留原来的路由以保持兼容性
@app.post("/identify-opening")
def identify_opening_legacy(request: AnalysisRequest):
    try:
        result = opening_service.identify_opening(request.fen)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class MoveEvaluationRequest(BaseModel):
    fen: str
    move: str
    depth: int = 20

@app.post("/api/evaluate-move")
def evaluate_move(request: MoveEvaluationRequest):
    try:
        result = stockfish_service.evaluate_move(
            request.fen,
            request.move,
            request.depth
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 创建游戏服务实例
game_service = GameService()

# 请求模型
class SaveGameRequest(BaseModel):
    fen: str
    pgn: str
    name: Optional[str] = None
    white_player: Optional[str] = None
    black_player: Optional[str] = None

class PlayerSuggestionRequest(BaseModel):
    prefix: str

# API路由
@app.post("/api/save-game")
def save_game(request: SaveGameRequest, db: Session = Depends(get_db)):
    try:
        game = game_service.save_game(
            db=db,
            fen=request.fen,
            pgn=request.pgn,
            name=request.name,
            white_player=request.white_player,
            black_player=request.black_player
        )
        
        return {
            "status": "success",
            "game_id": game.id,
            "name": game.name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/player-suggestions")
def get_player_suggestions(request: PlayerSuggestionRequest, db: Session = Depends(get_db)):
    try:
        suggestions = game_service.get_player_suggestions(db, request.prefix)
        return {
            "status": "success",
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/games")
def get_games(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        games = game_service.get_games(db, skip, limit)
        return {
            "status": "success",
            "games": [
                {
                    "id": game.id,
                    "name": game.name,
                    "white_player": game.white_player.name if game.white_player else None,
                    "black_player": game.black_player.name if game.black_player else None,
                    "created_at": game.created_at
                }
                for game in games
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/games/{game_id}")
def get_game(game_id: int, db: Session = Depends(get_db)):
    try:
        game = game_service.get_game(db, game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
            
        return {
            "status": "success",
            "game": {
                "id": game.id,
                "name": game.name,
                "fen": game.fen,
                "pgn": game.pgn,
                "white_player": game.white_player.name if game.white_player else None,
                "black_player": game.black_player.name if game.black_player else None,
                "created_at": game.created_at
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 在应用启动时初始化数据库
@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    try:
        init_db(db)
    finally:
        db.close()

# 添加一个新的路由，处理 /games 请求
@app.post("/games")
def save_game_alternative(request: dict, db: Session = Depends(get_db)):
    try:
        # 打印请求内容以便调试
        print(f"Received request: {request}")
        
        # 尝试从请求中提取数据
        fen = request.get("fen") or request.get("position", "")
        pgn_data = request.get("pgn") or request.get("moveHistory", "")  # 添加对 moveHistory 的支持
        name = request.get("name", None)
        white_player = request.get("white_player") or request.get("whitePlayer", None)  # 修正大小写
        black_player = request.get("black_player") or request.get("blackPlayer", None)  # 修正大小写
        
        # 确保必要的数据存在
        if not fen:
            raise HTTPException(status_code=400, detail="Missing required field: fen/position")
        
        # 将 pgn_data 转换为字符串
        if pgn_data is None:
            pgn = ""
        elif isinstance(pgn_data, list):
            # 如果是列表，将其转换为字符串
            pgn = " ".join(str(move) for move in pgn_data) if pgn_data else ""
        elif isinstance(pgn_data, str) and pgn_data.startswith('['):
            # 如果是 JSON 字符串，尝试解析
            import json
            try:
                moves = json.loads(pgn_data)
                pgn = " ".join(str(move) for move in moves) if moves else ""
            except:
                pgn = pgn_data  # 如果解析失败，保持原样
        else:
            pgn = str(pgn_data)  # 其他情况转换为字符串
        
        game = game_service.save_game(
            db=db,
            fen=fen,
            pgn=pgn,
            name=name,
            white_player=white_player,
            black_player=black_player
        )
        
        return {
            "status": "success",
            "game_id": game.id,
            "name": game.name
        }
    except Exception as e:
        print(f"Error saving game: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))