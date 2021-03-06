import os
import json
import shutil
import pyrebase


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
      user = self.auth.create_user_with_email_and_password(email, password)
      
      profile_pic = self.storage.child('profile_images/blank-profile-pic.png').get_url(user['idToken'])
      
      data = {
          'displayName': displayName if displayName else email,
          'profilePic': profile_pic,
      }
      self.db.child('users').child(user['localId']).set(data)

      user['displayName'] = data['displayName']
      user['profilePic'] = data['profilePic']

      return 201, user

    except Exception as e:
      _error_json = e.args[1]
      _error = json.loads(_error_json)['error']
      return 401, _error['message']

  # Log the user in application
  def login(self, email, password):
    try:
      user = self.auth.sign_in_with_email_and_password(email, password)
      user['displayName'] = self.db.child('users').child(user['localId']).child('displayName').get().val()
      user['profilePic'] = self.db.child('users').child(user['localId']).child('profilePic').get().val()
      return 200, user
    except Exception as e:
      _error_json = e.args[1]
      _error = json.loads(_error_json)['error']
      return 401, _error['message']

  def update_user(self, ownerId, token, displayName, profilePic):
    try:
      content_type = profilePic.content_type.split('/')[1]
      
      with open(f'images/{ownerId}.{content_type}', 'wb') as f:
        f.write(profilePic.file.read())

      self.storage.child(f'profile_images/{ownerId}/img_{ownerId}').put(f'images/{ownerId}.{content_type}', token)

      os.remove(f'images/{ownerId}.{content_type}')
      
      profilePic = self.storage.child(f'profile_images/{ownerId}/img_{ownerId}').get_url(token)
      
      data = {
        'displayName': displayName,
        'profilePic': profilePic,
      }

      self.db.child('users').child(ownerId).update(data, token)
      
      return 200
    except Exception as e:
      _error_json = e.args[1]
      _error = json.loads(_error_json)['error']
      return _error

  def change_password(self, email):
    try:
      self.auth.send_password_reset_email(email)
      return 200
    except Exception as e:
      _error_json = e.args[1]
      _error = json.loads(_error_json)['error']
      return _error['message']

  # Register a PDF in database
  def create_pdf(self, ownerId, token, hash, pdf_images, pdf_info):
    self.db.child('users').child(ownerId).child('pdfs').child(hash).set({'status': 'processing'})
    
    for index in range(len(pdf_images)):
      self.storage.child(f'pdf_images/{ownerId}/{hash}/{index:02d}.png').put(f'images/{hash}/{index:02d}.png')
    
    shutil.rmtree(f'images/{hash}/')

    pdf_info['pages'] = [
      self.storage.child(f'pdf_images/{ownerId}/{hash}/{index:02d}.png').get_url(token) for index in range(len(pdf_images))
    ]

    pdf_info['status'] = 'processed'
    
    self.db.child('users').child(ownerId).child('pdfs').child(hash).set(pdf_info)
    
    return 201

  # Search all URL imgaes of a PDF
  def search_pdf(self, ownerId, hash, token):
    return self.db.child(f'users/{ownerId}/pdfs/{hash}').get(token).val()

  def index_pdf(self, ownerId, token):
    user_pdfs = self.db.child(f'users/{ownerId}/pdfs').get(token)
    user_pdfs_dict = []
    
    for user in user_pdfs.each():
      data = user.val()
      data['fileId'] = user.key()
      user_pdfs_dict.append(data)
    
    return user_pdfs_dict

  def delete_pdf(self, ownerId, hash, token):
    return self.db.child(f'users/{ownerId}/pdfs/{hash}').remove(token)