#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
贸泽电子元器件价格爬虫主程序
"""

import subprocess
import sys
import os

def main():
    # 运行Streamlit应用
    subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])

if __name__ == "__main__":
    main()