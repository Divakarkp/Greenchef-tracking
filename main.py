# app/main.py

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
import os
import uuid
from app.supabase_client import supabase
from app.utils import generate_barcode

app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/barcodes", StaticFiles(directory="app/barcodes"), name="barcodes")

# Set template directory
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/generate", response_class=HTMLResponse)
def generate_get(request: Request):
    return templates.TemplateResponse("generate.html", {"request": request})

@app.post("/generate", response_class=HTMLResponse)
def generate_post(request: Request, sku: str = Form(...), product_name: str = Form(...), items_per_box: int = Form(...)):
    box_code = f"BX{uuid.uuid4().hex[:8].upper()}"
    barcode_path = generate_barcode(box_code)

    # Insert box into Supabase
    supabase.table("boxes").insert({
        "box_code": box_code,
        "sku": sku,
        "product_name": product_name,
        "items_per_box": items_per_box
    }).execute()

    return templates.TemplateResponse("generate.html", {"request": request, "barcode_path": barcode_path, "box_code": box_code})

@app.get("/dispatch", response_class=HTMLResponse)
def dispatch_get(request: Request):
    return templates.TemplateResponse("dispatch.html", {"request": request, "scanned_boxes": []})

@app.post("/dispatch", response_class=HTMLResponse)
def dispatch_post(request: Request, box_code: str = Form(...)):
    # Insert dispatch record into Supabase
    supabase.table("dispatch_records").insert({
        "box_code": box_code,
        "dispatch_location": "Bengaluru Office"
    }).execute()

    return RedirectResponse(url="/dispatch", status_code=303)

@app.get("/receive", response_class=HTMLResponse)
def receive_get(request: Request):
    return templates.TemplateResponse("receive.html", {"request": request, "scanned_boxes": []})

@app.post("/receive", response_class=HTMLResponse)
def receive_post(request: Request, box_code: str = Form(...)):
    # Insert receive record into Supabase
    supabase.table("receive_records").insert({
        "box_code": box_code,
        "receive_location": "Mumbai Warehouse"
    }).execute()

    return RedirectResponse(url="/receive", status_code=303)

# app/main.py

from fastapi import FastAPI
from app.supabase_client import supabase

app = FastAPI()

@app.get("/")
def root():
    response = supabase.table("boxes").select("*").limit(1).execute()
    return response.data
