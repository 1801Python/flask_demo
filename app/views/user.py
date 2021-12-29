# -*- coding: UTF-8 -*-
from common.webeasy import BaseHandler

from app.controllers import user as user_controller


class UserStatusView(BaseHandler):

    route = '/api/v1/user'

    def get(self):
        data = user_controller.get_user()
        return self.resp_format(data=data)
