from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

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
  print(file.filename)
  print(file.content_type)

  with open(file.filename, 'wb') as f:
    contents = await file.read()
    f.write(contents)
