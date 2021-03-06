from flask import Blueprint, jsonify, request, abort
from datetime import datetime
from medioex import do_write, di_read, ao_write, ai_read, temp_read

api = Blueprint('api', __name__, url_prefix='/api')

OUTPUTS = {}

# DIGITAL INPUT ROUTES


@api.route('/di/<int:pin>/read', methods=['GET'])
def di_read_api(pin):
    if 1 > pin or pin > 16:
        return jsonify({
            'status': 'ERROR',
            'message': 'Digital input pins for MedIOEx must be in [1, 16]'})

    result = di_read(pin)
    return jsonify({'status': 'OK',
                    'type': 'di',
                    'action': 'read',
                    'pin': pin,
                    'value': result})


# DIGITAL OUTPUT ROUTES

@api.route('/do/<int:pin>/read', methods=['GET'])
def do_read_api(pin):
    if 1 > pin or pin > 12:
        return jsonify({
            'status': 'ERROR',
            'message': 'Digital output pins for MedIOEx must be in [1, 12]'})
    return jsonify({'status': 'OK',
                    'type': 'do',
                    'action': 'read',
                    'pin': pin,
                    'value': OUTPUTS['do'][pin]})


@api.route('/do/<int:pin>/write', methods=['GET'])
def do_write_api(pin):
    val = int(request.args.get('val'))
    if 1 > pin or pin > 12:
        return jsonify({
            'status': 'ERROR',
            'message': 'Digital output pins for MedIOEx must be in [1, 12]'})
    elif val not in (0, 1):
        return jsonify({'status': 'ERROR',
                        'message': 'Digital outputs only accept 0 or 1.'})
    do_write(pin, val)
    OUTPUTS['do'][pin] = val
    return jsonify({'status': 'OK',
                    'type': 'do',
                    'action': 'write',
                    'pin': pin,
                    'value': val})


@api.route('/do/<int:pin>/set', methods=['GET'])
def do_set_api(pin):
    if 1 > pin or pin > 12:
        return jsonify({
            'status': 'ERROR',
            'message': 'Digital output pins for MedIOEx must be in [1, 12]'})
    do_write(pin, 1)
    OUTPUTS['do'][pin] = 1
    return jsonify({'status': 'OK',
                    'type': 'do',
                    'action': 'set',
                    'pin': pin,
                    'value': 1})


@api.route('/do/<int:pin>/reset', methods=['GET'])
def do_reset_api(pin):
    if 1 > pin or pin > 12:
        return jsonify({
            'status': 'ERROR',
            'message': 'Digital output pins for MedIOEx must be in [1, 12]'})
    do_write(pin, 0)
    OUTPUTS['do'][pin] = 0
    return jsonify({'status': 'OK',
                    'type': 'do',
                    'action': 'reset',
                    'pin': pin,
                    'value': 0})


# RELAY OUTPUT ROUTES

@api.route('/ro/<int:pin>/read', methods=['GET'])
def ro_read_api(pin):
    if 13 > pin or pin > 16:
        return jsonify({
            'status': 'ERROR',
            'message': 'Relay pins for MedIOEx must be in [13, 16]'})

    return jsonify({'status': 'OK',
                    'type': 'ro',
                    'action': 'read',
                    'pin': pin,
                    'value': OUTPUTS['ro'][pin]})


@api.route('/ro/<int:pin>/write', methods=['GET'])
def ro_write_api(pin):
    val = int(request.args.get('val'))
    if 13 > pin or pin > 16:
        return jsonify({
            'status': 'ERROR',
            'message': 'Relay pins for MedIOEx must be in [13, 16]'})

    elif val not in (0, 1):
        return jsonify({'status': 'ERROR',
                        'message': 'Relay outputs only accept 0 or 1.'})

    do_write(pin, val)
    OUTPUTS['ro'][pin] = val
    return jsonify({'status': 'OK',
                    'type': 'ro',
                    'action': 'write',
                    'pin': pin,
                    'value': val})


@api.route('/ro/<int:pin>/set', methods=['GET'])
def ro_set_api(pin):
    if 13 > pin or pin > 16:
        return jsonify({
            'status': 'ERROR',
            'message': 'Relay pins for MedIOEx must be in [13, 16]'})
    do_write(pin, 1)
    OUTPUTS['ro'][pin] = 1
    return jsonify({'status': 'OK',
                    'type': 'ro',
                    'action': 'set',
                    'pin': pin,
                    'value': 1})


@api.route('/ro/<int:pin>/reset', methods=['GET'])
def ro_reset_api(pin):
    if 13 > pin or pin > 16:
        return jsonify({
            'status': 'ERROR',
            'message': 'Relay pins for MedIOEx must be in [13, 16]'})
    do_write(pin, 0)
    OUTPUTS['ro'][pin] = 0
    return jsonify({'status': 'OK',
                    'type': 'ro',
                    'action': 'reset',
                    'pin': pin,
                    'value': 0})


