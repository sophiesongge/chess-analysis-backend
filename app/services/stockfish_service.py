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
    
    def evaluate_move(self, fen: str, move: str, depth: int = 20):
        """评估具体走法的质量"""
        try:
            transport = chess.engine.SimpleEngine.popen_uci(self.engine_path)
            board = chess.Board(fen)
            
            # 验证走法是否合法
            try:
                move_obj = board.parse_san(move)
            except ValueError:
                return {
                    "status": "error",
                    "message": "非法走法",
                    "evaluation": None
                }

            try:
                # 获取走子前的评分
                before_analysis = transport.analyse(board, chess.engine.Limit(depth=depth))
                if 'score' not in before_analysis:
                    return {
                        "status": "error",
                        "message": "无法获取走子前的评分",
                        "evaluation": None
                    }
                score_before = before_analysis['score']

                # 执行走法
                board.push(move_obj)
                
                # 获取走子后的评分
                after_analysis = transport.analyse(board, chess.engine.Limit(depth=depth))
                if 'score' not in after_analysis:
                    return {
                        "status": "error",
                        "message": "无法获取走子后的评分",
                        "evaluation": None
                    }
                score_after = after_analysis['score']
                
                # 计算走法的相对价值
                # 确保分数可以转换为整数
                try:
                    score_before_value = score_before.relative.score(mate_score=10000)
                    score_after_value = score_after.relative.score(mate_score=10000)
                    score_diff = score_after_value - score_before_value
                except (AttributeError, TypeError):
                    # 处理无法转换为数值的情况
                    return {
                        "status": "error",
                        "message": "无法计算分数差异",
                        "evaluation": None
                    }
                
                # 评估走法质量
                evaluation = {
                    "status": "success",
                    "move": move,
                    "score_before": score_before_value,
                    "score_after": score_after_value,
                    "score_difference": score_diff,
                    "quality": self._get_move_quality(score_diff),
                    "best_continuation": self._get_best_continuation(after_analysis),
                    "depth": depth
                }
                
                return evaluation
            
            finally:
                transport.quit()
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "evaluation": None
            }

    def _get_move_quality(self, score_diff: int) -> str:
        """根据分数差异评估走法质量"""
        if score_diff > 200:
            return "极佳"
        elif score_diff > 100:
            return "优秀"
        elif score_diff > 0:
            return "良好"
        elif score_diff > -100:
            return "一般"
        elif score_diff > -200:
            return "欠佳"
        else:
            return "差"

    def _get_best_continuation(self, analysis) -> list:
        """获取最佳后续走法"""
        if 'pv' in analysis:
            return [move.uci() for move in analysis['pv'][:3]]  # 返回前3步最佳后续
        return []