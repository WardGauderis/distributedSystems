from flask import Blueprint

bp = Blueprint('general', __name__)


def hopla():
	print('OK')
	from sys import stdout
	stdout.flush()


@bp.route('/test', methods=['GET'])
def temp():
	return 'TEST'
