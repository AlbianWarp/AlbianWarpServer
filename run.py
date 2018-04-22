from warpserver.server import app
from warpserver.config import PORT, HOST, DEBUG

if __name__ == '__main__':
    app.run(debug=DEBUG, host=HOST, port=PORT)
