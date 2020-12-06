from . import bp

from app.general import hopla

@bp.route('/', methods=['GET'])
def temp():
	hopla()
	return 'auth'
