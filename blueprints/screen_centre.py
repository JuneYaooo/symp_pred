# -*- coding: utf-8 -*-
"""
@Time    : 2022/12/15 17:14
@Author  : linz
@FileName: screen_centre.py
@version: 1.0
"""

from flask import jsonify, Blueprint, request
from flask_restful import Api, Resource
from app import logger
from app.models import *
from utils import get_days
from sqlalchemy import func

screen_centre = Blueprint('screen_centre', __name__, url_prefix="/api/v1/screen_centre")
api = Api(screen_centre)


class BedInfoView(Resource):
    def post(self):
        try:
            data = request.json
            now_date = data.pop("now_date")
            last_date = data.pop("last_date")
            start_date = data.pop("start_date")
            end_date = data.pop("end_date")
            dept_adrress = data.get("dept_adrress")
            date_range = get_days(start_date, end_date)
        except Exception as e:
            logger.exception(f"GET ARGS ERROR, EXCEPTION: {e}")
            return jsonify({"code": 0, "msg": "请求参数异常"})

        # TOP BAR INDEX
        nl_info_list = db.session.query(TbOverview.day,
                                        func.sum(TbOverview.szxgq_kcs).label('day_kcs_num')).join(TbDicHos,
                                                                                                  TbDicHos.dept_code == TbOverview.dept_code,
                                                                                                  isouter=True).filter(
            or_(TbOverview.day == last_date, TbOverview.day == now_date),
            TbDicHos.dept_adrress == dept_adrress if dept_adrress is not None else 1 == 1).group_by(
            TbOverview.day).all()

        nl_info_dict = {x.day: int(x.day_kcs_num if x.day_kcs_num is not None else 0) for x in nl_info_list}

        nl_date = [last_date, now_date]
        real_nl_info = dict()

        for nl_day in nl_date:
            real_nl_info[nl_day] = nl_info_dict.get(nl_day, 0)

        top_bar_info = dict(sum_bed_num=real_nl_info.get(now_date),
                            ring_ration=round(
                                (real_nl_info.get(now_date) - real_nl_info.get(last_date)) / real_nl_info.get(
                                    last_date), 4) if real_nl_info.get(
                                last_date, 0) != 0 else -2)

        # DATE RANGE INDEX
        range_info_list = db.session.query(TbOverview.day.label('day'),
                                           func.sum(TbOverview.szxgq_kcs).label('day_kcs_num')).join(TbDicHos,
                                                                                                     TbDicHos.dept_code == TbOverview.dept_code,
                                                                                                     isouter=True).filter(
            TbDicHos.dept_code.isnot(None),
            TbOverview.day >= start_date,
            TbOverview.day <= end_date,
            TbDicHos.dept_adrress == dept_adrress if dept_adrress is not None else 1 == 1).group_by(
            TbOverview.day).all()

        range_dict = {x.day: int(x.day_kcs_num if x.day_kcs_num is not None else 0) for x in range_info_list}

        real_range_info_list = []

        for range_day in date_range:
            real_range_info_list.append(dict(datetime=range_day, bed_num=range_dict.get(range_day, 0)))

        # HOSPITAL INFO INDEX
        now_caption_info_list = db.session.query(TbOverview.dept_code, TbOverview.caption, TbDicHos.sf_sj,
                                                 func.sum(TbOverview.szxgq_kcs).label('day_kcs_num')).join(TbDicHos,
                                                                                                           TbDicHos.dept_code == TbOverview.dept_code,
                                                                                                           isouter=True).filter(
            TbDicHos.dept_code.isnot(None),
            TbOverview.day == now_date,
            TbDicHos.dept_adrress == dept_adrress if dept_adrress is not None else 1 == 1).group_by(
            TbOverview.dept_code, TbOverview.caption, TbDicHos.sf_sj).order_by(
            func.sum(TbOverview.szxgq_kcs).desc()).all()

        last_caption_info_list = db.session.query(TbOverview.dept_code, TbOverview.caption,
                                                  func.sum(TbOverview.szxgq_kcs).label('day_kcs_num')).join(TbDicHos,
                                                                                                            TbDicHos.dept_code == TbOverview.dept_code,
                                                                                                            isouter=True).filter(
            TbDicHos.dept_code.isnot(None),
            TbOverview.day == last_date,
            TbDicHos.dept_adrress == dept_adrress if dept_adrress is not None else 1 == 1).group_by(
            TbOverview.dept_code, TbOverview.caption).order_by(func.sum(TbOverview.szxgq_kcs).desc()).all()

        last_caption_dict = {x.dept_code: int(x.day_kcs_num if x.day_kcs_num is not None else 0) for x in
                             last_caption_info_list}

        high_caption_info_list = []
        low_info_list = []
        for caption_info in now_caption_info_list:
            if caption_info.sf_sj is not None and (caption_info.sf_sj == 1):
                high_caption_info_list.append(dict(dept_code=caption_info.dept_code, caption=caption_info.caption,
                                                   day_kcs_num=int(caption_info.day_kcs_num), ring_ration=round(
                        (int(caption_info.day_kcs_num) - last_caption_dict.get(
                            caption_info.dept_code)) / last_caption_dict.get(
                            caption_info.dept_code), 4) if last_caption_dict.get(caption_info.dept_code,
                                                                                 0) != 0 else -2))
            else:
                low_info_list.append(dict(dept_code=caption_info.dept_code, caption=caption_info.caption,
                                          day_kcs_num=int(caption_info.day_kcs_num), ring_ration=round(
                        (int(caption_info.day_kcs_num) - last_caption_dict.get(
                            caption_info.dept_code)) / last_caption_dict.get(
                            caption_info.dept_code), 4) if last_caption_dict.get(caption_info.dept_code,
                                                                                 0) != 0 else -2))

        data = {'low_info_list': low_info_list, 'high_caption_info_list': high_caption_info_list,
                'top_bar_info': top_bar_info, 'real_range_info_list': real_range_info_list}

        return jsonify({"code": 1, 'data': data, "msg": "success"})


class BedFoldLineView(Resource):
    def post(self):
        try:
            data = request.json
            dept_code = data.pop("dept_code")
            start_date = data.pop("start_date")
            end_date = data.pop("end_date")
            dept_adrress = data.get("dept_adrress")
            date_range = get_days(start_date, end_date)
        except Exception as e:
            logger.exception(f"GET ARGS ERROR, EXCEPTION: {e}")
            return jsonify({"code": 0, "msg": "请求参数异常"})

        data_info_list = db.session.query(TbOverview.day, func.sum(TbOverview.szxgq_kcs).label('day_kcs_num')).join(
            TbDicHos,
            TbDicHos.dept_code == TbOverview.dept_code,
            isouter=True).filter(
            TbDicHos.dept_code.isnot(None), TbOverview.dept_code == dept_code,
                                            TbOverview.day >= start_date, TbOverview.day <= end_date,
            TbDicHos.dept_adrress == dept_adrress if dept_adrress is not None else 1 == 1).group_by(
            TbOverview.day).all()

        for x in data_info_list:
            logger.debug(f"{x.day}  {type(x.day)}")

        date_dict = {x.day: int(x.day_kcs_num if x.day_kcs_num is not None else 0) for x in data_info_list}
        logger.debug(f"{date_dict} \n {date_range}")

        data = []
        for day in date_range:
            item = dict()
            item['datetime'] = day
            item['bed_num'] = date_dict.get(day, 0)
            data.append(item)

        return jsonify({"code": 1, 'data': data, "msg": "success"})


api.add_resource(BedInfoView, "/bed/info")
api.add_resource(BedFoldLineView, "/bed/fold/line")
