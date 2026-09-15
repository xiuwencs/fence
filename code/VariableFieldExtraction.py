# -*- coding: utf-8 -*-
from scipy.ndimage import gaussian_filter
from collections import defaultdict
import math
from collections import Counter
import numpy as np
import seaborn as sns
from sklearn.metrics import mutual_info_score
import matplotlib
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

matplotlib.use('TkAgg')  # 或 'QtAgg'，取决于你的环境支持哪种



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
    return sort_list


def calculate_entropy(column):
    # 统计每个值的出现次数
    value_counts = Counter(column)
    total = len(column)
    entropy = 0.0

    for count in value_counts.values():
        # 计算概率
        probability = count / total
        # 累加熵值
        entropy -= probability * math.log2(probability)

    return entropy


def calculate_column_entropy(data):
    # 转置数据，按列处理
    columns = list(zip(*data))
    entropy_results = []

    for idx, column in enumerate(columns):
        entropy = calculate_entropy(column)
        entropy_results.append((idx, entropy))

    return entropy_results


def compute_adjacent_mi_pairs(mi_matrix):
    # 找出互信息最低的字节对（排除对角线）
    n_bytes = len(mi_matrix[0])
    adjacent_mi_pairs = []
    for i in range(n_bytes - 1):  # 避免越界
        j = i + 1
        adjacent_mi_pairs.append(((i, j), mi_matrix[i, j]))

    return adjacent_mi_pairs


def compute_min_mi(adjacent_mi_pairs):
    real_candidate_points = []
    mi_values = [item[1] for item in adjacent_mi_pairs]
    processed_mi_pair = [float(value) for value in mi_values]
    for idx, mi in enumerate(processed_mi_pair):
        if mi < 2.0:
            real_candidate_points.append(idx)
    return real_candidate_points


def find_variable_field_offset(messages):
    """
    在消息组中寻找变长字段偏移，支持递归分类
    threshold：一致性阈值，超过此值，进行分类
    min_group_size：最小分组数据量，避免过度拆分
    """
    threshold = 100
    min_group_size = 2
    # 转换为字节列表
    byte_messages = [list(map(lambda x: int(x, 16), msg)) for msg in messages]

    # 计算最大一致性及偏移
    best_offset, max_consistency = find_best_offset(byte_messages)

    # 根据最大一致性进行判断
    if max_consistency >= threshold and len(messages) >= min_group_size and best_offset > 3:
        # 根据偏移位置拆分消息
        groups = split_messages(byte_messages)
        classified_groups = []
        # 对每个组递归检测
        for group in groups:
            if len(group) >= min_group_size:
                # 转换回消息原始形式（十六进制字符串）
                group_msgs = list_to_hexstr(group)
                # 递归分析
                sub_offset, sub_consistency = find_best_offset(group)
                classified_groups.append({
                    'offset': sub_offset,
                    'consistency': sub_consistency,
                    'messages': group_msgs
                })
        return classified_groups
    else:
        # 不再分类，返回当前偏移和一致性
        return [{
            'offset': best_offset,
            'max_consistency': max_consistency,
            'messages': [list_to_hexstr(msg) for msg in byte_messages]
        }]


def find_best_offset(byte_messages):
    max_consistency = 0
    best_offset = 0
    for offset in range(len(byte_messages[0])):
        candidates = [msg[offset:] for msg in byte_messages]
        consistency = calculate_sequence_consistency(candidates)
        if consistency > max_consistency:
            max_consistency = consistency
            best_offset = offset
    return best_offset, max_consistency


def calculate_sequence_consistency(sequences):
    """
    计算序列的一致性
    """
    if not sequences:
        return 0

    # 找出最短序列长度
    min_length = min(len(seq) for seq in sequences)

    # 统计每个位置上的一致性
    total_consistency = 0
    for pos in range(min_length):
        # 提取该位置的所有值
        values = [seq[pos] for seq in sequences]

        # 计算唯一值的数量
        unique_values = len(set(values))

        # 一致性越高，唯一值越少
        total_consistency += (len(sequences) - unique_values)

    return total_consistency / min_length


