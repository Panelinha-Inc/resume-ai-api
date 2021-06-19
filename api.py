from fastapi import FastAPI, File, UploadFile, Header
from fastapi.middleware.cors import CORSMiddleware

from modules.file_hash_generator import generate_hash
from modules.pdfConverter import pdfConverter
from modules.pyrebase_connector import PyrebaseConnector

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=['*'],
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*'],
)

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
