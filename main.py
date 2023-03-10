from math import sqrt
import numpy as np
import pandas as pd
import utils
from math import exp


class SOStream:

def initial(self, alpha = 0.1, min_pts = 10, merge_threshold = 27000):
    self.alpha = alpha
    self.min_pts = min_pts
    self.M = [[]]
    self.merge_threshold = merge_threshold

def process(self, vt):
    winner_micro_cluster = min_dist(vt, self.M[-1])
    new_M = self.M[-1].copy()
        if len(new_M) >= self.min_pts:
            winner_neighbor = find_neighbors(winner_micro_cluster, self.min_pts, new_M)
            if dist(vt, winner_micro_cluster.centroid) < winner_micro_cluster.radius:
                updateCluster(winner_micro_cluster, vt, self.alpha, winner_neighbor)
            else:
                new_M.append(newCluster(vt))
                
                
            overlap = find_overlap(winner_micro_cluster, winner_neighbor)
            if len(overlap) > 0:
                merged_cluster, deleted_clusters = merge_clusters(winner_micro_cluster, overlap, self.merge_threshold)
                for deleted_cluster in deleted_clusters:
                    new_M.remove(deleted_cluster)
                if merged_cluster is not None:
                    new_M.append(merged_cluster)
        else:
            new_M.append(newCluster(vt))
        self.M.append(new_M)
    pass



def dist(v1, v2):
    return np.sqrt(((v1 - v2) ** 2).sum())


def weighted_mean(a, b, wieght_a, wieght_b):
    return ((wieght_a * a + wieght_b * b)/(wieght_a + wieght_b))


def min_dist(vt, micro_clusters):
    micro_cluster_min_dist = float('inf')
    min_micro_cluster = None
    for micro_cluster in micro_clusters:
        dist_to_micro_cluster = dist(vt, micro_cluster.centroid)
        if dist_to_micro_cluster <= micro_cluster_min_dist:
            micro_cluster_min_dist = dist_to_micro_cluster
            min_micro_cluster = micro_cluster
    
    return min_micro_cluster





def find_neighbors(win_microcluster, min_pts, model_t):
  if len(model_t) >= min_pts:
    win_dist = []
    for microcluster in model_t:
      win_dist.append(utils.dist(microcluster.centroid, win_microcluster.centroid))
    win_dist.sort()
    idx_microclusters = np.argsort(win_dist)
    
    k_dist = win_dist[min_pts-1]
    win_microcluster.radius = k_dist
    win_nn = [model_t[idx] for idx in idx_microclusters[0:(min_pts)]]
    return win_nn
  else:
    return []




def updateCluster(win_micro_cluster, vt, alpha, winner_neighbor):
    win_micro_cluster.centroid = (win_micro_cluster.number_points * win_micro_cluster.centroid + vt) / (win_micro_cluster.number_points+1)
    win_micro_cluster.number_points += 1
    width_neighbor = win_micro_cluster.radius ** 2
    for neighbor_micro_cluster in winner_neighbor:
        influence = exp(-(dist(neighbor_micro_cluster.centroid, win_micro_cluster.centroid)/(2 * width_neighbor)))
        neighbor_micro_cluster.centroid = neighbor_micro_cluster.centroid + alpha*influence*(win_micro_cluster.centroid-neighbor_micro_cluster.centroid)




def find_overlap(win, win_nn):
  overlap = []
  for microcluster in win_nn:
    if win is not microcluster:
      if utils.dist(win.centroid, microcluster.centroid) - (win.radius + microcluster.radius) < 0 :
        overlap.append(microcluster)
  return overlap



class MicroCluster:

def initial(self, centroid, number_points = 1, radius = 0):
        self.number_points = number_points
        self.radius = radius
        self.centroid = centroid

    pass



def merge_clusters(win_micro_cluster, overlaping_micro_clusters, merge_threshold):
    merged_cluster = None
    deleted_clusters = list()
    for micro_cluster in overlaping_micro_clusters:
        if dist(micro_cluster.centroid, win_micro_cluster.centroid) < merge_threshold:
            if len(deleted_clusters) == 0:
                deleted_clusters.append(win_micro_cluster)
                merged_cluster = MicroCluster(win_micro_cluster.centroid,
                                              number_points=win_micro_cluster.number_points,
                                              radius=win_micro_cluster.radius)
            merged_cluster = merge(micro_cluster, merged_cluster)
            deleted_clusters.append(micro_cluster)
    return merged_cluster, deleted_clusters


def merge(cluster_a, cluster_b):
    new_cluster_centroid = weighted_mean(cluster_a.centroid, cluster_b.centroid, cluster_a.number_points, cluster_b.number_points)
    new_cluster_radius = dist(cluster_a.centroid, cluster_b.centroid) + max(cluster_a.radius, cluster_b.radius)
    new_cluster = MicroCluster(centroid=new_cluster_centroid,
                               number_points=cluster_a.number_points + cluster_b.number_points,
                               radius=new_cluster_radius)
    return new_cluster




def newCluster(vt):
    return MicroCluster(vt)



