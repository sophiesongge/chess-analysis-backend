class Settings:
    PROJECT_NAME: str = "Chess Analysis API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost/chess_analysis"
    STOCKFISH_PATH: str = "/opt/homebrew/bin/stockfish"  # 更新为正确的路径

settings = Settings()