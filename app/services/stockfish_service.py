import chess
import chess.engine
import os
from app.core.config import settings

class StockfishService:
    def __init__(self):
        self.engine_path = settings.STOCKFISH_PATH
        if not os.path.exists(self.engine_path):
            raise Exception(f"Stockfish not found at {self.engine_path}")
        
    def analyze_position(self, fen: str, depth: int = 20):
        try:
            transport = chess.engine.SimpleEngine.popen_uci(self.engine_path)
            board = chess.Board(fen)
            
            try:
                result = transport.analyse(board, chess.engine.Limit(depth=depth))
                return {
                    "score": str(result["score"].relative) if "score" in result else None,
                    "best_move": result["pv"][0].uci() if "pv" in result and result["pv"] else None
                }
            except Exception as e:
                raise Exception(f"Analysis error: {str(e)}")
            finally:
                transport.quit()
        except Exception as e:
            raise Exception(f"Stockfish error: {str(e)}")