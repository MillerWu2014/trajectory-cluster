# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------
# file      :partition_test.py
# target    :
# 
# output    :
# author    :Miller
# date      :2019/4/2 10:57
# log       :包含修改时间、修改人、修改line及原因
# --------------------------------------------------------------------------------
from trajCluster.partition import approximate_trajectory_partitioning, segment_mdl_comp, rdp_trajectory_partitioning
from trajCluster.point import Point

from matplotlib import pyplot as plt


ts = [582.0, 517.0, 586.0, 507.0, 584.0, 496.0, 584.0, 490.0, 587.0, 483.0, 591.0, 476.0, 595.0, 472.0, 601.0, 468.0, 605.0, 467.0, 609.0, 468.0, 606.0, 473.0, 605.0, 477.0, 604.0, 481.0, 600.0, 486.0, 596.0, 490.0, 593.0, 494.0, 589.0, 497.0, 579.0, 500.0, 563.0, 503.0, 556.0, 507.0, 547.0, 510.0, 534.0, 514.0, 525.0, 518.0, 517.0, 521.0, 510.0, 522.0, 505.0, 525.0, 500.0, 529.0, 496.0, 530.0, 492.0, 532.0, 486.0, 535.0, 477.0, 537.0, 471.0, 535.0, 468.0, 533.0, 463.0, 529.0, 456.0, 528.0, 453.0, 523.0, 453.0, 519.0, 454.0, 513.0, 453.0, 509.0, 445.0, 510.0, 433.0, 522.0, 432.0, 518.0, 432.0, 515.0, 428.0, 515.0, 425.0, 515.0, 423.0, 516.0, 422.0, 515.0, 424.0, 512.0, 431.0, 510.0, 433.0, 509.0, 434.0, 510.0, 428.0, 510.0, 423.0, 507.0, 420.0, 506.0, 416.0, 504.0, 405.0, 499.0, 398.0, 494.0, 391.0, 489.0, 384.0, 484.0, 387.0, 477.0, 392.0, 471.0, 399.0, 468.0, 403.0, 464.0, 403.0, 467.0, 403.0, 472.0, 403.0, 474.0, 396.0, 474.0, 392.0, 474.0, 391.0, 473.0, 390.0, 474.0, 388.0, 479.0, 387.0, 486.0, 381.0, 493.0, 376.0, 502.0, 367.0, 510.0, 360.0, 513.0, 352.0, 515.0, 342.0, 516.0, 330.0, 517.0, 319.0, 516.0, 305.0, 511.0, 298.0, 502.0, 292.0, 493.0, 293.0, 482.0, 307.0, 468.0, 320.0, 458.0, 341.0, 446.0, 359.0, 433.0]
traj = [Point(ts[i:i+2][0], ts[i:i+2][1]) for i in range(0, len(ts), 2)]


cost_par = segment_mdl_comp(traj, 0, 1, typed='par')
cost_nopar = segment_mdl_comp(traj, 0, 1, typed='nopar')

part = approximate_trajectory_partitioning(traj, theta=6.0)

# print([(p.start, p.end) for p in part])
source_line_x = [p.x for p in traj]
source_line_y = [p.y for p in traj]

dest_line_x = []
dest_line_y = []
i = 0
for s in part:
    if i == 0:
        dest_line_x.append(s.start.x)
        dest_line_y.append(s.start.y)
        dest_line_x.append(s.end.x)
        dest_line_y.append(s.end.y)
    else:
        dest_line_x.append(s.end.x)
        dest_line_y.append(s.end.y)
    i += 1

fig = plt.figure(figsize=(9, 6))
ax = fig.add_subplot(111)
ax.plot(source_line_x, source_line_y, 'g--', lw=2.0, label="trajectory")
ax.scatter(source_line_x, source_line_y, alpha=0.5)
ax.plot(dest_line_x, dest_line_y, lw=1.0, c='red', label="partition")
ax.scatter(dest_line_x, dest_line_y, alpha=0.5)

ax.legend()
plt.savefig('./figures/trajectory_partition_theta_5.png')
plt.show()

rdp_line_x = []
rdp_line_y = []
i = 0
for seg in rdp_trajectory_partitioning(traj, epsilon=5.0):
    if i == 0:
        rdp_line_x.append(seg.start.x)
        rdp_line_y.append(seg.start.y)
        rdp_line_x.append(seg.end.x)
        rdp_line_y.append(seg.end.y)
    else:
        rdp_line_x.append(seg.end.x)
        rdp_line_y.append(seg.end.y)
    i += 1

fig = plt.figure(figsize=(9, 6))
ax1 = fig.add_subplot(111)
ax1.plot(source_line_x, source_line_y, 'g--', lw=2.0, label="trajectory")
ax1.scatter(source_line_x, source_line_y, alpha=0.5)
ax1.plot(rdp_line_x, rdp_line_y, lw=1.0, c='red', label="rdp compression")
ax1.scatter(rdp_line_x, rdp_line_y, alpha=0.5)

ax1.legend()
plt.savefig('./figures/trajectory_rdp_eps_5.png')
plt.show()
