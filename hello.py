#!usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author:cugxy
@file: $NAME.py
@time: 2018/10/26
"""

from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


if __name__ == "__main__":
    app.run()
