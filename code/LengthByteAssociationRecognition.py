from collections import Counter
import math
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np
from pyclustering.cluster.center_initializer import kmeans_plusplus_initializer
from pyclustering.cluster.xmeans import xmeans
from sklearn.metrics.cluster import normalized_mutual_info_score
from collections import defaultdict



class Packet:
    """数据包类"""

    def __init__(self):
        self.index = 0  # 该数据包的在数据集中的索引
        self.bytelen = 0  # 该数据包的字节长度
        self.content = []
        self.headerlen = 0
        self.offset = 0
        self.length = 0
        self.distance = 0


def PacketLen(packet: list) -> int:
    """
    计算数据包的长度
    :param packet: 列表元素为划分后的各个字段
    :return: 该数据包的字节长度
    """
    midlen = 0
    for i in range(len(packet)):
        midlen += len(packet[i])
    midlen = midlen // 2
    return midlen


def PacketsExpress(packets_list: dict) -> list:
    """
    记录每条数据包的属性：索引和字节长度
    :param FieldSegment: 文件读取后的数据包的字段划分结果 ,列表元素为字符串形式的字段划分结果
    :return: 返回包含每个数据包类实例的列表
    """
    packetclass_list = []
    count = 0
    for key, value in packets_list.items():
        for msg in value:
            unit = msg
            packet = Packet()
            packet.index = count
            packet.bytelen = key
            packet.content = unit
            packetclass_list.append(packet)
            count += 1
    return packetclass_list


import random


def RecombPacketsExpress(packets_list: dict) -> list:
    """
    记录每条数据包的属性：索引和字节长度
    从所有数据中随机选取20%的数据，按原始顺序两两合并
    :param packets_list: 字典，键为字节长度，值为该长度对应的消息列表
    :return: 返回包含每个数据包类实例的列表
    """
    # 1. 先按原逻辑生成完整的 packetclass_list
    packetclass_list = []
    count = 0
    for key, value in packets_list.items():
        for msg in value:
            packet = Packet()
            packet.index = count
            packet.bytelen = key
            packet.content = msg
            packetclass_list.append(packet)
            count += 1

    # 2. 如果总消息数少于4条，无法合并成两对，直接返回原列表
    total_count = len(packetclass_list)
    if total_count < 4:
        return packetclass_list

    # 3. 计算需要参与合并的消息数量（占总数的20%），确保为偶数
    merge_count = int(total_count * 0.5)
    if merge_count % 2 != 0:
        merge_count -= 1  # 调整为偶数，保证能两两配对
    if merge_count < 2:
        return packetclass_list

    # 4. 从所有数据中随机选取需要合并的消息索引
    all_indices = list(range(total_count))
    selected_indices = random.sample(all_indices, merge_count)

    # 5. 将选中的索引按原始顺序排序（保证按原始顺序两两合并）
    selected_indices.sort()

    # 记录哪些索引已被合并（用于后续删除）
    indices_to_remove = set()

    # 6. 按原始顺序两两配对合并
    for i in range(0, len(selected_indices), 2):
        idx1 = selected_indices[i]
        idx2 = selected_indices[i + 1]

        # 获取两条消息
        p1 = packetclass_list[idx1]
        p2 = packetclass_list[idx2]

        # 合并内容（按原始顺序拼接）
        merged_content = p1.content + p2.content
        merged_bytelen = p1.bytelen + p2.bytelen

        # 用 idx1 的位置存放合并后的消息（保留较小索引位置）
        p1.content = merged_content
        p1.bytelen = merged_bytelen
        # 标记 idx2 为待删除
        indices_to_remove.add(idx2)

    # 7. 按索引倒序删除被合并掉的消息（避免索引变动问题）
    for idx in sorted(indices_to_remove, reverse=True):
        del packetclass_list[idx]

    # 8. 重新为剩余消息分配连续索引
    for new_idx, packet in enumerate(packetclass_list):
        packet.index = new_idx

    return packetclass_list


def byte_data(hex_data):
    data_list = []
    for item in hex_data:
        if isinstance(item, list):  # 处理嵌套列表
            data_list.extend(item)
        elif isinstance(item, str):  # 处理字符串
            data_list.append(item)
        elif isinstance(item, bytes):  # 正确的字节数据
            data_list.append(item)
        else:
            raise TypeError(f"Unsupported data type: {type(item)}")

    byte_data = defaultdict(list)
    # print(f"data_list:{data_list}")
    for line in data_list:
        msg_len = PacketLen([line])
        if msg_len > 1460:
            print(f"msg_len:{msg_len}")
            byte_line = [line[i:i + 2] for i in range(0, 1460 * 2 - 1, 2)]
        else:
            byte_line = [line[i:i + 2] for i in range(0, len(line) - 1, 2)]
        byte_data[msg_len].append(byte_line)

    return dict(byte_data)


