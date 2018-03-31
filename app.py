from warpserver.warpserver import app,init_db
import sys

if len(sys.argv) >= 2:
    if sys.argv[1] == "init":
        init_db()


app.run(debug=True,host="0.0.0.0")