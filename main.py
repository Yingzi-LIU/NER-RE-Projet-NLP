from fastapi import FastAPI, Form, File, UploadFile, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import spacy
import wikipediaapi
import aiofiles

app = FastAPI()

# 加载spaCy法语模型
nlp = spacy.load("fr_core_news_sm")

wiki_wiki = wikipediaapi.Wikipedia(language='fr', user_agent="MyAppName/1.0 (myemail@example.com)")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze/")
async def analyze_text(text: str = Form(default=""), file: UploadFile = File(None)):
    if file:
        contents = await file.read()
        text = contents.decode("utf-8")
        await file.close()

    if not text:
        return {"error": "No text provided"}

        
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        wiki_page = wiki_wiki.page(ent.text)
        if wiki_page.exists():
            entities.append({"entity": ent.text, "type": ent.label_, "url": wiki_page.fullurl})
        else:
            entities.append({"entity": ent.text, "type": ent.label_, "url": None})
    return {"entities": entities}

