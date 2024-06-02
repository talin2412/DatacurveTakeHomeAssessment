from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import docker

app = FastAPI()
client = docker.from_env()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the SQLAlchemy database URL
DATABASE_URL = "sqlite:///./code_runs.db"

# Create a database engine instance
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a DeclarativeMeta subclass
Base = declarative_base()

# Define a SQLAlchemy ORM model
class CodeRun(Base):
    __tablename__ = "code_runs"
    id = Column(Integer, primary_key=True, index=True, default=1)
    code = Column(String, nullable=False)
    result = Column(String, nullable=False)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Set up the session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/get_latest_code")
async def get_latest_code(db: Session = Depends(get_db)):
    db_code_run = db.query(CodeRun).filter(CodeRun.id == 1).first()
    if not db_code_run:
        raise HTTPException(status_code=404, detail="No code run found")
    response_data = {
        "code": db_code_run.code,
        "result": db_code_run.result,
    }
    return JSONResponse(content=response_data)

# Pydantic model for the request body
class CodeRunCreate(BaseModel):
    code: str

@app.post("/run_code")
async def run_code(code_run: CodeRunCreate):
    code = code_run.code  
    try:
        # Run the code in a Docker container
        container = client.containers.run(
            "python-exec-env",  # Use the image created earlier or python:3.11
            command=["python", "-c", code],
            detach=True,
            remove=False,
            stdout=True,
            stderr=True
        )
        # Wait for the container to finish executing
        result = container.wait(timeout=5)
        exit_status = result['StatusCode']
        # Retrieve logs after the container has stopped
        output = container.logs(stdout=True, stderr=True).decode('utf-8')
        container.remove()  # Clean up by removing the container manually
        response_data = {
            "result": output,
            "status": exit_status,
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        container.stop()
        container.remove()
        raise HTTPException(status_code=400, detail={str(e)})

@app.post("/submit_code")
async def submit_code(code_run: CodeRunCreate, db: Session = Depends(get_db)):
    code = code_run.code  
    try:
        # Run the code in a Docker container
        container = client.containers.run(
            "python-exec-env",  # Use the image created earlier or python:3.11
            command=["python", "-c", code],
            detach=True,
            remove=False,
            stdout=True,
            stderr=True
        )
        # Wait for the container to finish executing
        result = container.wait(timeout=5)
        exit_status = result['StatusCode']
        # Retrieve logs after the container has stopped
        output = container.logs(stdout=True, stderr=True).decode('utf-8')
        container.remove()  # Clean up by removing the container manually
        if (exit_status == 0):
            db_code_run = db.query(CodeRun).filter(CodeRun.id == 1).first()
            if db_code_run:
                db_code_run.code = code
                db_code_run.result = output
            else:
                db_code_run = CodeRun(id=1, code=code, result=output)
                db.add(db_code_run)
            db.commit()
            db.refresh(db_code_run)

        response_data = {
            "result": output,
            "status": exit_status,
        }
        return JSONResponse(content=response_data)
    except Exception as e:
        container.stop()
        container.remove()
        raise HTTPException(status_code=400, detail={str(e)})