def cluster(data):
    byte_msg = byte_data(data)
    msg = PacketsExpress(byte_msg)

    max_length = max([len(sublist.content) for sublist in msg])
    # print(f"max_length:{max_length}")
    data_padded = [sublist.content + ['00'] * (max_length - len(sublist.content)) for sublist in msg]
    data_int = [[int(val, 16) for val in sublist] for sublist in data_padded]

    # 自动确定聚类数
    max_clusters = 8
    best_score = -1
    best_clusters = 2
    for k in range(2, max_clusters + 1):
        kmeans = KMeans(n_clusters=k, random_state=0).fit(data_int)
        labels = kmeans.labels_
        score = silhouette_score(data_int, labels)
        if score > best_score:
            best_score = score
            best_clusters = k
    print('最佳聚类数：{}'.format(best_clusters))

    kmeans = KMeans(n_clusters=best_clusters, random_state=0).fit(data_int)
    labels = kmeans.labels_
    result = [[] for _ in range(max(labels) + 1)]
    for i, sublist in enumerate(msg):
        result[labels[i]].append(sublist)

    return result


def kmeans(data):
    # 将数据转换成二维数组
    data_int = np.array(data).reshape(-1, 1)

    max_clusters = 8
    best_score = -1
    best_clusters = 6

    for k in range(6, max_clusters + 1):
        kmeans = KMeans(n_clusters=k, random_state=0).fit(data_int)
        labels = kmeans.labels_
        score = silhouette_score(data_int, labels)
        if score > best_score:
            best_score = score
            best_clusters = k

    print('最佳聚类数：{}'.format(best_clusters))

    # 使用最佳簇数进行最终聚类
    final_kmeans = KMeans(n_clusters=best_clusters, random_state=0).fit(data_int)
    labels = final_kmeans.labels_
    centers = final_kmeans.cluster_centers_
    return labels


def x_kmeans(data):
    real_results = []
    byte_msg = byte_data(data)
    msg = PacketsExpress(byte_msg)
    max_length = max([len(sublist.content) for sublist in msg])
    print(f"max_length:{max_length}")
    data_padded = [sublist.content + ['00'] * (max_length - len(sublist.content)) for sublist in msg]
    data_int = [[int(val, 16) for val in sublist] for sublist in data_padded]

    X = np.array(data_int)

    initial_centers = kmeans_plusplus_initializer(data_int, 2).initialize()
    xmeans_instance = xmeans(data_int, initial_centers)
    xmeans_instance.process()

    clusters = xmeans_instance.get_clusters()
    centers = xmeans_instance.get_centers()
    labels = np.zeros(len(X), dtype=int)
    results = [[] for _ in range(len(clusters))]

    print(f"聚类完成， 共分为 {len(clusters)} 个簇： ")
    for cluster_idx, cluster in enumerate(clusters):
        print(f"簇 {cluster_idx + 1}: 包含 {len(cluster)} 个样本")
        for sample_idx in cluster:
            labels[sample_idx] = cluster_idx

    for idx, subresult in enumerate(msg):
        results[labels[idx]].append(subresult)

    if len(centers) >= 10:
        # print(f"len of centers:{len(centers)},centers:{centers}")
        avg_centers = []
        for center in centers:
            avg = sum(center) / len(centers)
            avg_centers.append(avg)

        avg_labels = kmeans(avg_centers)

        cluster_label = defaultdict(list)
        for idx, label in enumerate(avg_labels):
            cluster_label[label].append(idx)

        cluster_label = dict(cluster_label)

        for idx in cluster_label.values():
            temp_result = []
            for i, result in enumerate(results):
                if i in idx:
                    temp_result.extend(result)
            if len(temp_result) > 8:
                real_results.append(temp_result)
    else:
        real_results = results

    print(f"聚类完成， 共分为 {len(real_results)} 个簇： ")

    return real_results


