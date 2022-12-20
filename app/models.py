# -*- coding:utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
import app

db = SQLAlchemy()


class TbOverview(db.Model):
    day = Column(String(8), primary_key=True)
    dept_code = Column(String(9), primary_key=True)
    caption = Column(String(100))
    dept_adrresscode = Column(String(6))
    yydj_j = Column(String(1))
    dept_class = Column(String(4))
    szxgq_kcs = Column(db.Integer)

    __table_args__ = (
        UniqueConstraint("day", "dept_code", name="ix_unq"),
    )

    __mapper_args__ = {
        "order_by": day.desc()
    }


class TbDicHos(db.Model):
    dept_code = Column(String(16), primary_key=True)
    caption = Column(String(32), primary_key=True)
    dept_adrress = Column(String(4))
    yydj_j = Column(String(3))
    dept_class = Column(String(8))
    sf_sj = Column(Integer)
