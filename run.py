# -*- coding:utf-8 -*-
from flask import request, jsonify
import blueprints
from app import app
from blueprints.screen_centre import screen_centre
from blueprints.screen_left import screen_left
from blueprints.screen_right import screen_right

app.register_blueprint(screen_centre)
app.register_blueprint(screen_left)
app.register_blueprint(screen_right)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=False)
