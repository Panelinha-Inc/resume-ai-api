import pyrebase
import json


class PyrebaseConnector(object):
  def __init__(self):
    # Check if an internet connection is present
    # self.is_connected()

    # Initialize Application Services
    self.firebase = self.initialize_app()

    # Get a reference to the auth service
    self.auth = self.firebase.auth()

    # Get a reference to the database service
    self.db = self.firebase.database()

    # Get a reference to the storage service
    self.storage = self.firebase.storage()

  # Initialize the app
  def initialize_app(self):
    with open('firebase_key.json', 'r') as f:
      config = json.load(f)

    return pyrebase.initialize_app(config)

  
  # Create a user
  def sign_up(self, email, password, displayName):
    try:
      self.user = self.auth.create_user_with_email_and_password(email, password)

      data = {
          'displayName': displayName
      }
      self.db.child('users').child(self.user['localId']).set(data)

      return 201

    except Exception as e:
      _error_json = e.args[1]
      _error = json.loads(_error_json)['error']
      return _error['message']

  # Log the user in application
  def login(self, email, password):
    try:
      self.user = self.auth.sign_in_with_email_and_password(email, password)
      return 200
    except Exception as e:
      _error_json = e.args[1]
      _error = json.loads(_error_json)['error']
      return _error['message']

  def update_user(self, displayName):
    try:
      data = {
        'displayName': displayName
      }
      self.db.child('users').child(self.auth.current_user['localId']).update(data)
      return 200
    except Exception as e:
      _error_json = e.args[1]
      _error = json.loads(_error_json)['error']
      return _error['message']

  def change_password(self, email):
    try:
      self.auth.send_password_reset_email(email)
      return 200
    except Exception as e:
      _error_json = e.args[1]
      _error = json.loads(_error_json)['error']
      return _error['message']

  # Register a PDF in database
  def create_pdf(self, ownerId, hash, pdf_images):
    # TO-DO
    # Esta tendo problema de permissão negada para salvar o arquivo
    for index in range(len(pdf_images)):
      self.storage.child(f'{index:02d}.png').put(f'images/{hash}_{index:02d}.png')
    data = {
      'pdfs': [hash]
    }
    self.db.child('users').child(ownerId).set(data)
    return 201