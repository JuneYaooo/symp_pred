# -*- coding: utf-8 -*-
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = "mysql://root:Rootdata_200@1.116.135.31:10028/etl_sk?charset=utf8mb4"
SQLALCHEMY_POOL_SIZE = 5
SQLALCHEMY_POOL_TIMEOUT = 10
SQLALCHEMY_POOL_RECYCLE = 60 * 10
SQLALCHEMY_RECORD_QUERIES = True
IDENTIFY_TOKEN = False

PIC_TYPE = ['bmp', 'png', 'jpeg', 'jpg']
VIDEO_TYPE = ['mp4', 'avi']

TOKEN_INVALID_TIME = 3 * 24 * 60 * 60
SECRET_KEY = 'prd-screen-api'

CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://:Redis@DB123@redis:6379/1'

API_LOG_PATH = "/data/log/api.{time:YYYY-MM-DD}.log"
