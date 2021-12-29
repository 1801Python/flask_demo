# -*- coding: UTF-8 -*-
import json
import logging
import traceback

import logzero
import pike.discovery.py as discovery
from flask import Blueprint, Flask, Response, make_response, \
    jsonify
from flask.views import MethodView
from werkzeug.exceptions import HTTPException

_FORMAT = '%(color)s[%(levelname)s] %(message)s%(end_color)s'

LOG = logzero.setup_logger('demo.application',
                           level=logging.INFO,
                           formatter=logzero.LogFormatter(fmt=_FORMAT))


def _catch_all(error):
    if not isinstance(error, HTTPException):
        data = error.data if hasattr(error, 'data') else None
        tb = ''.join(traceback.format_tb(error.__traceback__))
        LOG.info('v' * 78)
        LOG.info(f'{error} {type(error)} \n{tb}'.strip())
        LOG.info('^' * 78)
        code = error.error_code if hasattr(error, 'error_code') else -1
        reason = error.message if hasattr(error, 'message') else str(error)
        retval = dict(msg=reason, data=data, code=code)
        retval['traceback'] = tb
        return Response(json.dumps(retval), 500)
    else:
        # LOG.info(error, exc_info=True)
        return error



def generate_bp(module):
    # 创建蓝图
    _bp = Blueprint('provider', __name__)
    num_routes = 0
    # 自动发现路由（具有 route 属性且值是 str 且具备响应请求的能力的类）
    for v in discovery.get_all_classes(module):
        if hasattr(v, 'route') and isinstance(v.route, str):
            LOG.info(f'Adding route {v.route} from {v.__name__} ...')
            # mapping
            _bp.add_url_rule(v.route, view_func=v.as_view(v.__name__))
            num_routes += 1
    LOG.info(f'#{num_routes} routes has been successfully added.')
    return _bp


def create_app(model):
    _app = Flask(__name__)
    # 创建并注册蓝图
    bp = generate_bp(model)
    _app.register_blueprint(bp)
    # 错误处理
    _app.register_error_handler(Exception, _catch_all)
    return _app


class BaseHandler(MethodView):

    @staticmethod
    def resp_format(code=0, msg='success', data=None):
        if type(data) == Response:
            return data
        return make_response(jsonify({
            'code': code,
            'msg': msg,
            'data': data
        }))