def split_messages(data):

    # 自动确定聚类数
    max_clusters = 8
    best_score = -1
    best_clusters = 2
    for k in range(2, max_clusters + 1):
        kmeans = KMeans(n_clusters=k, random_state=0).fit(data)
        labels = kmeans.labels_
        score = silhouette_score(data, labels)
        if score > best_score:
            best_score = score
            best_clusters = k
    print('最佳聚类数：{}'.format(best_clusters))

    kmeans = KMeans(n_clusters=best_clusters, random_state=0).fit(data)
    labels = kmeans.labels_
    result = [[] for _ in range(max(labels) + 1)]
    for i, sublist in enumerate(data):
        result[labels[i]].append(sublist)

    return result


def list_to_hexstr(lst):
    # 如果元素是列表，先扁平化
    hex_msgs = []
    if lst and isinstance(lst[0], list):
        for item in lst:
            msg = [f"{byte:02x}" for byte in item]
            hex_msgs.append(msg)
    return hex_msgs


def label_points(entropy_candidate_points,min_mi_pair,data):

    candidate_points = entropy_candidate_points
    unique_points = list(set(candidate_points))
    msg_labels = []
    for i in range(len(data)):
        temp_data = []
        print(f"len sort:{len(data)}")
        data_i = data[i]
        content = data_i[0].content
        # 根据长度限制
        msg_length = min(len(content), 16)
        print(f"msg_length:{msg_length}")

        for line in data[i]:
            msg_len = min(len(line.content), 16)
            temp_data.append(line.content[:msg_len])

        classified_groups = find_variable_field_offset(temp_data)

        entropy_result = calculate_column_entropy(temp_data)

        print(f"entropy_result:{entropy_result}")
        for m in range(len(classified_groups)):
            msgs = classified_groups[m]['messages']
            print(f"len of group:{len(msgs)}")
            static_index = classified_groups[m]['offset'] - 1
            msg_label = []
            for j in range(msg_length):
                msg_label.append('XX')
                if j == static_index and static_index > 4 and msg_length > 12:
                    msg_label.append('E-')
                if j in unique_points:
                    msg_label.append('C-')
                if j in min_mi_pair and j != 0:
                    msg_label.append('M-')
            if msg_length <= 12:
                msg_label.append('E-')
            msg_label.append('{}'.format(len(msgs)))
            msg_labels.append(msg_label)

    return msg_labels


def compute_mutual_info_matrix(cluster_data):
    """
    计算每两个字节位置之间的互信息值
    :param data: numpy.ndarray, shape=(n_samples, n_bytes)
    :return: numpy.ndarray, shape=(n_bytes, n_bytes)
    """
    max_len = max(len(row) for row in cluster_data)
    padded_data = []
    for row in cluster_data:
        # 将十六进制字符串转换成整数，如果不够长就填充 0x00
        padded_row = [int(byte, 16) for byte in row] + [0] * (max_len - len(row))
        padded_data.append(padded_row)
    data = np.array(padded_data, dtype=np.uint8)
    n_samples, n_bytes = data.shape
    mi_matrix = np.zeros((n_bytes, n_bytes))

    for i in range(n_bytes):
        for j in range(n_bytes):
            mi_matrix[i, j] = mutual_info_score(data[:, i], data[:, j])

    return mi_matrix


def plot_mi(adjacent_mi_pairs):
    # 提取MI值
    mi_values = [item[1] for item in adjacent_mi_pairs]
    indices = np.arange(len(mi_values))

    # 转换为numpy数组
    mi_array = np.array(mi_values)

    # 进行高斯滤波
    sigma = 0.6  # 可根据需要调整
    smoothed_mi = gaussian_filter(mi_array, sigma=sigma)

    # 计算增量（差分）
    delta_mi = np.diff(smoothed_mi)
    signs = np.sign(delta_mi)
    sign_changes = (signs[:-1] > 0) & (signs[1:] < 0)
    candidate_points = np.where(sign_changes)[0] + 1  # +1对应原始索引

    candidate_points_list = list(candidate_points)
    mi_candidate_points = [int(x) - 1 for x in candidate_points_list]
    right_candidate_points = [int(x) + 1 for x in candidate_points_list]
    mi_candidate_points.extend(right_candidate_points)


    return mi_candidate_points