def calculate_shannon_entropy(data):
    byte_msg = []
    for submsg in data:
        byte_msg.append(submsg.content)
    num_rows = len(byte_msg)
    num_cols = len(byte_msg[0])
    shannon_entropies = []
    for col in range(num_cols):
        column_values = [byte_msg[row][col] for row in range(num_rows)]
        value_counts = Counter(column_values)  # 统计column_values中每个元素出现的次数，会返回一个字典形式的计数结果
        prob_dist = [count / num_rows for count in value_counts.values()]
        shannon_entropy = -sum(prob * math.log2(prob) for prob in prob_dist)
        shannon_entropies.append(shannon_entropy)
    return shannon_entropies


def len_sort_k(data, lmin):
    result = {}
    for sublist in data:
        length = sublist.bytelen
        sublist.content = sublist.content[:lmin]
        if length not in result:
            result[length] = [sublist]
        else:
            result[length].append(sublist)
    sort_list = []
    for key in result:
        sort_list.append(result[key])
    print('len_sort successfully!total:{}'.format(len(sort_list)))
    return sort_list


def len_cluster(cluster_data_k, lmin):
    sorted_cluster = []
    for cluster_data in cluster_data_k:
        sorted_list = len_sort_k(cluster_data, lmin)
        sorted_cluster.append(sorted_list)

    return sorted_cluster


def len_sort(data):
    result = {}
    for sublist in data:
        length = sublist.bytelen
        if length not in result:
            result[length] = [sublist]
        else:
            result[length].append(sublist)
    sort_list = []
    for key in result:
        sort_list.append(result[key])
    print('len_sort successfully!total:{}'.format(len(sort_list)))
    return sort_list


def find_most_frequent(lst):
    filtered_lst = [num for num in lst if num < 15]
    counter = Counter(filtered_lst)
    most_common = counter.most_common(1)
    return most_common[0][0] if most_common else None


def compute_k(data):
    """
    计算 data 中每一列的 k 值，k = msg_len - int(单元格内容的16进制值)
    并去除每列重复的 k 值，返回字典 idx，key为列号，value为该列k值列表。
    """
    # 假设所有行的 length 属性一致
    msg_len = data[0].bytelen

    # 收集所有行的 content，假设 content 是可迭代的16进制字符串列表
    msg = [line.content for line in data]

    # 转置，按列遍历
    columns = list(zip(*msg))

    idx = defaultdict(list)
    for col_idx, col_values in enumerate(columns):
        for v in col_values:
            val = int(v, 16)
            if val <= msg_len:
                k = msg_len - val
                # 去重
                if k not in idx[col_idx]:
                    idx[col_idx].append(k)
    filtered_idx = {k: v for k, v in idx.items() if len(v) == 1}

    return dict(filtered_idx)  # 转为普通dict返回，方便使用


def trans_byte(data):
    msg = []
    for line in data:
        temp_data = []
        for i in range(0, len(line) - 1, 2):
            temp_data.append(line[i:i + 2])
        msg.append(temp_data)

    return msg


def unique_list(data):
    return list(set(data))


def list_strmsg(data):
    list_str = []
    for line in data:
        sample = line.content
        list_str.append(''.join(sample))
    return list_str


def find_relation(data):
    msg_index = []

    list_str = list_strmsg(data)
    unique_data = unique_list(list_str)
    unique_byte = trans_byte(unique_data)
    msg_len = data[0].bytelen
    length = []
    for line in unique_byte:
        length.append(msg_len)
        temp_idx = []
        temp_data = []
        for i in range(len(line)):
            if int(line[i], 16) <= msg_len:
                if line[i] not in temp_idx:
                    temp_idx.append(i)
                    temp_data.append(int(line[i], 16))
        msg_index.append(list(zip(temp_idx, temp_data)))
    return msg_index, length


def group_all_tuples_by_first_element(data):
    groups = defaultdict(list)

    # 遍历所有行
    for key in data:
        for lst in data[key]:  # 每行的列表
            for tup in lst:  # 每个元组
                groups[tup[0]].append(tup)  # 按第一个元素分组

    # 按第一个元素排序（可选）
    sorted_groups = dict(sorted(groups.items()))
    return sorted_groups


