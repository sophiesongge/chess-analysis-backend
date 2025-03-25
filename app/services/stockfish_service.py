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
                # 获取详细分析
                result = transport.analyse(board, chess.engine.Limit(depth=depth))
                
                # 获取最佳走法（不需要深度分析）
                best_move = transport.play(board, chess.engine.Limit(time=0.1))
                
                return {
                    "score": str(result["score"].relative) if "score" in result else None,
                    "best_move": best_move.move.uci() if best_move.move else None,
                    "pv": [move.uci() for move in result.get("pv", [])][:5] if "pv" in result else []
                }
            except Exception as e:
                raise Exception(f"Analysis error: {str(e)}")
            finally:
                transport.quit()
        except Exception as e:
            raise Exception(f"Stockfish error: {str(e)}")
    
    def get_best_move(self, fen: str, time_limit: float = 0.1):
        """
        快速获取最佳走法，不进行深度分析
        """
        try:
            transport = chess.engine.SimpleEngine.popen_uci(self.engine_path)
            board = chess.Board(fen)
            
            try:
                result = transport.play(board, chess.engine.Limit(time=time_limit))
                return {
                    "best_move": result.move.uci() if result.move else None
                }
            finally:
                transport.quit()
        except Exception as e:
            raise Exception(f"Stockfish error: {str(e)}")