def plot_entropy(entropy_results):
    # 提取索引和值
    real_entropy_candidate_points = []

    indices = [item[0] for item in entropy_results]
    values = [item[1] for item in entropy_results]

    # 转换为NumPy数组
    data = np.array(values)

    # 1. 高斯平滑
    smooth_data = gaussian_filter(data, sigma=0.4)

    # 2. 计算增量（一阶差分）
    delta = np.diff(smooth_data)

    # 计算差分的绝对值
    abs_delta = np.abs(delta)
    abs_delta_indices = np.where(abs_delta > 0.5)[0] + 1
    print(f"abs_delta:{abs_delta}")


    # 4. 识别拐点（符号变化）
    # 寻找符号变化（正到负或负到正）
    signs = np.sign(delta)
    # 极大值点：符号由正变负
    maxima_points = np.where((signs[:-1] > 0) & (signs[1:] <= 0))[0] + 1
    # 极小值点：符号由负变正
    minima_points = np.where((signs[:-1] < 0) & (signs[1:] >= 0))[0] + 1
    candidate_points = maxima_points

    # 转换为list
    candidate_points_list = list(candidate_points)
    entropy_candidate_points = [int(x) for x in candidate_points_list]
    abs_delta_points = [int(x) for x in abs_delta_indices]
    processed_abs_delta_points = []
    for i in range(1,len(abs_delta_points),2):
        print(abs_delta_points[i-1],abs_delta_points[i])
        if abs_delta_points[i] - abs_delta_points[i-1] == 1:
            processed_abs_delta_points.append(abs_delta_points[i])
        else:
            processed_abs_delta_points.append(abs_delta_points[i - 1])
            processed_abs_delta_points.append(abs_delta_points[i])

    entropy_candidate_points = list(set(entropy_candidate_points))
    print(f"entropy_candidate_points:{entropy_candidate_points}")

    real_entropy_candidate_points.extend(entropy_candidate_points)

    return real_entropy_candidate_points,processed_abs_delta_points


def remove_duplicate(rows):
    unique_rows = []
    duplicate_count = defaultdict(int)
    for row in rows:
        data = row[:-1]
        row_tuple = tuple(data)
        if row_tuple not in unique_rows:
            unique_rows.append(row_tuple)
        duplicate_count[row_tuple] += int(row[-1])
    unique_rows = [list(row) for row in unique_rows]

    for row in unique_rows:
        row.append(str(duplicate_count[tuple(row)]))
    return unique_rows

def transf_data(msg_label):
    processed_data = []
    for line in msg_label:
        temp = [''.join(line[:-1])]
        processed_data.extend(temp)

    return processed_data

def find_most_common_elements(lst):
    count = Counter(lst)
    most_common = count.most_common()
    max_count = most_common[0][1]
    result = [x[0] for x in most_common if x[1] == max_count]
    return int(result[0])


def find_first_char(lst,element):
    element_index = []
    for i in range(len(lst)):
        if lst[i] == element:
            element_index.append(i)
    return element_index


def find_later_element(lst,elemnet,index):
    isfirst = False
    for i in range(index,len(lst)):
        if lst[i] == elemnet and not isfirst:
            return i

def find_first_differ_index(lst,longest_row):
    isfirst = False
    for i in range(0,len(longest_row)):
        for j in range(0, len(lst)):
            if longest_row[i] != lst[j][i] and not isfirst:
                return i


def re_align(lst,unique_front,longest_row):
    if unique_front:
        insert_pos = unique_front[0]
    else:
        insert_pos = find_first_differ_index(lst,longest_row)
    print(f"longest_row:{longest_row}")
    for i in range(0, len(lst)):
        count = 0
        for j in range(0, len(lst[i])):
            if lst[i][j] == 'C-' and lst[i][j] != longest_row[j]:
                print(f"line:{lst[i]}")
                print(f"i:{i},j:{j}")
                index = find_later_element(longest_row,'C-',j)
                if index:
                    gap = index - j
                    print(f"gap:{gap}")
                    if count != gap:
                        lst[i].insert(insert_pos,'--')
                        count += 1
                    else:
                        break
                else:
                    break
    return lst


