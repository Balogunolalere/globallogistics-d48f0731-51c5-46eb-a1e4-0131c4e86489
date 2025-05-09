from fastapi import FastAPI, Request, Form, status, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import EmailStr
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
# from deta import Deta

load_dotenv()

# Initialize Deta Base
# deta_project_key = os.getenv("APP_KEY")
# deta = Deta(deta_project_key)
# newsletter_db = deta.Base("global_newsletter")

# disable the docs
app = FastAPI(docs_url=None, redoc_url=None)

# Mount the directory "static" at the path "/static" in the application
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create a Jinja2Templates object with the directory "templates"
templates = Jinja2Templates(directory="templates")


# Define a route for the path "/" that returns the "index.html" template
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/about")
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact")
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.get("/terminal", name="terminal_page")
async def terminal(request: Request):
    return templates.TemplateResponse("terminal.html", {"request": request})

@app.get("/shipping", name="shipping_page")
async def shipping(request: Request):
    return templates.TemplateResponse("shipping.html", {"request": request})


def send_email(sender_email: str, receiver_email: str, login: str, password: str, fname: str, email: EmailStr, message: str):
    smtp_server = 'mail.privateemail.com'
    port = 465
    messagex = EmailMessage()
    messagex["Subject"] = "Contact Form"
    messagex["From"] = f"Global Logistic BV <{sender_email}>"
    messagex["To"] = receiver_email
    content = f"""
    <html>
    <body>
        <h2>Form</h2>
        <p><b>First Name:</b> {fname}</p>
        <p><b>Email:</b> {email}</p>
        <p><b>Message:</b></p>
        <p>{message}</p>
    </body>
    </html>
    """
    messagex.set_content(content, subtype='html')
    server = smtplib.SMTP_SSL(smtp_server, port)
    server.login(login, password)
    server.send_message(messagex)
    server.quit()

@app.post("/sendmail")
async def mail(background_tasks: BackgroundTasks, request: Request, fname: str = Form(...),  email: EmailStr = Form(...), message: str = Form(...)):
    print(fname, email, message)
    sender_email = os.getenv("HOST_EMAIL")
    receiver_email  = os.getenv("HOST_EMAIL")
    login = sender_email
    password = os.getenv("HOST_PASSWORD")
    background_tasks.add_task(send_email, sender_email, receiver_email, login, password, fname, email, message)
    resp = RedirectResponse(url="/contact", status_code=status.HTTP_302_FOUND)
    return resp

@app.get("/storage", name="storage_page")
async def storage(request: Request):
    return templates.TemplateResponse("storage.html", {"request": request})

# Define a route for the path "/rail-transport" that returns the "rail-transport.html" template
@app.get("/rail-transport", name="railway_page")
async def rail_transport(request: Request):
    return templates.TemplateResponse("railway.html", {"request": request})

# Define a route for the path "/pipeline-transport" that returns the "pipeline-transport.html" template
@app.get("/pipeline-transport", name="pipeline_page")
async def pipeline_transport(request: Request):
    return templates.TemplateResponse("pipeline.html", {"request": request})

@app.middleware("http")
async def fix_mime_type(request: Request, call_next):
    response = await call_next(request)
    content_types = {
        ".ttf" :"font/ttf",
        ".woff": "font/woff", 
        ".woff2": "font/woff2"
    }
    for e in content_types:
        if request.url.path.endswith(e): response.headers["Content-Type"] = content_types[e]
    return response

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)
    if response.status_code == 200:
        response.headers["Cache-Control"] = "public, max-age=1200"
    return response

# Define a route for the newsletter subscription
# @app.post("/subscribe")
# async def subscribe(request: Request, email: EmailStr = Form(...), consent: bool = Form(...)):
#     # Check if the email already exists in the database
#     existing_emails = newsletter_db.fetch({"email": email}).items
#     if existing_emails:
#         # If the email already exists, return an error response
#         return templates.TemplateResponse("email_exists.html", {"request": request, "email": email, "error": "This email is already subscribed."})
    
#     if consent:
#         # Insert the subscriber data into the Deta Base
#         newsletter_db.put({"email": email, "consent": consent})
#         # Send a confirmation email
#         smtp_server = 'mail.privateemail.com'
#         port = 465
#         messagexxx = EmailMessage()
#         messagexxx["Subject"] = "Welcome to Global Logistics Newsletter!"
#         messagexxx["From"] = f"Global Logistic BV <{os.getenv('HOST_EMAIL')}>"
#         messagexxx["To"] = email
#         content = f"""
#         <html>
#         <body>
#             <h2>You are subscribed to Global Logistics Newsletter!</h2>
#             <p>You are receiving this email because you have subscribed to our newsletter.</p>
#             <p>If you wish to unsubscribe, please click <a href="https://globallogisticsbv.com/unsubscribe?email={email}">here</a>.</p>
#         </body>
#         </html>
#         """
#         messagexxx.set_content(content, subtype='html')
#         server = smtplib.SMTP_SSL(smtp_server, port)
#         server.login(os.getenv('HOST_EMAIL'), os.getenv('HOST_PASSWORD'))
#         server.send_message(messagexxx)
#         server.quit()
#         # return the page
#         return templates.TemplateResponse("subscribed.html", {"request": request, "email": email})
#     else:
#         return templates.TemplateResponse("error.html", {"request": request, "email": email, "error": "Consent not given."})
    
# def unsubscribe_email(email):
#     # Fetch the item with the matching email
#     items = newsletter_db.fetch({"email": email}).items
#     if items:
#         # Get the key of the item
#         key = items[0]["key"]
#         # Delete the item from the database using the key
#         newsletter_db.delete(key)
#         return True
#     else:
#         return False
    
# @app.get("/unsubscribe")
# async def unsubscribe(request: Request, email: str):
#     # Try to unsubscribe the email
#     if unsubscribe_email(email):
#         return templates.TemplateResponse("unsubscribed.html", {"request": request, "email": email})
#     else:
#         return {"error": "Email not found in the database"}