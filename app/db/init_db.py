import logging
from sqlalchemy.orm import Session
from app.db.base_class import Base
from app.db.session import engine
from app.models.player import Player
from app.models.game import Game

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    # 创建表
    logger.info("创建数据库表")
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表创建完成")