def post_process(lst,longest_row):
    front = []
    rear = []
    for i in range(0, len(lst)):
        for j in range(0, len(lst[i])):
            if lst[i][j] == '--':
                for k in range(j - 1, 0, -1):
                    if lst[i][k] == 'C-':
                        front.append(k)
                        break
                for m in range(j + 1, len(lst[i])):
                    if lst[i][m] == 'C-':
                        rear.append(m)
                        break
    print('front:{}'.format(front))
    print('rear:{}'.format(rear))
    unique_front = list(set(front))
    if len(unique_front) == 1:
        insert_pos = unique_front[0]
        for i in range(0, len(lst)):
            if len(lst[i]) > insert_pos:
                if lst[i][insert_pos] == 'XX':
                    lst[i].insert(insert_pos, '--')

    re_align(lst,unique_front,longest_row)

    return lst


def find_first_greater(list, num):
    for x in list:
        if x > num:
            return x


def find_last_occurrence(lst, element):
    if element in lst:
        return len(lst) - lst[::-1].index(element) - 1


def find_all_C(lst,element_index):
    if lst[element_index] == 'C-':
        return False
    else:
        return True

def lst_post_process(lst):
    lst_new = []
    result = []
    if lst:
        min_len = min([len(line) for line in lst])
        for i in range(min_len):
            c_char = True
            for line in lst:
                if line[i] not in ['C-','--']:
                    c_char = False
            if c_char:
                result.append(i)

    if result and result[0] <= 8:
        for line in lst:
            temp_result = []
            for i in range(len(line)):
                if i != result[0]:
                    temp_result.append(line[i])
            lst_new.append(temp_result)
    if not result:
        lst_new = lst
    return lst_new,result

def pro_process(lst):
    result = []
    for line in lst:
        merged_line = []
        count = 0
        i = 0
        # 遍历line
        while i < len(line):
            # 检查当前元素与下一个元素
            if i + 1 < len(line) and line[i:i+2] == ['XX', 'C-']:
                count += 1
                i += 2
            else:
                # 如果连续的次数大于等于3，合并
                if count >= 3:
                    merged_line.extend(['XX'] * count)
                    merged_line.append('C-')
                else:
                    # 复制之前的连续元素
                    for _ in range(count):
                        merged_line.extend(['XX', 'C-'])
                count = 0
                # 添加当前元素
                merged_line.append(line[i])
                i += 1
        # 处理最后剩余的连续
        if count >= 3:
            merged_line.extend(['XX'] * count)
            merged_line.append('C-')
        else:
            for _ in range(count):
                merged_line.extend(['XX', 'C-'])
        result.append(merged_line)

    return result


def lst_pro_process(lst):
    lst_new = []
    result = []
    min_len = min([len(line) for line in lst])
    for i in range(min_len):
        c_char = True
        for j in range(len(lst)):
            if lst[j][i] not in ['M-']:
                print(f"i:{i},{lst[j][i]},{j}")
                c_char = False
                break
        if c_char:
            result.append(i)
    print(f"result:{result}")
    if len(result) == 2:
        for line in lst:
            temp_result = []
            for i in range(len(line)):
                if i < result[1] and line[i] in ['XX']:
                    temp_result.append(line[i])
                if i >= result[1]:
                    temp_result.append(line[i])
            lst_new.append(temp_result)
    if not result:
        lst_new = lst
    return lst_new


