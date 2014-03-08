import os

import keen
from flask import abort, Blueprint, Flask, redirect
from itsdangerous import BadSignature, URLSafeSerializer

footsteps = Blueprint('footsteps', __name__)
serializer = URLSafeSerializer(os.environ['SECRET_KEY'])

@footsteps.route('/<serialized>')
def track(serialized):
  try:
    payload = serializer.loads(serialized)
    event = payload.pop('event')
    keen.add_event(event, payload)
  except BadSignature:
    abort(404)
  return redirect(payload['url'])

def create_app():
  app = Flask(__name__)
  app.register_blueprint(footsteps)
  app.debug = os.environ.get('DEBUG', False)
  return app
