# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# file      :segment_test.py
# target    :
# 
# output    :
# author    :Miller
# date      :2019/4/1 16:05
# log       :包含修改时间、修改人、修改line及原因
# --------------------------------------------------------------------------------
from trajCluster.segment import Segment
from trajCluster.point import Point

s = Point(1.0, 2.0)
e = Point(10.0, 2.0)

se1 = Segment(s, e, traj_id=1)
se2 = Segment(Point(3.0, 5.0), Point(7.0, 8.0))
x = se1.perpendicular_distance(se2)
print("两个segment的垂直距离为:", x)

y = se1.parallel_distance(se2)
print("两个segment的长度距离为:", y)

z = se1.angle_distance(se2)
print("两个segment的角度距离为:", z)
