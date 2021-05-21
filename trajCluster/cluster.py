# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# file      :cluster.py
# target    :轨迹之间聚类实现, 对所有的segment进行聚类, 使用dbscan密度聚类来实现segment的聚类
#
# output    :
# author    :Miller
# date      :2019/4/1 14:13
# log       :包含修改时间、修改人、修改line及原因
# --------------------------------------------------------------------------------
import math

from .segment import compare, Segment
from .point import Point
from collections import deque, defaultdict

min_traj_cluster = 2  # 定义聚类的簇中至少需要的trajectory数量


def neighborhood(seg, segs, epsilon=2.0):
    """计算一个segment在距离epsilon范围内的所有segment集合, 计算的时间复杂度为O(n). n为所有segment的数量
    parameter
    ---------
        seg: Segment instance, 需要计算的segment对象
        segs: List[Segment, ...], 所有的segment集合, 为所有集合的partition分段结果集合
        epsilon: float, segment之间的距离度量阈值
    return
    ------
        List[segment, ...], 返回seg在距离epsilon内的所有Segment集合.
    """
    segment_set = []
    for segment_tmp in segs:
        seg_long, seg_short = compare(seg, segment_tmp)  # get long segment by compare segment
        if seg_long.get_all_distance(seg_short) <= epsilon:
            segment_set.append(segment_tmp)
    return segment_set


def expand_cluster(segs, queue: deque, cluster_id: int, epsilon: float, min_lines: int):
    while len(queue) != 0:
        curr_seg = queue.popleft()
        curr_num_neighborhood = neighborhood(curr_seg, segs, epsilon=epsilon)
        if len(curr_num_neighborhood) >= min_lines:
            for m in curr_num_neighborhood:
                if m.cluster_id == -1:
                    queue.append(m)
                    m.cluster_id = cluster_id
        else:
            pass


def line_segment_clustering(traj_segments, epsilon: float = 2.0, min_lines: int = 5):
    """线段segment聚类, 采用dbscan的聚类算法, 参考论文中的伪代码来实现聚类, 论文中的part4.2部分中的伪代码及相关定义
    parameter
    ---------
        traj_segments: List[Segment, ...], 所有轨迹的partition划分后的segment集合.
        epsilon: float, segment之间的距离度量阈值
        min_lines: int or float, 轨迹在epsilon范围内的segment数量的最小阈值
    return
    ------
        Tuple[Dict[int, List[Segment, ...]], ...], 返回聚类的集合和不属于聚类的集合, 通过dict表示, key为cluster_id, value为segment集合
    """
    cluster_id = 0
    cluster_dict = defaultdict(list)
    for seg in traj_segments:
        _queue = deque(list(), maxlen=50)
        if seg.cluster_id == -1:
            seg_num_neighbor_set = neighborhood(seg, traj_segments, epsilon=epsilon)
            if len(seg_num_neighbor_set) >= min_lines:
                seg.cluster_id = cluster_id
                for sub_seg in seg_num_neighbor_set:
                    sub_seg.cluster_id = cluster_id  # assign clusterId to segment in neighborhood(seg)
                    _queue.append(sub_seg)  # insert sub segment into queue
                expand_cluster(traj_segments, _queue, cluster_id, epsilon, min_lines)
                cluster_id += 1
            else:
                seg.cluster_id = -1
        # print(seg.cluster_id, seg.traj_id)
        if seg.cluster_id != -1:
            cluster_dict[seg.cluster_id].append(seg)  # 将轨迹放入到聚类的集合中, 按dict进行存放

    remove_cluster = dict()
    cluster_number = len(cluster_dict)
    for i in range(0, cluster_number):
        traj_num = len(set(map(lambda s: s.traj_id, cluster_dict[i])))  # 计算每个簇下的轨迹数量
        print("the %d cluster lines:" % i, traj_num)
        if traj_num < min_traj_cluster:
            remove_cluster[i] = cluster_dict.pop(i)
    return cluster_dict, remove_cluster


