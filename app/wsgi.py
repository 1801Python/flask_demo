# -*- coding: UTF-8 -*-
from common.webeasy import create_app
from . import views


application = app = create_app(views)
