# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# file      :point_to_line_distance.py
# target    :
# 
# output    :
# author    :Miller
# date      :2019/4/2 14:04
# log       :包含修改时间、修改人、修改line及原因
# --------------------------------------------------------------------------------
import numpy as np

from trajCluster.partition import _point2line_distance

start = np.array((0, 0))
end = np.array((3, 4))
point = np.array((0, 4))

d = np.abs(np.linalg.norm(np.cross(end-start, start-point))) / np.linalg.norm(end-start)
dd = _point2line_distance(point, start, end)
print(d, dd)