# ANALOG INPUT ROUTES

@api.route('/ai/<int:pin>/read', methods=['GET'])
def ai_read_api(pin):
    ss = request.args.get('start', 0.0)
    se = request.args.get('end', 4095.0)
    try:
        ss = float(ss)
        se = float(se)
    except ValueError:
        abort(400)

    if 1 > pin or pin > 4:
        return jsonify({
            'status': 'ERROR',
            'message': 'Analog input pins for MedIOEx must be in [1, 4]'})

    result = ai_read(pin)

    # The line below is just a linear transformation.
    #
    #      (nv - ns)   (sv - ss)
    #      --------- = ---------
    #      (ne - ns)   (se - ss)
    #
    # ns = normal start (0)
    # ne = normal end (4095)
    # nv = value got via ai_read [0, 4095] ~= [0, 4096)
    # ss = scaled start (given by user)
    # se = scaled end (given by user)
    # sv = value demanded
    sv = ss + (result - 0) * (se - ss) / (4095 - 0)

    return jsonify({'status': 'OK',
                    'type': 'ai',
                    'action': 'read',
                    'pin': pin,
                    'start': ss,
                    'end': se,
                    'value': sv})


# ANALOG OUTPUT ROUTES

@api.route('/ao/<int:pin>/read', methods=['GET'])
def ao_read_api(pin):
    ss = request.args.get('start', 0.0)
    se = request.args.get('end', 4095.0)
    try:
        ss = float(ss)
        se = float(se)
    except ValueError:
        abort(400)

    if 1 > pin or pin > 4:
        return jsonify({
            'status': 'ERROR',
            'message': 'Analog output pins for MedIOEx must be in [1, 4]'})
    result = OUTPUTS['ao'][pin]

    # Check the formula at ai_read_api before changing the line below
    sv = ss + (result - 0) * (se - ss) / (4095 - 0)

    return jsonify({'status': 'OK',
                    'type': 'ao',
                    'action': 'read',
                    'pin': pin,
                    'start': ss,
                    'end': se,
                    'value': sv})


@api.route('/ao/<int:pin>/write', methods=['GET'])
def ao_write_api(pin):
    ss = request.args.get('start', 0.0)
    se = request.args.get('end', 4095.0)
    try:
        ss = float(ss)
        se = float(se)
    except ValueError:
        abort(400)
    sv = int(request.args.get('val'))

    if 1 > pin or pin > 4:
        return jsonify({
            'status': 'ERROR',
            'message': 'Analog output pins for MedIOEx must be in [1, 4]'})
    elif not (ss <= sv <= se or ss >= sv >= se):
        return jsonify({
            'status': 'ERROR',
            'message': 'Value should be between {} and {}.'.format(ss, se)})

    nv = 0 + (4095 - 0) * (sv - ss) / (se - ss)
    val = nv

    # Check the formula at ai_read_api before changing the line below
    ao_write(pin, int(nv))
    OUTPUTS['ao'][pin] = val

    return jsonify({'status': 'OK',
                    'type': 'ao',
                    'action': 'write',
                    'pin': pin,
                    'value': sv})


# TEMPERATURE

@api.route('/temperature/read', methods=['GET'])
def get_temperature():
    result = temp_read(1)
    return jsonify({'status': 'OK',
                    'type': 'temperature',
                    'action': 'read',
                    'value': result})


# ALL OUTPUTS

@api.route('/reset', methods=['GET'])
def reset_all_outputs():
    for pin in range(1, 5):
        ao_write(pin, 0)
        OUTPUTS['ao'][pin] = 0

    for pin in range(1, 13):
        do_write(pin, 0)
        OUTPUTS['do'][pin] = 0

    for pin in range(13, 17):
        do_write(pin, 0)
        OUTPUTS['ro'][pin] = 0

    return jsonify({'status': 'OK',
                    'action': 'reset',
                    'value': None})


# STATUS

@api.route('/status', methods=['GET'])
def status():
    status = OUTPUTS.copy()

    inputs = {
        'di': {},
        'ai': {}
    }
    for pin in range(1, 17):
        inputs['di'][pin] = di_read(pin)
    for pin in range(1, 5):
        inputs['ai'][pin] = ai_read(pin)
    status.update(inputs)

    status['temperature'] = temp_read(1)
    status['uptime'] = datetime.now().timestamp() - OUTPUTS['start_timestamp']

    return jsonify({'status': 'OK',
                    'action': 'status',
                    'value': status})
