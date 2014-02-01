"""
This defines the whole RESTful API that will run within flask
"""
import os
import zen_path_info as pi
import zen_request_context as rc
import zen_request_validator as rv
from flask import Flask, abort, request, jsonify

def check_for_parameters(text):
	"""
	No parameters allowed
	"""
	split_content = text.split(';')
	if len(split_content) > 1:
		return (404, 'Parameters not allowed on element "{}"'.format(text))
	return (200,'')

def check_version(version):
	"""
	Validation of the version being requested
	"""
	(status, error_message) = check_for_parameters(version)
	if status == 200:
		versions = ['1.0']
		if version not in versions:
			(status, error_message) = (404, 'Unknown API version "{}"'.format(version))
	return (status, error_message)

def initial_checks(version, meta):
	"""
	Basic checks on URL
	"""
	(status, error_message) = check_version(version)
	if status == 200:
		(status, error_message) = check_for_parameters(meta)
	return (status, error_message)

def create_error_output(val):
	return {val[0]:val[1]}

def exec_request_pipeline(version, meta, request, varargs = None):
	"""
	Standard pipeline for all requests
	"""
	# Validate basic URL details
	(status, error_message) = initial_checks(version, meta)
	if status != 200:
		return create_error_output((status, error_message))

	# Construct request context
	context = rc.RequestContext(version, meta, pi.PathInfo(varargs, request.query_string), request)
	
	# Validate request
	(status, error_message) = rv.validate_request_details(context)
	if status != 200:
		return create_error_output((status, error_message))

	# TODO: authenticate and authorise here
	#...
	# Execute request
	return context.exec_fn(context)

app = Flask(__name__)

@app.route('/<version>/<meta>/<path:varargs>')
def routing_start(version, meta, varargs = None):
	return jsonify(exec_request_pipeline(version, meta, request, varargs))

@app.route('/')
@app.route('/<path:varargs>')
def bad_routing_start(varargs = None):
	if not varargs:
		return jsonify(create_error_output((404, 'Incomplete URL provided "{}"'.format(varargs))))
	else:
		return jsonify(create_error_output((404, 'Incomplete URL provided')))

if __name__ == "__main__":
    app.run(debug=True)
