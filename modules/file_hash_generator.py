import hashlib

from fastapi import File, UploadFile

async def generate_hash(file: UploadFile = File(...)):
  '''
  Hash File Generator

  Parameters:
    file: The file object to generate hash

  Returns:
    string: Hexadecimal hash string from file
    bytes: The content bytes from file
    
  '''

  # Read bytes from file
  content = await file.read()
  
  # Generate hash from file
  result = hashlib.md5(content)

  # Return the equivalent hexadecimal value
  return result.hexdigest(), content