def alignment(lst):


    for i in range(len(lst)):
        lst[i] = [elem for elem in lst[i] if elem not in '*-']
    max_length = max([len(line) for line in lst])
    longest_rows = [line for line in lst if len(line) == max_length]
    if len(longest_rows) > 1:
        longest_row = longest_rows[1]
    else:
        longest_row = longest_rows[0]
    print(f"longest_row:{longest_row}")
    lst.remove(longest_row)
    dir = []
    for k in range(0, len(longest_row)):
        if longest_row[k] == 'C-':
            dir.append(k)

    for i in range(len(lst)):
        t = 0
        for j in range(len(lst[i])):
            if t != 0:
                j = j + t
            if j == len(longest_row):
                break
            if lst[i][j] == 'C-' and lst[i][j] != longest_row[j]:
                if 'C-' in lst[i][:j]:
                    l = find_last_occurrence(lst[i][:j], 'C-')
                    l_last = find_last_occurrence(longest_row[:j], 'C-')
                    if l == l_last:
                        inser = j - 1
                    else:
                        inser = l_last
                else:
                    if 'C-' in longest_row[:j]:
                        last_element = find_last_occurrence(longest_row[:j],'C-')
                        inser = last_element
                    else:
                        inser = j
                num = find_first_greater(dir, j)
                # print(f"num:{num}")
                if num is not None:
                    t = num - j
                    for k in range(t):
                        lst[i].insert(inser, '--')

    for line in lst:
        print(f"alignment:{line}")

    lst,result = lst_post_process(lst)
    longest_row_new = []
    if result and result[0] <= 8:
        for i in range(len(longest_row)):
            if i != result[0]:
                longest_row_new.append(longest_row[i])
    if not result:
        longest_row_new = longest_row
    lst.append(longest_row_new)
    return lst


def find_end_index(lst,results):
    global max_line
    if not lst or not all(lst):  # Check for empty list or empty strings
        return -1

    min_length = min(len(line) - 2 for line in lst)
    max_length = max(len(line) for line in lst)
    # 获取最大长度的行
    max_lines = [line for line in lst if len(line) == max_length]
    # 可能有多个最大长度行，选择第一个即可
    max_line = max_lines[0]
    min_element = min(results)
    min_length = min(min_length,min_element)
    for j in range(min_length, max_length):
        end_element = ['XX','--']
        # 先确认 j 在所有行的范围内
        if all(len(line) - 2 > j for line in lst):
            if all(line[j] in end_element for line in lst):
                return j
        else:
            # 如果某些行长度不足，此时考虑只判断已存在的行
            if all(line[j] in end_element for line in lst if len(line) - 2 > j):
                return j

    return None


def find_first_all_X(lst,min_element):
    msg_num = len(lst)

    for j in range(min_element-1,0,-1):
        count = 0
        for i in range(len(lst)):
            if j < len(lst[i]):
                if lst[i][j] == 'XX':
                    count += 1
            else:
                break
        if count == msg_num:
            return j


def find_second_insert(lst):
    second_insert =  None
    for i in range(len(lst)):
        if lst[i] == 'E-':
            second_insert = i

    return second_insert


def find_end_C(lst):
    second_insert = None
    for i in range(len(lst)):
        if lst[i] == 'C-':
            second_insert = i

    return second_insert


def remove_horizontal_line(lst):
    for i in range(len(lst)):
        lst[i] = [elem for elem in lst[i] if elem not in ('--', 'C-', 'D-', 'E-')]

    for i in range(len(lst)):
        if lst[i][-1] == '/':
            last_element = lst[i][-2]
            lst[i][-1] = last_element
            lst[i][-2] = '/'

    return lst


def find_min_slash_index(slash_idx):
    unique_slash = list(set(slash_idx))
    min_slash = unique_slash[0]
    for item in unique_slash:
        if item < min_slash:
            min_slash = item
    return min_slash


def compute_length(slash_idx,min_slash):
    length = []
    unique_slash = list(set(slash_idx))
    for item in unique_slash:
        k = item - min_slash - 1
        if k > 0:
            length.append(k)

    return length


