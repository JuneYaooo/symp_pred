# -*- coding: utf-8 -*-
from flask import jsonify, Blueprint, request
from flask_restful import Api, Resource
from app import logger
from app.models import *
from utils import get_days
from sqlalchemy import func

screen_right = Blueprint('screen_right', __name__, url_prefix="/api/v1/screen_right")
api = Api(screen_right)


class TestView(Resource):
    def get(self):
        try:
            data = request.args
            now_date = data.get("now_date")
            dept_adrress = data.get("dept_adrress")
        except Exception as e:
            logger.exception(f"GET ARGS ERROR, EXCEPTION: {e}")
            return jsonify({"code": 0, "msg": "请求参数异常"})

        # TODO SQL
        results = db.session.execute("SELECT * FROM tb_dic_hos limit 1").fetchall()
        logger.debug(f"{results}")

        # TODO RESULT TO WEB DATA

        data = [dict(now_date=now_date, dept_adrress=dept_adrress)]

        return jsonify({"code": 1, 'data': data, "msg": "success"})

    def post(self):
        try:
            data = request.json
            now_date = data.pop("now_date")
            dept_adrress = data.get("dept_adrress")
        except Exception as e:
            logger.exception(f"GET ARGS ERROR, EXCEPTION: {e}")
            return jsonify({"code": 0, "msg": "请求参数异常"})

        # TODO SQL
        results = db.session.execute("SELECT * FROM tb_dic_hos limit 1").fetchall()
        logger.debug(f"{results}")

        # TODO RESULT TO WEB DATA

        data = [dict(now_date=now_date, dept_adrress=dept_adrress)]
        return jsonify({"code": 1, 'data': data, "msg": "success"})


api.add_resource(TestView, "/test/info")
