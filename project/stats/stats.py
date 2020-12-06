from flask import Blueprint

bp = Blueprint('auth', __name__)


@bp.route('/', methods=['GET'])
def temp():
	return "stats"
