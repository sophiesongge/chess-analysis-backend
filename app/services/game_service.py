from sqlalchemy.orm import Session
from sqlalchemy import func
import re
from typing import Optional
from app.models.game import Game
from app.models.player import Player

class GameService:
    def __init__(self):
        pass
    
    def save_game(self, db: Session, fen: str, pgn: str, name: Optional[str] = None, 
                 white_player: Optional[str] = None, black_player: Optional[str] = None):
        """保存棋局"""
        # 处理默认名称
        if not name or name.startswith("ChessGame_"):
            name = self._generate_default_name(db)
        
        # 处理棋手
        white_player_id = None
        black_player_id = None
        
        if white_player:
            white_player_obj = self._get_or_create_player(db, white_player)
            white_player_id = white_player_obj.id
            
        if black_player:
            black_player_obj = self._get_or_create_player(db, black_player)
            black_player_id = black_player_obj.id
        
        # 创建新游戏
        game = Game(
            name=name,
            fen=fen,
            pgn=pgn,
            white_player_id=white_player_id,
            black_player_id=black_player_id
        )
        
        db.add(game)
        db.commit()
        db.refresh(game)
        
        return game
    
    def _generate_default_name(self, db: Session) -> str:
        """生成默认游戏名称"""
        # 查找最后一个默认名称的游戏
        pattern = r'ChessGame_(\d+)'
        last_game = db.query(Game).filter(
            Game.name.op('~')(pattern)
        ).order_by(Game.id.desc()).first()
        
        counter = 1
        if last_game is not None:
            game_name = str(last_game.name) if last_game.name is not None else ""
            match = re.match(pattern, game_name)
            if match:
                counter = int(match.group(1)) + 1
            
        return f"ChessGame_{counter}"
    
    def _get_or_create_player(self, db: Session, player_name: str):
        """获取或创建棋手"""
        # 标准化名称 (首字母大写)
        normalized_name = self._normalize_player_name(player_name)
        
        # 查找现有棋手
        player = db.query(Player).filter(
            func.lower(Player.name) == func.lower(normalized_name)
        ).first()
        
        # 如果不存在，创建新棋手
        if not player:
            player = Player(name=normalized_name)
            db.add(player)
            db.commit()
            db.refresh(player)
            
        return player
    
    def _normalize_player_name(self, name: str) -> str:
        """标准化棋手名称"""
        # 将名字按空格分割，每个部分首字母大写
        parts = name.strip().split()
        normalized_parts = [part.capitalize() for part in parts]
        return " ".join(normalized_parts)
    
    def get_player_suggestions(self, db: Session, prefix: str):
        """根据前缀获取棋手建议"""
        if not prefix or len(prefix) < 2:
            return []
            
        # 不区分大小写搜索
        players = db.query(Player).filter(
            func.lower(Player.name).like(f"{prefix.lower()}%")
        ).all()
        
        return [player.name for player in players]
    
    def get_games(self, db: Session, skip: int = 0, limit: int = 100):
        """获取所有棋局"""
        return db.query(Game).order_by(Game.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_game(self, db: Session, game_id: int):
        """获取特定棋局"""
        return db.query(Game).filter(Game.id == game_id).first()