"""
This defines the whole RESTful API that will run within flask
"""
import os
import zen_path_info as pi
import zen_request_context as rc
import zen_request_validator as rv
from flask import Flask, abort, request, jsonify

app = Flask(__name__)

def create_zen_request_context(version, meta, request, varargs = None):
	if not varargs:
		abort(404)

	return rc.RequestContext(version, meta, pi.PathInfo(varargs, request.query_string), request)

def exec_request_pipeline(version, meta, request, varargs = None):
	# Construct request context
	context = create_zen_request_context('1.0', 'data', request, varargs)
	# Validate request
	(status, error_message) = rv.validate_request_details(context)
	if status != 200:
		return {status:error_message}
	# Should authenticate and authorise here
	#...
	# Execute request
	return context.exec_fn(context)

@app.route('/1.0/data/<path:varargs>')
def v1_0_data_routing_start(varargs = None):
	return jsonify(exec_request_pipeline('1.0', 'data', request, varargs))

@app.route('/1.0/model/<path:varargs>')
def v1_0_model_routing_start(varargs = None):
	return jsonify(exec_request_pipeline('1.0', 'data', request, varargs))

@app.route('/')
@app.route('/<path:varargs>')
def routing_start(varargs = None):
    # Should never get here
    abort(404)

if __name__ == "__main__":
    app.run(debug=True)
