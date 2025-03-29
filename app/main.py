from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.services.stockfish_service import StockfishService
from app.services.opening_service import OpeningService

class AnalysisRequest(BaseModel):
    fen: str
    depth: int = 20

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

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

@app.post("/identify-opening")
def identify_opening(request: AnalysisRequest):
    try:
        result = opening_service.identify_opening(request.fen)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))