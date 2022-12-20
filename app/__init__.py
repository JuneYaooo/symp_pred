# -*- coding:utf-8 -*-
from settings import *
from loguru import logger
from flask import Flask, request, jsonify, g
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_cors import CORS
from app.models import db
from flask_sqlalchemy import get_debug_queries
from app.models import *

logger.add(API_LOG_PATH, level="DEBUG", encoding='utf-8', enqueue=True, rotation="00:00", retention="30 days")

app = Flask(__name__)
app.config.from_object("settings")
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
# cache = Cache()
# cache.init_app(app)
db.init_app(app)
# db.create_all(app=app)


@app.before_request
def request_log():
    if request.method != "OPTIONS":
        db.session.remove()
        logger.info(f"Request: path: {request.full_path}, method: {request.method}, params: {request.json}")


@app.after_request
def response_log(response):
    if request.method != "OPTIONS":
        db.session.remove()
        logger.info(f"Response: {response.json}")
        return response
    return response


@app.after_request
def response_info(response):
    for query in get_debug_queries():
        if query.duration >= 0.3:
            logger.warning(f"URL: {request.full_path}, Method: {request.method}, ReqTime: {datetime.now()}")
            logger.warning(
                f"MYSQL QUERY: {query.statement}\nParameters: {query.parameters}\nDuration: {query.duration}\n")
    return response
