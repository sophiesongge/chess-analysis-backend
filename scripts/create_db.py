import logging
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.init_db import init_db
from app.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main() -> None:
    logger.info("创建初始数据")
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    logger.info("初始数据创建完成")

if __name__ == "__main__":
    main()