# -*- coding: utf-8 -*-
from flask import jsonify, Blueprint, request
from flask_restful import Api, Resource
from app import logger
from app.models import *
from utils import get_days
from sqlalchemy import func

screen_left = Blueprint('screen_left', __name__, url_prefix="/api/v1/screen_left")
api = Api(screen_left)


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
            now_date = data.pop("now_date") # 必须
            dept_adrress = data.get("dept_adrress") # 非必须
        except Exception as e:
            logger.exception(f"GET ARGS ERROR, EXCEPTION: {e}")
            return jsonify({"code": 0, "msg": "请求参数异常"})

        # TODO SQL
        results = db.session.execute("SELECT * FROM tb_dic_hos limit 1").fetchall()
        logger.debug(f"{results}")

        # TODO RESULT TO WEB DATA

        data = [dict(now_date=now_date, dept_adrress=dept_adrress)]
        return jsonify({"code": 1, 'data': data, "msg": "success"})

class FeverDetailsView(Resource):
    def get(self):
        try:
            data = request.args
            dept_adrress = data.get("dept_adrress")  # [] 多选
            caption = data.get("caption")  # [] 多选,传ID
            time_dimension = data.get("time_dimension")  # 日 周 月 季
        except Exception as e:
            logger.exception(f"GET ARGS ERROR, EXCEPTION: {e}")
            return jsonify({"code": 0, "msg": "请求参数异常"})


    def post(self):
        try:
            data = request.json
            dept_adrress = data.pop("dept_adrress")  # [] 多选，全部区为全区卫健委
            caption = data.pop("caption")  # [] 多选，全部医院为全部市级医院
            time_dimension = data.pop("time_dimension")  # 日 周 月 季
            logger.debug(f"parameters: {data}")
            if len(dept_adrress) > 0 and len(caption) > 0:
                raise Exception("请求参数异常, dept_adrress和caption不能同时有值")
        except Exception as e:
            logger.exception(f"GET ARGS ERROR, EXCEPTION: {e}")
            return jsonify({"code": 0, "msg": f"请求参数异常。{e}"})

        result_dict = {}
        # 参数转换
        dept_adrress_condition = '' if len(
            dept_adrress) == 0 or dept_adrress==['全部区'] else f"and tdh.dept_adrress in {str(dept_adrress).replace('[', '(').replace(']', ')')}"
        caption_condition = '' if len(
            caption) == 0 or caption==['全部医院'] else f"and tdh.dept_code in {str(caption).replace('[', '(').replace(']', ')')}"

        # 获取最新日期
        # 算区级指标
        today = datetime.now().strftime("%Y%m%d")
        sql_visit = f"""select max(date_format(str_to_date(day, '%Y%m%d'),'%Y%m%d')) as newest_day
                            from tb_overview to2
                            inner join p_tb_dic_hos tdh on to2.dept_code=tdh.dept_code
                            where day <= "{today}" {dept_adrress_condition} {caption_condition}
                            """
        logger.debug(f"sql_date~~~{sql_visit}")
        results = db.session.execute(sql_visit).fetchall()
        logger.debug(f"最新日期~~~{results}")
        end_date = results[0][0] if len(results) > 0 and len(results[0]) > 0 else None
        result_dict['fever_visit_date'] = end_date

        # parameters process
        # end_date = datetime.now().strftime("%Y%m%d")
        # end_date_format = datetime.now().strftime("%Y-%m-%d")
        end_date_time = datetime.strptime(end_date, "%Y%m%d") if end_date is not None else datetime.now()
        start_date = (end_date_time - timedelta(days=14)).strftime("%Y%m%d") if time_dimension == '日' else \
            (end_date_time - timedelta(weeks=8)).strftime("%Y%m%d") if time_dimension == '周' else \
                (end_date_time - relativedelta(months=8)).strftime("%Y%m%d") if time_dimension == '月' else \
                    (end_date_time - relativedelta(months=8 * 3)).strftime(
                        "%Y%m%d") if time_dimension == '季' else end_date
        current_month = end_date_time.month
        current_year = end_date_time.year
        days_list = [(end_date_time - timedelta(days=14) + timedelta(days=i + 1)).strftime("%Y-%m-%d") for i in
                     range(14)]
        months_list = []
        for i in range(11, -1, -1):
            month = current_month - i
            year = current_year
            if month < 1:
                month += 12
                year -= 1
            months_list.append(f"{year:04d}-{month:02d}")

        def get_week_number(date):
            return date.isocalendar()[1]

        current_week = get_week_number(end_date_time)
        weeks_list = []
        for i in range(7, -1, -1):
            week = current_week - i
            year = current_year
            if week < 1:
                year -= 1
                week = 52 + week
            elif week > 52:
                year += 1
                week = week - 52
            weeks_list.append(f"{year:04d}-{week:02d}")

        current_quarter = (current_month - 1) // 3 + 1
        quarter_list = []
        for i in range(7, -1, -1):
            quarter = current_quarter - i
            year = current_year
            if quarter < 1:
                quarter += 4
                year -= 1
            quarter_list.append(f"{year:04d}-{quarter:d}")

        date_list = days_list if time_dimension == '日' else weeks_list if time_dimension == '周' else months_list if time_dimension == '月' else quarter_list if time_dimension == '季' else end_date

        select_time = "date_format(str_to_date(day, '%Y%m%d'),'%Y-%m-%d')" if time_dimension == '日' else \
            "concat(YEAR(str_to_date(day, '%Y%m%d')),'-',WEEK(str_to_date(day, '%Y%m%d')))" if time_dimension == '周' else \
                "concat(YEAR(str_to_date(day, '%Y%m%d')),'-',MONTH(str_to_date(day, '%Y%m%d')))" if time_dimension == '月' else \
                    "concat(YEAR(str_to_date(day, '%Y%m%d')),'-',QUARTER(str_to_date(day, '%Y%m%d')))" if time_dimension == '季' else "date_format(str_to_date(day, '%Y%m%d'),'%Y-%m-%d')"
        select_dimention = ",tdh.dept_adrress" if len(dept_adrress) > 0 and len(
            caption) == 0 else ",tdh.dept_code" if len(dept_adrress) == 0 and len(caption) > 0 else ''
        area_flag = "sf_sj = 1" if caption == ['全部医院'] else "sf_sj is NULL" if len(dept_adrress) > 0 else "1"
        # 发热门诊就诊人次
        sql_visit = f"""select {select_time} as TIME, CAST(SUM(frmz_zzll) AS SIGNED) as fever_visit, CAST(SUM(frmz_hshkyyxs) AS SIGNED) as pos_visit
                from ((select day,to2.dept_code,frmz_zzll,frmz_hshkyyxs,tdh.sf_sj 
                from tb_overview to2
                inner join p_tb_dic_hos tdh on to2.dept_code=tdh.dept_code
                where day <= "{end_date}" and day >= "{start_date}" and tdh.sf_sj is Null {dept_adrress_condition} {caption_condition})
                UNION (
                select ywrq as day,to2.dept_code,frmzrc as frmz_zzll,hz_frmz_yxrs as frmz_hshkyyxs,tdh.sf_sj 
                from (select ywrq,dept_code,sum(frmzrc) as frmzrc from sk_day_report group by ywrq,dept_code )  to2
                left join sk_sjyy_yxrytjb ssy on to2.ywrq =ssy.day and to2.dept_code =ssy.dept_code
                inner join p_tb_dic_hos tdh on to2.dept_code=tdh.dept_code
                where ywrq <= "{end_date}" and ywrq >= "{start_date}"  and tdh.sf_sj = 1 {caption_condition})) uni
                where {area_flag}
                group by {select_time} 
                order by TIME asc
                """
        results = db.session.execute(sql_visit).fetchall()
        logger.debug(f"sql_visit~~~{sql_visit}")
        logger.debug(f"{results}")
        fever_visit_dict = {}
        pos_visit_dict = {}
        for res in results:
            fever_visit_dict[res[0]] = res[1]
            pos_visit_dict[res[0]] = res[2]

        data = [dict(time=[i for i in date_list],
                     fever_visit=[fever_visit_dict[i] if i in fever_visit_dict and fever_visit_dict[i] is not None else 0 for i in
                                  date_list])]
        result_dict['fever_visit_arr'] = data
        # 总人数
        data = [dict(time=[i for i in date_list],
                     pos_visit=[pos_visit_dict[i] if i in pos_visit_dict and pos_visit_dict[i] is not None else 0 for i in
                                date_list])]
        result_dict['fever_pos_visit_arr'] = data
        logger.debug(f"data[0]['pos_visit'],{data[0]['pos_visit']}")
        result_dict['fever_pos_visit_cur'] = data[0]['pos_visit'][-1] if len(data[0]['pos_visit']) > 0 else 0
        result_dict['fever_pos_visit_relative'] = data[0]['pos_visit'][-1] - data[0]['pos_visit'][-2] if len(data[0]['pos_visit']) > 1 else \
            data[0]['pos_visit'][-1] if len(data[0]['pos_visit']) > 0 else 0

        # 阳性人数
        data = [dict(time=[i for i in date_list],
                     pos_visit_rate=[float(pos_visit_dict[i]/fever_visit_dict[i]) if i in pos_visit_dict and i in fever_visit_dict and pos_visit_dict[i] is not None and fever_visit_dict[i] is not None and fever_visit_dict[i]!=0 else 0
                                     for i in date_list])]
        result_dict['fever_pos_rate_arr'] = data
        result_dict['fever_pos_rate_cur'] =data[0]['pos_visit_rate'][-1] if len(data[0]['pos_visit_rate']) > 0 else 0
        result_dict['fever_pos_rate_relative'] = data[0]['pos_visit_rate'][-1] - data[0]['pos_visit_rate'][-2] if len(data[0]['pos_visit_rate']) > 1 else \
            data[0]['pos_visit_rate'][-1] if len(data[0]['pos_visit_rate']) > 0 else 0




        # # 发热门诊阳性人数
        # sql_pos_visit = f"""select {select_time} as TIME, CAST(SUM(frmz_hshkyyxs) AS SIGNED) as pos_visit
        #                 from tb_overview to2
        #                 inner join p_tb_dic_hos tdh on to2.dept_code=tdh.dept_code
        #                 where day <= "{end_date}"and day >= "{start_date}" {dept_adrress_condition} {caption_condition}
        #                 group by {select_time}
        #                 order by TIME asc
        #                 """
        # results = db.session.execute(sql_pos_visit).fetchall()
        # results_dict = dict(results)
        # logger.debug(f"{results} ============== {sql_pos_visit}")
        #
        # for i in results:
        #     logger.debug(f"{i}")
        # pos_visit_list = [int(i[1]) if len(i) > 0 and i[1] is not None else 0 for i in results]
        #
        # data = [dict(time=[i for i in date_list],
        #              pos_visit=[results_dict[i] if i in results_dict and results_dict[i] is not None else 0 for i in
        #                         date_list])]
        # result_dict['fever_pos_visit_arr'] = data
        # result_dict['fever_pos_visit_cur'] = pos_visit_list[-1] if len(results) > 0 else 0
        # result_dict['fever_pos_visit_relative'] = pos_visit_list[-1] - pos_visit_list[-2] if len(results) > 1 else \
        #     pos_visit_list[0] if len(results) > 0 else 0
        #
        # # 发热门诊阳性检出率
        # sql_pos_visit = f"""select {select_time} as TIME , SUM(frmz_hshkyyxs)/SUM(frmz_zzll) as pos_visit_rate
        #                         from tb_overview to2
        #                         inner join p_tb_dic_hos tdh on to2.dept_code=tdh.dept_code
        #                         where day <= "{end_date}"and day >= "{start_date}" {dept_adrress_condition} {caption_condition}
        #                         group by {select_time}
        #                         order by TIME asc
        #                         """
        # results = db.session.execute(sql_pos_visit).fetchall()
        # results_dict = dict(results)
        # logger.debug(f"{results}")
        # pos_rate_list = [float(i[1]) if len(i) > 0 and i[1] is not None else 0 for i in results]
        # data = [dict(time=[i for i in date_list],
        #              pos_visit_rate=[float(results_dict[i]) if i in results_dict and results_dict[i] is not None else 0
        #                              for i in date_list])]
        # result_dict['fever_pos_rate_arr'] = data
        # result_dict['fever_pos_rate_cur'] = pos_rate_list[-1] if len(results) > 0 else 0
        # result_dict['fever_pos_rate_relative'] = pos_rate_list[-1] - pos_rate_list[-2] \
        #     if len(results) > 1 else pos_rate_list[-1] if len(results) > 0 else 0

        return jsonify({"code": 1, 'data': result_dict, "msg": "success"})