def representative_trajectory_generation(cluster_segment: dict, min_lines: int = 3, min_dist: float = 2.0):
    """通过论文中的算法对轨迹进行变换, 提取代表性路径, 在实际应用中必须和当地的路网结合起来, 提取代表性路径, 该方法就是通过算法生成代表性轨迹
    parameter
    ---------
        cluster_segment: Dict[int, List[Segment, ...], ...], 轨迹聚类的结果存储字典, key为聚类ID, value为类簇下的segment列表
        min_lines: int, 满足segment数的最小值
        min_dist: float, 生成的轨迹点之间的最小距离, 生成的轨迹点之间的距离不能太近的控制参数
    return
    ------
        Dict[int, List[Point, ...], ...], 每个类别下的代表性轨迹结果
    """
    representive_point = defaultdict(list)
    for i in cluster_segment.keys():
        cluster_size = len(cluster_segment.get(i))
        sort_point = []  # [Point, ...], size = cluster_size*2
        rep_point, zero_point = Point(0, 0, -1), Point(1, 0, -1)

        # 对某个i类别下的segment进行循环, 计算类别下的平局方向向量: average direction vector
        for j in range(cluster_size):
            rep_point = rep_point + (cluster_segment[i][j].end - cluster_segment[i][j].start)
        rep_point = rep_point / float(cluster_size)  # 对所有点的x, y求平局值

        cos_theta = rep_point.dot(zero_point) / rep_point.distance(Point(0, 0, -1))  # cos(theta)
        sin_theta = math.sqrt(1 - math.pow(cos_theta, 2))  # sin(theta)

        # 对某个i类别下的所有segment进行循环, 每个点进行坐标变换: X' = A * X => X = A^(-1) * X'
        #   |x'|      | cos(theta)   sin(theta) |    | x |
        #   |  |  =   |                         | *  |   |
        #   |y'|      |-sin(theta)   cos(theta) |    | y |
        for j in range(cluster_size):
            s, e = cluster_segment[i][j].start, cluster_segment[i][j].end
            # 坐标轴变换后进行原有的segment修改
            cluster_segment[i][j] = Segment(Point(s.x * cos_theta + s.y * sin_theta, s.y * cos_theta - s.x * sin_theta, -1),
                                            Point(e.x * cos_theta + e.y * sin_theta, e.y * cos_theta - e.x * sin_theta, -1),
                                            traj_id=cluster_segment[i][j].traj_id,
                                            cluster_id=cluster_segment[i][j].cluster_id)
            sort_point.extend([cluster_segment[i][j].start, cluster_segment[i][j].end])

        # 对所有点进行排序, 按照横轴的X进行排序, 排序后的point列表应用在后面的计算中
        sort_point = sorted(sort_point, key=lambda _p: _p.x)
        for p in range(len(sort_point)):
            intersect_cnt = 0.0
            start_y = Point(0, 0, -1)
            for q in range(cluster_size):
                s, e = cluster_segment[i][q].start, cluster_segment[i][q].end
                # 如果点在segment内则进行下一步的操作:
                if (sort_point[p].x <= e.x) and (sort_point[p].x >= s.x):
                    if s.x == e.x:
                        continue
                    elif s.y == e.y:
                        intersect_cnt += 1
                        start_y = start_y + Point(sort_point[p].x, s.y, -1)
                    else:
                        intersect_cnt += 1
                        start_y = start_y + Point(sort_point[p].x, (e.y-s.y)/(e.x-s.x)*(sort_point[p].x-s.x)+s.y, -1)
            # 计算the average coordinate: avg_p and dist >= min_dist
            if intersect_cnt >= min_lines:
                tmp_point: Point = start_y / intersect_cnt
                # 坐标转换到原始的坐标系, 通过逆矩阵的方式进行矩阵的计算:https://www.shuxuele.com/algebra/matrix-inverse.html
                tmp = Point(tmp_point.x*cos_theta-sin_theta*tmp_point.y,
                            sin_theta*tmp_point.x+cos_theta*tmp_point.y, -1)
                _size = len(representive_point[i]) - 1
                if _size < 0 or (_size >= 0 and tmp.distance(representive_point[i][_size]) > min_dist):
                    representive_point[i].append(tmp)
    return representive_point
