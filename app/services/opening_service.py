import chess
import chess.pgn
import io
import os
import json
import requests
from pathlib import Path

class OpeningService:
    def __init__(self):
        # 使用相对路径替代绝对路径
        current_dir = Path(__file__).parent.parent.parent  # 从 app/services 向上三级到项目根目录
        self.data_dir = current_dir / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.eco_file = self.data_dir / "eco.json"
        
        # 加载或下载开局数据库
        self.openings = self._load_openings()
        
    def _download_eco_database(self):
        """下载 ECO 开局数据库"""
        print("正在下载并整合 Lichess 开局数据库...")
        
        # Lichess 开局数据库的 TSV 文件
        tsv_files = [
            "https://raw.githubusercontent.com/lichess-org/chess-openings/master/a.tsv",
            "https://raw.githubusercontent.com/lichess-org/chess-openings/master/b.tsv",
            "https://raw.githubusercontent.com/lichess-org/chess-openings/master/c.tsv",
            "https://raw.githubusercontent.com/lichess-org/chess-openings/master/d.tsv",
            "https://raw.githubusercontent.com/lichess-org/chess-openings/master/e.tsv"
        ]
        
        all_openings = []
        
        try:
            for url in tsv_files:
                response = requests.get(url)
                response.raise_for_status()
                
                # 解析 TSV 文件
                lines = response.text.strip().split('\n')
                for line in lines:
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 3:
                            eco_code = parts[0].strip()
                            name = parts[1].strip()
                            pgn = parts[2].strip()
                            
                            all_openings.append({
                                "eco": eco_code,
                                "name": name,
                                "pgn": pgn
                            })
            
            # 保存整合后的数据到 JSON 文件
            with open(self.eco_file, "w", encoding="utf-8") as f:
                json.dump(all_openings, f, ensure_ascii=False, indent=2)
                
            print(f"成功下载并整合了 {len(all_openings)} 个开局")
            return all_openings
        except Exception as e:
            print(f"下载或整合开局数据库失败: {str(e)}")
            return []
        
    def _load_openings(self):
        """加载开局数据库"""
        # 如果本地文件不存在，则下载
        if not self.eco_file.exists():
            eco_data = self._download_eco_database()
        else:
            # 从本地文件加载
            try:
                with open(self.eco_file, "r", encoding="utf-8") as f:
                    eco_data = json.load(f)
            except Exception as e:
                print(f"加载 ECO 数据库失败: {str(e)}")
                eco_data = []
        
        # 将 PGN 转换为棋盘位置
        openings_dict = {}
        for opening in eco_data:
            try:
                pgn_text = opening.get("pgn", "")
                if not pgn_text:
                    continue
                    
                # 添加游戏头信息以便 python-chess 解析
                full_pgn = f'[Event "ECO"]\n[ECO "{opening.get("eco", "")}"]\n[Opening "{opening.get("name", "")}"]\n\n{pgn_text} *'
                
                pgn = io.StringIO(full_pgn)
                game = chess.pgn.read_game(pgn)
                
                if not game:
                    continue
                    
                board = game.board()
                
                # 执行所有走法
                for move in game.mainline_moves():
                    board.push(move)
                
                # 存储 FEN 和开局信息的映射
                fen = board.fen()
                openings_dict[fen] = {
                    "name": opening.get("name", "未知开局"),
                    "code": opening.get("eco", ""),
                    "pgn": pgn_text
                }
            except Exception as e:
                # 忽略解析错误
                continue
                
        # 如果数据库为空，使用备用数据
        if not openings_dict:
            openings_dict = self._load_backup_openings()
            
        return openings_dict
    
    def _load_backup_openings(self):
        """加载备用开局数据"""
        # 基本开局数据
        eco_data = [
            {"eco": "A00", "name": "波兰防御", "pgn": "1. b4"},
            {"eco": "A02", "name": "鸟开局", "pgn": "1. f4"},
            {"eco": "A04", "name": "雷蒂开局", "pgn": "1. Nf3"},
            {"eco": "A10", "name": "英国开局", "pgn": "1. c4"},
            {"eco": "A40", "name": "女王兵开局", "pgn": "1. d4"},
            {"eco": "A45", "name": "印度防御", "pgn": "1. d4 Nf6"},
            {"eco": "A80", "name": "荷兰防御", "pgn": "1. d4 f5"},
            {"eco": "B00", "name": "国王兵开局", "pgn": "1. e4"},
            {"eco": "B01", "name": "斯堪的纳维亚防御", "pgn": "1. e4 d5"},
            {"eco": "B02", "name": "阿列欣防御", "pgn": "1. e4 Nf6"},
            {"eco": "B07", "name": "皮尔茨防御", "pgn": "1. e4 d6"},
            {"eco": "B20", "name": "西西里防御", "pgn": "1. e4 c5"},
            {"eco": "B30", "name": "西西里防御老西西里变例", "pgn": "1. e4 c5 2. Nf3 Nc6"},
            {"eco": "C00", "name": "法国防御", "pgn": "1. e4 e6"},
            {"eco": "C10", "name": "法国防御保尔森变例", "pgn": "1. e4 e6 2. d4 d5 3. Nc3"},
            {"eco": "C20", "name": "国王兵对称开局", "pgn": "1. e4 e5"},
            {"eco": "C40", "name": "国王骑士开局", "pgn": "1. e4 e5 2. Nf3"},
            {"eco": "C42", "name": "俄罗斯防御", "pgn": "1. e4 e5 2. Nf3 Nf6"},
            {"eco": "C44", "name": "国王兵开局", "pgn": "1. e4 e5 2. Nf3 Nc6"},
            {"eco": "C60", "name": "西班牙开局", "pgn": "1. e4 e5 2. Nf3 Nc6 3. Bb5"},
            {"eco": "C65", "name": "西班牙开局柏林防御", "pgn": "1. e4 e5 2. Nf3 Nc6 3. Bb5 Nf6"},
            {"eco": "C70", "name": "西班牙开局关闭变例", "pgn": "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4"},
            {"eco": "D00", "name": "女王兵开局", "pgn": "1. d4 d5"},
            {"eco": "D06", "name": "女王兵对称开局", "pgn": "1. d4 d5 2. c4"},
            {"eco": "D30", "name": "女王兵士开局", "pgn": "1. d4 d5 2. c4 e6"},
            {"eco": "D70", "name": "格林菲尔德防御", "pgn": "1. d4 Nf6 2. c4 g6 3. g3"},
            {"eco": "E00", "name": "加塔兰开局", "pgn": "1. d4 Nf6 2. c4 e6 3. g3"},
            {"eco": "E10", "name": "印度防御", "pgn": "1. d4 Nf6 2. c4 e6"},
            {"eco": "E60", "name": "国王印度防御", "pgn": "1. d4 Nf6 2. c4 g6"}
        ]
        
        openings_dict = {}
        for opening in eco_data:
            try:
                # 修改 PGN 格式，确保兼容性
                moves_text = opening["pgn"]
                
                # 创建新的棋盘
                board = chess.Board()
                
                # 手动解析和应用走法
                moves = moves_text.split()
                for i in range(0, len(moves), 3):
                    if i + 1 < len(moves):
                        move_text = moves[i + 1]  # 跳过走法编号，如 "1."
                        try:
                            move = board.parse_san(move_text)
                            board.push(move)
                        except ValueError as e:
                            print(f"无法解析走法 {move_text}: {str(e)}")
                            continue
                
                # 存储 FEN 和开局信息
                fen = board.fen()
                openings_dict[fen] = {
                    "name": opening["name"],
                    "code": opening["eco"],
                    "pgn": opening["pgn"]
                }
            except Exception as e:
                print(f"处理开局 {opening['name']} 时出错: {str(e)}")
                
        return openings_dict
    
    def identify_opening(self, fen: str):
        """识别开局"""
        try:
            board = chess.Board(fen)
            
            # 尝试直接匹配
            if board.fen() in self.openings:
                return self.openings[board.fen()]
            
            # 如果没有直接匹配，尝试匹配位置部分
            position_fen = ' '.join(board.fen().split(' ')[:2])  # 只保留位置和行动方
            
            for stored_fen, opening_info in self.openings.items():
                stored_position = ' '.join(stored_fen.split(' ')[:2])
                if position_fen == stored_position:
                    return opening_info
            
            # 如果还是没有匹配，返回未知开局
            return {"name": "未知开局", "code": "", "pgn": ""}
        except Exception as e:
            return {"name": "开局识别错误", "code": "", "error": str(e)}