def refine_mark(lst,first_inser, values_k):
    global slash_start
    count_X = []
    start = []
    isfixed = False
    for i in range(len(lst)):
        slash_index = []
        for j in range(len(lst[i])):
            if lst[i][j] == '/':
                slash_index.append(j)
        slash_start = slash_index[0]
        slash_end = slash_index[1]
        x = slash_end -slash_start
        count_X.append(x)
        start.append(slash_start)

    unique_count_X = list(set(count_X))
    unique_start_slash = list(set(start))
    max_len = max(unique_count_X)
    print(f"unique_count_X:{unique_count_X},unique_start_slash:{unique_start_slash}")
    if len(unique_count_X) == 1 or len(unique_start_slash) != 1 or all([item > 5 for item in unique_count_X]) or any([item > 10 for item in unique_count_X])\
            or (values_k and first_inser == 1 and (all([item < 126 for item in values_k]) or len(values_k) == 6)):
        isfixed = True
        for i in range(len(lst)):
            lst[i] = [elem for elem in lst[i] if elem not in '/']

    return lst,isfixed


def mark_and_remove(lst,values_k):
    first_inser = 0
    results = []
    for i in range(len(lst)):
        for j in range(len(lst[i])):
            if lst[i][j] in ['--']:
                results.append(j)
    if not results:
        print('This protocol does not have variable-length fields!')
        return None
    min_element = min(results)
    first_identical = find_first_all_X(lst,min_element)
    X_index = find_end_index(lst,results)
    print(f"first_identical:{first_identical},X_index:{X_index}")

    diff = X_index - first_identical

    for i in range(len(lst)):
        second_inser = find_second_insert(lst[i])
        C_index = find_end_C(lst[i])
        first_inser = first_identical

        # 如果二者都没有找到，设置插入位置
        if second_inser is None and C_index is None:
            second_inser = first_inser + 1

        # 如果没有second_inser但有C_index
        if second_inser is None and C_index is not None and diff > 1:
            second_inser = C_index

        if second_inser is None and C_index is not None and diff == 1:
            second_inser = first_inser + 1

        # 根据first_inser调整end_inser
        if first_inser != 1:
            end_inser = second_inser
        else:
            end_inser = X_index + 1# 确认X_index已定义
            if lst[i][end_inser - 2] == '--':
                end_inser = X_index - 1

            if lst[i][end_inser - 2] == 'XX' and lst[i][end_inser] != 'C-':
                end_inser = X_index - 1


        # 插入字符'/'到指定位置
        if end_inser is not None and first_inser is not None:
            lst[i].insert(end_inser, '/')
            lst[i].insert(first_inser, '/')

    lst = remove_horizontal_line(lst)
    print(f"first_inser:{first_inser}")
    lst,isfixed = refine_mark(lst, first_inser, values_k)

    for item in lst:
        print(f"item:{item}")

    if isfixed:
        print('This protocol does not have variable-length fields!')
        return None
    else:
        slash_idx = []
        for i in range(len(lst)):
            for j in range(len(lst[i])):
                if lst[i][j] == '/':
                    slash_idx.append(j)

        min_slash = find_min_slash_index(slash_idx)
        offset = min_slash
        length = compute_length(slash_idx,min_slash)
        print(f"offset:{offset},length:{length}")

        return offset


def label_vote_data(unique_data_label,vote_entropy,vote_mi):
    #print(f"vote_entropy:{vote_entropy},vote_mi:{vote_mi}")
    for i in range(len(unique_data_label)):
        count = 0
        j = 0
        while j < len(unique_data_label[i]):
            token = unique_data_label[i][j]
            if token == 'XX':
                count += 1
            else:
                # 判断标签和投票条件
                should_delete = False
                X_count = count - 1
                if token == 'C-' and X_count not in vote_entropy:
                    should_delete = True
                elif token == 'M-' and X_count not in vote_mi:
                    should_delete = True
                if should_delete:
                    unique_data_label[i].pop(j)
                    # 删除后，不增加j，重新检测当前位置
                    continue
            j += 1

    return unique_data_label


