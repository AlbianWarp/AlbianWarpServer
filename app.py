from warpserver.warpserver import app,init_db, socketio
import sys

if len(sys.argv) >= 2:
    if sys.argv[1] == "init":
        init_db()


socketio.run(app, debug=False, host="0.0.0.0")