import os

from typing import Optional

from pydantic import BaseModel

from fastapi import FastAPI, File, UploadFile, Header, Depends

from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from modules.pdfConverter import pdfConverter
from modules.file_hash_generator import generate_hash
from modules.pyrebase_connector import PyrebaseConnector


class SignUpForm(BaseModel):
  email: str
  password: str
  displayName: Optional[str] = None


app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=['*'],
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*'],
)

security = HTTPBasic()

pc = PyrebaseConnector()


@app.get('/')
def hello_world():
  return {'hello': 'world'}

@app.post('/signup/', status_code=201)
def signup(sign_up_form: SignUpForm):
  user = pc.sign_up(sign_up_form.email, sign_up_form.password, sign_up_form.displayName)
  return user

@app.get('/login/')
def login(credentials: HTTPBasicCredentials = Depends(security)):
  return pc.login(credentials.username, credentials.password)

@app.post('/uploadfile/', status_code=201)
async def create_upload_file(user_id: str = Header(...), file: UploadFile = File(...)):
  # print(f'Original filename: {file.filename}')
  # print(f'Content type: {file.content_type}')
  
  content_type = file.content_type.split('/')[1]
  # print(f'Content type: {content_type}')
  
  new_filename, content = generate_hash(file.file)
  # print(f'New filename: {new_filename}')

  pdf_path = f'./uploaded_files/{new_filename}.{content_type}'

  with open(pdf_path, 'wb') as f:
    f.write(content)

  pdf_images = pdfConverter(pdf_path, poppler_path=r'poppler-0.68.0\bin')

  pc = PyrebaseConnector()
  result = pc.create_pdf(user_id, new_filename, pdf_images)

  if result == 201:
    return {'status': 'success'}
  else:
    return {'status': 'fail'}
