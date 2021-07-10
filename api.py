import os

from typing import Optional

from pydantic import BaseModel

from fastapi import FastAPI, Form, File, UploadFile, Header, Depends

from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from modules.pdfConverter import pdfConverter
from modules.file_hash_generator import generate_hash
from modules.pyrebase_connector import PyrebaseConnector


class SignUpForm(BaseModel):
  email: str
  password: str
  displayName: Optional[str] = None

class ResetPasswordForm(BaseModel):
  email: str

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
  status_code, sign_up_data = pc.sign_up(sign_up_form.email, sign_up_form.password, sign_up_form.displayName)
  return {
    'status_code': status_code,
    'data': sign_up_data
  }

@app.get('/login/')
def login(credentials: HTTPBasicCredentials = Depends(security)):
  status_code, login_data = pc.login(credentials.username, credentials.password)
  return {
    'status_code': status_code,
    'data': login_data
  }

@app.put('/user/', status_code=200)
async def update_profile(displayName: str = Form(...), user_id: str = Header(...), token: str = Header(...), file: UploadFile = File(...)):
  result = pc.update_user(user_id, token, displayName, file)
  
  if result == 200:
    return {'status': 'success'}
  else:
    return {
      'status': 'fail',
      'data': result
    }

@app.post('/resetpassword/', status_code=200)
def reset_password(reset_password_form: ResetPasswordForm):
  result = pc.change_password(reset_password_form.email)
  
  if result == 200:
    return {'status': 'success'}
  else:
    return {
      'status': 'fail',
      'data': result
    }

@app.post('/uploadfile/', status_code=201)
async def create_upload_file(user_id: str = Header(...), token: str = Header(...), file: UploadFile = File(...)):
  content_type = file.content_type.split('/')[1]
  
  new_filename, content = generate_hash(file.file)

  pdf_path = f'./uploaded_files/{new_filename}.{content_type}'

  with open(pdf_path, 'wb') as f:
    f.write(content)

  pdf_images = pdfConverter(pdf_path, poppler_path=r'poppler-0.68.0\bin')
  os.remove(pdf_path)

  result = pc.create_pdf(user_id, token, new_filename, pdf_images)

  if result == 201:
    return {'status': 'success'}
  else:
    return {'status': 'fail'}

@app.get('/document/')
def get_document(fileId: str, user_id: str = Header(...)):
  return pc.search_pdf(user_id, fileId)