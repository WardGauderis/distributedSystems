from . import bp

@bp.route('/', methods=['GET'])
def temp():
	return 'auth'