def change_element(vote_data_label):
    # 将非 'XX' 和 'C-' 的元素都改为 'C-'
    for i in range(len(vote_data_label)):
        for j in range(len(vote_data_label[i]) - 1):
            if vote_data_label[i][j] not in ['XX', 'C-', 'E-']:
                vote_data_label[i][j] = 'C-'

    # 合并连续的 'C-'，只保留一个
    for i in range(len(vote_data_label)):
        j = 0
        while j < len(vote_data_label[i]):
            if vote_data_label[i][j] == 'C-':
                # 检查后续是否也是 'C-'
                k = j + 1
                while k < len(vote_data_label[i]) and vote_data_label[i][k] == 'C-':
                    # 删除重复的 'C-'，保持第一个
                    vote_data_label[i].pop(k)
                j += 1
            else:
                j += 1
    return vote_data_label


def filter_labels(unique_data_labels):
    min_length = min(len(lst) for lst in unique_data_labels)
    min_length = min(min_length,9)
    count = 0
    for j in range(min_length - 2):
        # 获取当前位置元素
        current_elements = [line[j] for line in unique_data_labels]
        # 判断是否所有元素都相同
        if len(set(current_elements)) > 1:
            # 如果不全相同，删除不符合条件的子列表
            # 倒序遍历以安全删除
            for i in range(len(unique_data_labels) - 1, -1, -1):
                if unique_data_labels[i][j] != current_elements[0]:
                    count += 1
                    print(f"Filtered line:{unique_data_labels[i]}")
                    unique_data_labels.pop(i)
        if count == 1:
            break

    return unique_data_labels


def refinement_alignment(lst,cluster_data):
    results = []
    for i in range(len(lst)):
        for j in range(len(lst[i])):
            if lst[i][j] == '--':
                results.append(j)

    min_index = min(results)
    original_offset = find_first_all_X(lst,min_index)
    variable_field_offset = 0
    for i in range(original_offset):
        if lst[0][i] == 'XX':
            variable_field_offset += 1
    print(f"variable_field_offset:{variable_field_offset}")

    processed_cluster_data = []
    for data in cluster_data:
        sorted_data = len_sort(data)
        processed_cluster_data.append(sorted_data)


def entopy_anlysis(cluster_data,values_k):
    remain_num = 0
    data_label = []
    total_entropy = []
    total_delta = []
    total_mi = []
    sorted_data = []
    for data in cluster_data:
        sorted = len_sort(data)
        sorted_data.append(sorted)

    for data in sorted_data:
        print(f"len:{len(data)}")
        temp_data = []
        for item in data:
            count = 0
            for line in item:
                if len(line.content) > 16:
                    msg = line.content[:16]
                else:
                    msg = line.content
                if count < 16:
                    count += 1
                temp_data.append(msg)
        if len(temp_data) > 20:
            entropy_rersults = calculate_column_entropy(temp_data)

            print(f"entropy_results:{entropy_rersults}")
            mutual_information = compute_mutual_info_matrix(temp_data)
            adjacent_mi_pairs = compute_adjacent_mi_pairs(mutual_information)
            print(f"adjacent_mi_pairs:{adjacent_mi_pairs}")
            entropy_candidate_points,abs_delta_points = plot_entropy(entropy_rersults)
            mi_candidate_points = plot_mi(adjacent_mi_pairs)

            total_entropy.append(entropy_candidate_points)
            total_delta.append(abs_delta_points)
            total_mi.append(mi_candidate_points)


            min_adjacent_mi = compute_min_mi(adjacent_mi_pairs)
            print(f"min_adjacent_mi:{min_adjacent_mi}")
            msg_labels = label_points(entropy_candidate_points,mi_candidate_points,data)

            data_label.extend(msg_labels)
        else:
            remain_num += len(temp_data)

    for item in data_label:
        print(f"item:{item}")
    data_label = lst_pro_process(data_label)
    unique_data_label = remove_duplicate(data_label)

    change_data_label = change_element(unique_data_label)
    unique_data_labels = remove_duplicate(change_data_label)
    for item in unique_data_labels:
        print(f"item:{item}")

    alig_seq = alignment(unique_data_labels)
    print(f"remain_num:{remain_num}")

    variable_field_offset = mark_and_remove(alig_seq,values_k)
    return variable_field_offset
