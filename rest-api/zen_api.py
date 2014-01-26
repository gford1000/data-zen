"""
This defines the whole RESTful API that will run within flask
"""
import os
import zen_path_info as pi
from flask import Flask, abort, request, jsonify

app = Flask(__name__)

@app.route('/')
@app.route('/<path:varargs>')
def routing_start(varargs = None):
    if varargs:
        # Deconstruct request
        path_info = pi.PathInfo(varargs, request.query_string)
        return "Done!"
        
    else:
        # Should never get here
        abort(404)

if __name__ == "__main__":
    app.run(debug=True)
