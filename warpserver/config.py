
import random
import string
import os

# FLASK CONFIGURATION
HOST = os.getenv('AW_HOST', '127.0.0.1')
PORT = int(os.getenv('AW_PORT', '5000'))
SECRET_KEY = os.getenv(
    'AW_SECRET_KEY',
    ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
)

# SQLALCHEMY CONFIGURATION
SQLALCHEMY_DATABASE_URI = os.getenv('AW_SQLALCHEMY_DATABASE_URI', 'sqlite:///database.sqlite')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# UPLOAD CONFIGURATION
MAX_CONTENT_LENGTH = 1024 * 512
UPLOAD_FOLDER = os.getenv('AW_UPLOAD_FOLDER', '.')

# GITHUB_CONFIGURATION

CLIENT_GITHUB_API_URL = os.getenv('AW_CLIENT_GITHUB_API_URL', 'https://api.github.com/repos/KeyboardInterrupt/AlbianWarpClient')
GAME_MODIFICATIONS_GITHUB_API_URL = os.getenv('AW_GAME_MODIFICATIONS_GITHUB_API_URL', 'https://api.github.com/repos/KeyboardInterrupt/AlbianWarpGameModifications')