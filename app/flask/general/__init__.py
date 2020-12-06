from flask import Blueprint

bp = Blueprint('general', __name__)


@bp.route('/test', methods=['GET'])
def temp():
	return 'TEST'
