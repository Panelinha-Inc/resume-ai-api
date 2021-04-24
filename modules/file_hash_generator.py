import hashlib

def generate_hash(file):
  '''
  Hash File Generator

  Parameters:
    file: The file object to generate hash

  Returns:
    string: Hexadecimal hash string from file
    bytes: The content bytes from file
    
  '''

  # Read bytes from file
  content = file.read()
  
  # Generate hash from file
  result = hashlib.md5(content)

  # Return the equivalent hexadecimal value
  return result.hexdigest(), content
