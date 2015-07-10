import ast
from flask import flash, request

# check if value is float
def is_float(value):
	try:
		float(value)
		return True
	except ValueError:
		return False

def get_waypoints(form):
	waypoints = []

	i = 0
	while True:
		# get value from html element
		marker = form.get('marker_' + str(i))
		if (marker is None) or (marker is ''):
			break

		# convert value to point (double, double) and add it to database
		raw_coordinate = ast.literal_eval(str(marker))
		if (raw_coordinate is not None) and is_float(raw_coordinate[0]) and is_float(raw_coordinate[1]):
			waypoints.append({'lat': raw_coordinate[0], 'lng': raw_coordinate[1]})

		i = i + 1 # check next marker

	return waypoints
