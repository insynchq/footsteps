import os

import keen
from flask import abort, Blueprint, Flask, redirect, url_for
from itsdangerous import BadSignature, URLSafeSerializer

footsteps = Blueprint('footsteps', __name__)
serializer = URLSafeSerializer(os.environ['SECRET_KEY'])
scheme = os.environ.get('URL_SCHEME', 'https')


_app = None
def sign(url, **kwargs):
  global _app
  _app = _app or create_app()
  with _app.test_request_context():
    payload = dict(**kwargs)
    serialized = serializer.dumps(payload)
    return url_for('footsteps.track', serialized=serialized, _external=True,
                   _scheme=scheme)


@footsteps.route('/<serialized>')
def track(serialized):
  try:
    payload = serializer.loads(serialized)
    event = payload.pop('event', 'footsteps')
    keen.add_event(event, payload)
  except BadSignature:
    abort(404)
  return redirect(payload['url'])


def create_app():
  app = Flask(__name__)
  app.register_blueprint(footsteps)
  app.debug = os.environ.get('DEBUG', False)
  return app
