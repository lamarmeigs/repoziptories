from flask import Flask

from application.api.v1.endpoints import v1_blueprint
from application.api.v2.endpoints import v2_blueprint


app = Flask(__name__.split('.')[0])
app.register_blueprint(v1_blueprint, url_prefix='/v1')
app.register_blueprint(v2_blueprint, url_prefix='/v2')