class FeverDrilDownView(Resource):
    def get(self):
        try:
            data = request.args
            hos_grade = data.get("hos_grade")  # [] 多选
            select_date = data.get("select_date")  # [] 多选,传ID
        except Exception as e:
            logger.exception(f"GET ARGS ERROR, EXCEPTION: {e}")
            return jsonify({"code": 0, "msg": "请求参数异常"})


    def post(self):
        try:
            data = request.json
            hos_grade = data.pop("hos_grade")  # 市级医院，区级医院
            select_date = data.pop("select_date")  # "2022-12-17"
            logger.debug(f"parameters: {data}")
        except Exception as e:
            logger.exception(f"GET ARGS ERROR, EXCEPTION: {e}")
            return jsonify({"code": 0, "msg": f"请求参数异常。{e}"})

        select_grade = "aa.sf_sj = 1" if hos_grade == "市级医院" else "aa.sf_sj is Null"
        group_field1 = "tdh.caption" if hos_grade == "市级医院" else 'tdh.dept_adrress'
        group_field2 = "tdh.dept_code" if hos_grade == "市级医院" else 'tdh.dept_adrress'
        # 发热门诊就诊人次
        result_dict = {}
        if hos_grade == "区级医院":
            sql_visit_details = f"""select aa.dept_adrress,aa.caption,aa.dept_code,aa.sf_sj,date_format(aa.time,'%Y-%m-%d') as time,aa.fever_visit,bb.fever_visit_yes,cc.fever_visit_lastweek  from 
                                    (select tdh.dept_adrress,{group_field1} as caption,{group_field2} as dept_code,tdh.sf_sj,str_to_date(day, '%Y%m%d') as TIME,DATE_SUB(str_to_date(day, '%Y%m%d'),INTERVAL 1 DAY) as yesterday,DATE_SUB(str_to_date(day, '%Y%m%d'),INTERVAL 7 DAY) as last_week, CAST(SUM(frmz_zzll) AS SIGNED) as fever_visit
                                    from tb_overview to2
                                    inner join p_tb_dic_hos tdh on to2.dept_code=tdh.dept_code
                                    where tdh.sf_sj is Null 
                                    group by tdh.dept_adrress,{group_field1},{group_field2},tdh.sf_sj,str_to_date(day, '%Y%m%d') ,DATE_SUB(str_to_date(day, '%Y%m%d'),INTERVAL 1 DAY),DATE_SUB(str_to_date(day, '%Y%m%d'),INTERVAL 7 DAY) ) aa
                                    left join (select tdh.dept_adrress,{group_field1} as caption, {group_field2} as dept_code,tdh.sf_sj,str_to_date(day, '%Y%m%d') as TIME, CAST(SUM(frmz_zzll) AS SIGNED) as fever_visit_yes
                                    from tb_overview to2
                                    inner join p_tb_dic_hos tdh on to2.dept_code=tdh.dept_code
                                    where tdh.sf_sj is Null 
                                    group by tdh.dept_adrress,{group_field1},{group_field2},tdh.sf_sj,str_to_date(day, '%Y%m%d')) bb on aa.yesterday =bb.TIME and aa.dept_code = bb.dept_code
                                    left join (select tdh.dept_adrress,{group_field1} as caption,{group_field2} as dept_code,tdh.sf_sj,str_to_date(day, '%Y%m%d') as TIME, CAST(SUM(frmz_zzll) AS SIGNED) as fever_visit_lastweek
                                    from tb_overview to2
                                    inner join p_tb_dic_hos tdh on to2.dept_code=tdh.dept_code
                                    where tdh.sf_sj is Null 
                                    group by tdh.dept_adrress,{group_field1},{group_field2},tdh.sf_sj,str_to_date(day, '%Y%m%d')) cc on aa.last_week =cc.TIME and aa.dept_code = cc.dept_code
                                    where {select_grade} and aa.TIME='{select_date}'
                                    order by aa.fever_visit desc
                            """
        else:
            sql_visit_details = f"""select aa.dept_adrress,aa.caption,aa.dept_code,aa.sf_sj,date_format(aa.time,'%Y-%m-%d') as time,aa.fever_visit,bb.fever_visit_yes,cc.fever_visit_lastweek  from 
                                    (select tdh.dept_adrress,tdh.caption as caption,tdh.dept_code as dept_code,tdh.sf_sj,str_to_date(ywrq, '%Y%m%d') as TIME,DATE_SUB(str_to_date(ywrq, '%Y%m%d'),INTERVAL 1 DAY) as yesterday,DATE_SUB(str_to_date(ywrq, '%Y%m%d'),INTERVAL 7 DAY) as last_week, CAST(SUM(frmzrc) AS SIGNED) as fever_visit
                                    from sk_day_report to2
                                    inner join p_tb_dic_hos tdh on to2.dept_code=tdh.dept_code
                                    group by tdh.dept_adrress,tdh.caption,tdh.dept_code,tdh.sf_sj,str_to_date(ywrq, '%Y%m%d') ,DATE_SUB(str_to_date(ywrq, '%Y%m%d'),INTERVAL 1 DAY),DATE_SUB(str_to_date(ywrq, '%Y%m%d'),INTERVAL 7 DAY) ) aa
                                    left join (select tdh.dept_adrress,tdh.caption as caption, tdh.dept_code as dept_code,tdh.sf_sj,str_to_date(ywrq, '%Y%m%d') as TIME, CAST(SUM(frmzrc) AS SIGNED) as fever_visit_yes
                                    from sk_day_report to2
                                    inner join p_tb_dic_hos tdh on to2.dept_code=tdh.dept_code
                                    group by tdh.dept_adrress,tdh.caption,tdh.dept_code,tdh.sf_sj,str_to_date(ywrq, '%Y%m%d')) bb on aa.yesterday =bb.TIME and aa.dept_code = bb.dept_code and aa.sf_sj = bb.sf_sj
                                    left join (select tdh.dept_adrress,tdh.caption as caption,tdh.dept_code as dept_code,tdh.sf_sj,str_to_date(ywrq, '%Y%m%d') as TIME, CAST(SUM(frmzrc) AS SIGNED) as fever_visit_lastweek
                                    from sk_day_report to2
                                    inner join p_tb_dic_hos tdh on to2.dept_code=tdh.dept_code
                                    group by tdh.dept_adrress,tdh.caption,tdh.dept_code,tdh.sf_sj,str_to_date(ywrq, '%Y%m%d')) cc on aa.last_week =cc.TIME and aa.dept_code = cc.dept_code and aa.sf_sj = cc.sf_sj
                                    where aa.sf_sj =1 and aa.TIME='{select_date}'
                                    order by aa.fever_visit desc
                                """
        logger.debug(f"sql_visit_details~~{sql_visit_details}")
        results = db.session.execute(sql_visit_details).fetchall()
        # logger.debug(f"{results}")
        clean_list = []
        result_dict['tableData'] = []
        for item in results:
            cur_visit = 0 if item[5] is None else item[5]
            yes_visit = 0 if item[6] is None else item[6]
            lastweek_visit = 0 if item[7] is None else item[7]
            yes_rate = None if yes_visit == 0 else cur_visit / yes_visit - 1
            lastweek_rate = None if lastweek_visit == 0 else cur_visit / lastweek_visit - 1
            # clean_list.append([item[0], cur_visit, yes_rate, lastweek_rate])
            if hos_grade == "市级医院":
                result_dict['tableData'].append(
                    dict(caption=item[1], cur_visit=cur_visit, yes_rate=yes_rate, lastweek_rate=lastweek_rate))
            else:
                result_dict['tableData'].append(
                    dict(caption=item[0], cur_visit=cur_visit, yes_rate=yes_rate, lastweek_rate=lastweek_rate))

        # data = [dict(caption=[i[0] for i in clean_list], cur_visit=[i[1] for i in clean_list], yes_rate=[i[2] for i in clean_list], lastweek_rate=[i[3] for i in clean_list])]

        return jsonify({"code": 1, 'data': result_dict, "msg": "success"})

