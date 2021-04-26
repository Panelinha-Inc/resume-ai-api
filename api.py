from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from modules.file_hash_generator import generate_hash

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=['*'],
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*'],
)

@app.post('/uploadfile/', status_code=201)
async def create_upload_file(file: UploadFile = File(...)):
  # print(f'Original filename: {file.filename}')
  # print(f'Content type: {file.content_type}')
  
  content_type = file.content_type.split('/')[1]
  # print(f'Content type: {content_type}')
  
  new_filename, content = generate_hash(file.file)
  # print(f'New filename: {new_filename}')

  with open(f'./uploaded_files/{new_filename}.{content_type}', 'wb') as f:
    f.write(content)
