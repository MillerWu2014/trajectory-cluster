# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# file      :partition.py
# target    :对轨迹进行partition处理,
# 
# output    :
# author    :Miller
# date      :2019/4/2 9:23
# log       :包含修改时间、修改人、修改line及原因
# --------------------------------------------------------------------------------
import math

from .segment import Segment
from .point import _point2line_distance


eps = 1e-12   # defined the segment length theta, if length < eps then l_h=0


def segment_mdl_comp(traj, start_index, current_index, typed='par'):
    """计算MDL principle, MDL包括了两部分: L(H)和L(D|H), 在后面使用时也有'par'和'nopar'两种情况, 不同的情况下计算方式不同.其计算公式参考论文
    <<Trajectory Clustering: A Partition-and-Group Framework>>中的part3-TRAJECTORY PARTITIONING, 具体公式主要在(6), (7)两个.
    parameter
    ----------
        traj: List[(t, x, y)], 轨迹数据用列表表示, 轨迹中的一个点通过(time, x, y)的形式来定义
        start_index: int, 开始的索引, 轨迹中的开始索引位置.
        current_index: int, 当前索引位置
        typed: str, 'par' or ‘nopar’两个参数可选, 对应不同的计算结果
    return
    ------
        float, MDL的值, 在par的模式下包括了L(H)和L(D|H)两个部分, nopar模式只有L(H)部分"""
    length_hypothesis = 0
    length_data_hypothesis_perpend = 0
    length_data_hypothesis_angle = 0

    seg = Segment(traj[start_index], traj[current_index])
    if typed == "par" or typed == "PAR":
        if seg.length < eps:
            length_hypothesis = 0
        else:
            length_hypothesis = math.log2(seg.length)

    # compute the segment hypothesis
    for i in range(start_index, current_index, 1):
        sub_seg = Segment(traj[i], traj[i+1])  # 定义子segment
        if typed == 'par' or typed == 'PAR':
            length_data_hypothesis_perpend += seg.perpendicular_distance(sub_seg)
            length_data_hypothesis_angle += seg.angle_distance(sub_seg)
        elif typed == "nopar" or typed == "NOPAR":
            length_hypothesis += sub_seg.length

    if typed == 'par' or typed == 'PAR':
        if length_data_hypothesis_perpend > eps:
            length_hypothesis += math.log2(length_data_hypothesis_perpend)
        if length_data_hypothesis_angle > eps:
            length_hypothesis += math.log2(length_data_hypothesis_angle)
        return length_hypothesis
    elif typed == "nopar" or typed == "NOPAR":
        if length_hypothesis < eps:
            return 0
        else:
            return math.log2(length_hypothesis)  # when typed == nopar the L(D|H) is zero.
    else:
        raise ValueError("The parameter 'typed' given value has error!")


def approximate_trajectory_partitioning(traj, traj_id=None, theta=5.0):
    """按照论文中的算法流程实现轨迹的partition部分, 主要通过MDL来确定特征点并实现的轨迹分段, 其中theta可以视为惩罚参数,若theta越大那么轨迹
    压缩率越大.
    parameter
    ---------
        traj: List[Point[x, y], ...], 一个完整轨迹的列表, 其中轨迹点必须为Point类型.
        traj_id: int, 轨迹ID
        theta: float, 可是视为轨迹压缩率的控制参数, 在原始的论文中无次参数.
    return
    ------
        List[Segment[Point, Point], ...], 返回所有的分段后的轨迹列表.
    """
    size = len(traj)
    start_index: int = 0; length: int = 1

    partition_trajectory = []
    while (start_index + length) < size:
        curr_index = start_index + length
        cost_par = segment_mdl_comp(traj, start_index, curr_index, typed='par')
        cost_nopar = segment_mdl_comp(traj, start_index, curr_index, typed='nopar')
        if cost_par > (cost_nopar+theta):
            seg = Segment(traj[start_index], traj[curr_index-1], traj_id=traj_id)
            partition_trajectory.append(seg)
            start_index = curr_index - 1
            length = 1
        else:
            length += 1
    seg = Segment(traj[start_index], traj[size-1], traj_id=traj_id, cluster_id=-1)
    partition_trajectory.append(seg)
    return partition_trajectory


def rdp_trajectory_partitioning(trajectory, traj_id=None, epsilon=1.0):
    """实现轨迹压缩的Ramer-Douglas-Peucker算法, 实现对轨迹中的重要点进行提取并实现轨迹的分割, 和上面的partition方法的返回结果一致
    parameter
    ---------
        trajectory: List[Point[x, y], ...], 轨迹数据列表, 按照时间先后排序, 轨迹中的点都通过Point形式进行表示.
        epsilon: float, 距离阈值, 需要通过阈值来控制轨迹压缩的程度.
    """
    size = len(trajectory)
    d_max = 0.0
    index = 0
    for i in range(1, size-1, 1):
        d = _point2line_distance(trajectory[i].as_array(), trajectory[0].as_array(), trajectory[-1].as_array())
        if d > d_max:
            d_max = d
            index = i

    if d_max > epsilon:
        result = rdp_trajectory_partitioning(trajectory[:index+1], epsilon=epsilon) + \
                 rdp_trajectory_partitioning(trajectory[index:], epsilon=epsilon)
    else:
        result = [Segment(trajectory[0], trajectory[-1], traj_id=traj_id, cluster_id=-1)]
    return result
