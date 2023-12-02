from fastapi import FastAPI, Request, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Database
DATABASE_URL = "sqlite:///./database/users.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Create Table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)


Base.metadata.create_all(bind=engine)

# Mount Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 Templates
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_file(csv_file: UploadFile = File(...)):
    try:
        content = await csv_file.read()

        try:
            decoded_content = content.decode('utf-8')
        except UnicodeDecodeError:
            decoded_content = content.decode('latin-1')

        rows = decoded_content.split('\n')[1:]

        db = SessionLocal()

        for row in rows:
            if row:
                values = row.split(',')
                if len(values) == 2:
                    user = User(name=values[0], age=int(values[1]))
                    db.add(user)
                else:
                    print(f"Ignoring invalid row: {row}")
        db.commit()
        db.close()

        return {"message": "User data saved successfully"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
