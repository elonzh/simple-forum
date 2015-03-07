# -*- coding:utf-8 -*-
"""
SAE 部署文件
"""

import sys
import os

root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(root, 'site-packages'))

import sae
from app import app

application = sae.create_wsgi_app(app)