# -*- coding: utf-8 -*-
import csv
import time
start_time = time.time()
from Import_hex import import_file

from VariableFieldExtraction import entopy_anlysis

from collections import defaultdict

from LengthByteAssociationRecognition import len_cluster, cluster
from LengthByteAssociationRecognition import x_kmeans
import os
from LengthByteAssociationRecognition import find_candidate_field, find_target_byte
from LengthFieldExtraction import determine_field


if __name__ == '__main__':

    file = 'D:/PyCharmProjects/FENCE/dnp3_100.pcap'
    trans_file = 'D:/paperdata/txtfile.txt'

    # 导入文件
    pcapng_file = os.path.normpath(file)

    import_data = import_file(pcapng_file, trans_file)

    # 消息类型聚类
    # 仅包含目标协议的数

    cluster_data_k = x_kmeans(import_data)
    lmin = 16
    cluster_data_k = len_cluster(cluster_data_k, lmin)
    len_idx = []
    len_k = []
    for i in range(len(cluster_data_k)):
        idx, idx_k = find_candidate_field(cluster_data_k[i])
        len_idx.append(idx)
        len_k.extend(idx_k)

    print(f"len_idx:{len_idx}")
    print(f"len_k:{len_k}")
    print(f"len of len_k:{len(len_k)}")
    target_indices, values_k = find_target_byte(len_idx, len_k, cluster_data_k)
    if target_indices:
        print(f"target_indices:{target_indices}")
    else:
        print(f"No a specific byte!")

    print(f"values_k:{values_k}")
    cluster_data = x_kmeans(import_data)
    offset = entopy_anlysis(cluster_data,values_k)

    determine_field(cluster_data_k, offset, values_k, target_indices)
    end_time = time.time()
    print(f"运行时间为：{end_time-start_time}")

