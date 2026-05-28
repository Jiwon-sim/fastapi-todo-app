from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite 데이터베이스 파일 경로 지정
SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"

# DB 엔진 생성 (SQLite의 경우 멀티스레드 활성화 설정 필요)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 데이터베이스 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# DB 모델의 기반이 되는 Base 클래스 생성
Base = declarative_base()

# DB 세션을 가져오는 의존성 주입 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
