# -*- coding:utf-8 -*-

import os
import zipfile


def unzip(path):
    temp_dir = os.path.dirname(path)
    zfile = zipfile.ZipFile(path, "r")
    for subfile in zfile.namelist(): 
        zfile.extract(subfile, temp_dir)
    zfile.close()