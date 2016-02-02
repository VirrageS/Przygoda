import ast

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
        try:
            raw_coordinate = ast.literal_eval(str(marker))
            if (raw_coordinate is not None) and is_float(raw_coordinate[0]) and is_float(raw_coordinate[1]):
                waypoints.append({'lat': raw_coordinate[0], 'lng': raw_coordinate[1]})
        except:
            return None

        i = i + 1 # check next marker

    return waypoints

def get_bounds(form):
    # get start position from html element
    start_pos = form.get('bl_corner')
    if (start_pos is None) or (start_pos is ''):
        return None

    # convert value to point (double, double)
    try:
        start_pos = ast.literal_eval(str(start_pos))
        if (start_pos is None):
            return None

        if (not is_float(start_pos[0])) or (not is_float(start_pos[1])):
            return None
    except:
        return None

    # get end position from html element
    end_pos = form.get('tr_corner')
    if (end_pos is None) or (end_pos is ''):
        return None

    try:
        # convert value to point (double, double)
        end_pos = ast.literal_eval(str(end_pos))
        if (end_pos is None):
            return None

        if (not is_float(end_pos[0])) or (not is_float(end_pos[1])):
            return None
    except:
        return None

    return {'bl_corner': start_pos, 'tr_corner': end_pos}