class FeverDistrictHosView(Resource):
    def get(self):
        try:
            data = request.args
            dept_adrress = data.get("dept_adrress")
            select_date = data.get("select_date")
        except Exception as e:
            logger.exception(f"GET ARGS ERROR, EXCEPTION: {e}")
            return jsonify({"code": 0, "msg": "请求参数异常"})


    def post(self):
        try:
            data = request.json
            dept_adrress = data.pop("dept_adrress")  # 某个区
            select_date = data.pop("select_date")  # "2022-12-17"
            logger.debug(f"parameters: {data}")
        except Exception as e:
            logger.exception(f"GET ARGS ERROR, EXCEPTION: {e}")
            return jsonify({"code": 0, "msg": f"请求参数异常。{e}"})

        group_field = ""
        # 发热门诊就诊人次
        result_dict = {}
        sql_visit_details = f"""select aa.dept_adrress,aa.caption,aa.dept_code,aa.sf_sj,date_format(aa.time,'%Y-%m-%d') as time,aa.fever_visit,bb.fever_visit_yes,cc.fever_visit_lastweek  from 
                            (select tdh.dept_adrress,tdh.caption,tdh.dept_code,tdh.sf_sj,str_to_date(day, '%Y%m%d') as time,DATE_SUB(str_to_date(day, '%Y%m%d'),INTERVAL 1 DAY) as yesterday,DATE_SUB(str_to_date(day, '%Y%m%d'),INTERVAL 7 DAY) as last_week, CAST(SUM(frmz_zzll) AS SIGNED) as fever_visit
                            from tb_overview to2
                            inner join p_tb_dic_hos tdh on to2.dept_code=tdh.dept_code
                            group by tdh.dept_adrress,tdh.caption,tdh.dept_code,tdh.sf_sj,str_to_date(day, '%Y%m%d') ,DATE_SUB(str_to_date(day, '%Y%m%d'),INTERVAL 1 DAY),DATE_SUB(str_to_date(day, '%Y%m%d'),INTERVAL 7 DAY) ) aa
                            left join (select tdh.dept_adrress,tdh.caption, tdh.dept_code,tdh.sf_sj,str_to_date(day, '%Y%m%d') as time, CAST(SUM(frmz_zzll) AS SIGNED) as fever_visit_yes
                            from tb_overview to2
                            inner join p_tb_dic_hos tdh on to2.dept_code=tdh.dept_code
                            group by tdh.dept_adrress,tdh.caption,tdh.dept_code,tdh.sf_sj,str_to_date(day, '%Y%m%d')) bb on aa.yesterday =bb.TIME and aa.dept_code = bb.dept_code
                            left join (select tdh.dept_adrress,tdh.caption,tdh.dept_code,tdh.sf_sj,str_to_date(day, '%Y%m%d') as time, CAST(SUM(frmz_zzll) AS SIGNED) as fever_visit_lastweek
                            from tb_overview to2
                            inner join p_tb_dic_hos tdh on to2.dept_code=tdh.dept_code
                            group by tdh.dept_adrress,tdh.caption,tdh.dept_code,tdh.sf_sj,str_to_date(day, '%Y%m%d')) cc on aa.last_week =cc.time and aa.dept_code = cc.dept_code
                            where  aa.sf_sj is null and aa.time='{select_date}' and aa.dept_adrress='{dept_adrress}'
                            order by aa.fever_visit desc
                            """
        results = db.session.execute(sql_visit_details).fetchall()
        logger.debug(f"{results}")
        clean_list = []
        result_dict['tableData'] = []
        for item in results:
            cur_visit = 0 if item[5] is None else item[5]
            yes_visit = 0 if item[6] is None else item[6]
            lastweek_visit = 0 if item[7] is None else item[7]
            yes_rate = None if yes_visit == 0 else cur_visit / yes_visit - 1
            lastweek_rate = None if lastweek_visit == 0 else cur_visit / lastweek_visit - 1
            # clean_list.append([item[0], cur_visit, yes_rate, lastweek_rate])
            result_dict['tableData'].append(
                dict(caption=item[1], cur_visit=cur_visit, yes_rate=yes_rate, lastweek_rate=lastweek_rate))

        # data = [dict(caption=[i[0] for i in clean_list], cur_visit=[i[1] for i in clean_list], yes_rate=[i[2] for i in clean_list], lastweek_rate=[i[3] for i in clean_list])]

        return jsonify({"code": 1, 'data': result_dict, "msg": "success"})