def find_candidate_field(cluster_data):
    idx = {}
    msg_len = []
    idx_k = []
    for i in range(len(cluster_data)):
        idx[i], length = find_relation(cluster_data[i])
        idx_k.append(compute_k(cluster_data[i]))
        msg_len.extend(length)

    reassmbled_idx = group_all_tuples_by_first_element(idx)
    print(reassmbled_idx)
    nmi_results = {}
    print(f"msg_len:{msg_len}")
    for id, data in reassmbled_idx.items():
        if len(data) <= len(msg_len):
            v_values = [tup[1] for tup in data] + [0] * (len(msg_len) - len(data))
            nmi = normalized_mutual_info_score(v_values, msg_len)
            nmi_results[id] = nmi

    final_idx = []
    for key in nmi_results:
        print(f"key:{key},nmi:{nmi_results[key]}")
        if nmi_results[key] > 0.95:
            final_idx.append(key)
    return final_idx, idx_k


def group_all_tuples_by_key(len_k):
    merged = defaultdict(list)

    for d in len_k:
        for k, v in d.items():
            merged[k].extend(v)
    merged = dict(merged)

    print(f"merged:{merged}")
    return merged


def find_most_frequent_k(data):
    filtered_lst = [num for num in data if num < 15]
    counter = Counter(filtered_lst)
    most_common = counter.most_common(1)
    return most_common[0] if most_common else None


def find_k(merged_k, cluster_len):
    target_k_idx = []
    values_k = []
    for key, values in merged_k.items():
        k = list(set(values))
        common_k = find_most_frequent_k(values)
        if common_k:
            common_k = list(common_k)
        ratio = len(values) / cluster_len
        if len(k) == 1 and ratio > 0.90:
            # print(f"len(k) = 1--key:{key}")
            values_k.extend(values)
            target_k_idx.append(key)
        elif common_k and ratio > 0.90 and common_k[0] <= 20:
            ration1 = common_k[1] / cluster_len
            if 0.2 <= ration1 <= 0.25 and common_k[1] > 1:
                values_k.extend(values)
                target_k_idx.append(key)
            if 0.45 <= ration1 <= 0.5 and common_k[1] > 1:
                values_k.extend(values)
                target_k_idx.append(key)
            if 0.85 <= ration1 and common_k[1] > 1:
                values_k.extend(values)
                target_k_idx.append(key)

    print(f"target_k_idx:{target_k_idx}")
    return target_k_idx, values_k

def NMI_vote_candidate(most_common_indices,len_idx):
    isnmi = True
    if not most_common_indices:
        return False
    rate = len(most_common_indices) / len(len_idx)
    if rate < 0.8:
        isnmi = False
    return isnmi

def compute_len_cluster(cluster_data):
    length = 0
    for i in range(len(cluster_data)):
        length += len(cluster_data[i])

    print(f"length:{length}")
    return length


def get_values_k(indices, cluster_data):
    values_k = []

    for cluster in cluster_data:
        for sample in cluster:
            for msg in sample:
                data = msg.content
                val = int(data[indices], 16)
                msg_len = msg.bytelen
                k = msg_len - val
                msg.distance = k
                values_k.append(k)

    unique_k = list(set(values_k))

    return unique_k


def find_target_byte(len_idx, len_k, cluster_data):
    byte_idx = []
    merged_k = group_all_tuples_by_key(len_k)
    length_cluster = compute_len_cluster(cluster_data)
    idx, values_k = find_k(merged_k, length_cluster)
    if idx:
        byte_idx.extend(idx)
    print(f"byte_idx:{byte_idx}")


    # 统计每个数字出现在多少个列表中（去重）
    num_to_lists = {}
    for i, sublist in enumerate(len_idx):
        for num in set(sublist):  # 用 set 去重，防止同一列表中重复计数
            num_to_lists.setdefault(num, []).append(i)

    print(f"每个数字出现在哪些列表索引: {num_to_lists}")

    # 按出现列表数量排序
    sorted_nums = sorted(num_to_lists.items(), key=lambda x: len(x[1]), reverse=True)

    most_common_item = sorted_nums[0][0] if sorted_nums else None
    most_common_indices = sorted_nums[0][1] if sorted_nums else None
    candidate_char = NMI_vote_candidate(most_common_indices, len_idx)

    print(f"values_k:{values_k}")
    unique_k = list(set(values_k))

    if candidate_char and most_common_item:
        index = most_common_item
        print(f"A_Specific_Byte_Index_NMI:index:{index}")
        value_k = get_values_k(index, cluster_data)
        print(f"values:{values_k}")
        return [index], value_k
    if byte_idx:
        print(f"A_Specific_Byte_Index_Linear:byte_idx:{byte_idx}")
        return byte_idx, unique_k
    else:
        return None, None
