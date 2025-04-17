import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Chess Analysis API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", os.getenv("USER", "sophiesong"))  # 使用系统用户名作为默认值
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")  # macOS Homebrew 安装的 PostgreSQL 默认无密码
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "chess_analysis")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"
    )
    STOCKFISH_PATH: str = "/opt/homebrew/bin/stockfish"  # 更新为正确的路径
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()