########################################### Bilin  ######################################################
import datetime as dt

########################################### Bilin  ######################################################
import datetime as dt


class Kfcws(Resource):
    """
        接口用途：自动读取当前日期，提取 申康在院人数、开放床位数、床位使用率、床位使用率环比
        接收参数：不用接收参数
        接口返回：
            JSON格式：
                kfcws： 当天开放床位数
                zyrs：当天住院人数
                cwsyl：当天床位使用率，百分比
                cwsyl_hb：相比昨日床位使用率环比
    """

    def post(self):
        now_date = (datetime.now() + dt.timedelta(days=-1)).strftime("%Y%m%d")
        last_date = (datetime.now() + dt.timedelta(days=-2)).strftime("%Y%m%d")

        ##### 注意
        ##### 提交的时候，删除下面两行
        # now_date = "20221215"
        # last_date = "20221214"

        # 获取当前开放床位数
        now_kfcws = db.session.execute(
            "SELECT sum(kf_cws) FROM etl_sk.sk_day_report WHERE dept_code = '425009828' AND ywrq = '{}';".format(
                now_date)).fetchall()
        now_kfcws = now_kfcws[0][0]
        if now_kfcws == None:
            print("当天开放床位数为 0, 请核查是否是数据库未更新当天数据")
            now_kfcws = 0

        # 获取当天在院人数
        now_zyrs = db.session.execute(
            "SELECT sum(zyrs) FROM etl_sk.sk_day_report WHERE dept_code = '425009828' AND ywrq = '{}';".format(
                now_date)).fetchall()
        now_zyrs = now_zyrs[0][0]
        if now_zyrs == None:
            print("当天在院人数为 0, 请核查是否是数据库未更新当天数据")
            now_zyrs = 0

        # 计算当天床位使用率
        if now_kfcws != 0:
            now_cwsyl = round(100 * now_zyrs / now_kfcws, 2)
        else:
            now_cwsyl = 0  # 如果当天开放床位数为0，则认为当天床位数使用率为0

        # 获取前一天开放床位数
        last_kfcws = db.session.execute(
            "SELECT sum(kf_cws) FROM etl_sk.sk_day_report WHERE dept_code = '425009828' AND ywrq = '{}';".format(
                last_date)).fetchall()
        last_kfcws = last_kfcws[0][0]
        if last_kfcws == None:
            print("前一天开放床位数为 0, 请核查是否是数据库是否异常")
            last_kfcws = 0

        # 获取前一天在院人数
        last_zyrs = db.session.execute(
            "SELECT sum(zyrs) FROM etl_sk.sk_day_report WHERE dept_code = '425009828' AND ywrq = '{}';".format(
                last_date)).fetchall()
        last_zyrs = last_zyrs[0][0]
        if last_zyrs == None:
            print("前一天在院人数为 0, 请核查是否是数据库未更新当天数据")
            last_zyrs = 0

        # 计算前一天床位使用率
        if last_kfcws != 0:
            last_cwsyl = round(100 * last_zyrs / last_kfcws, 3)
        else:
            last_cwsyl = 0  # 如果前一天开放床位数为0，则认为当天床位数使用率为0

        # 计算床位使用率环比（昨日)
        cwsyl_hb = round(now_cwsyl - last_cwsyl, 3)

        data = {'kfcws': now_kfcws,
                'zyrs': now_zyrs,
                'cwsyl': now_cwsyl,
                'cwsyl_hb': cwsyl_hb
                }

        return jsonify({"code": 1, 'data': data, "msg": "success"})


#### 接口路由
api.add_resource(Kfcws, "/test/kfcws")
api.add_resource(TestView, "/test/info")
api.add_resource(FeverDetailsView, "/feverdetails/info")
api.add_resource(FeverDrilDownView, "/feverdrildown/info")
api.add_resource(FeverDistrictHosView, "/feverdistricthos/info")