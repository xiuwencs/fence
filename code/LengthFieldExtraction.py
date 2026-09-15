from collections import Counter
from collections import defaultdict
import math


def n_gram_fixed_field_BE(data, n, target_index):
    length = []
    field = []
    print(f"{n}-gram-field")
    if target_index[0] + 1 - n >= 0:
        for line in data:
            msg = line.content
            msg_length = line.bytelen
            start = target_index[0] - n + 1
            end = target_index[0] + 1
            target_field = [''.join(msg[start:end])]
            length.append(msg_length)
            field.extend(target_field)
        k_num = []

        print(f"target_field:{field}")
        for i in range(len(length)):
            if n > 1:
                num = ''.join(field[i])
                val = int(num, 16)
            else:
                val = int(field[i], 16)
            k = length[i] - val
            k_num.append(k)

        # 计数
        unique_k = list(set(k_num))
        print(f"unique_k:{unique_k}")
        print()
        counter = Counter(k_num)
        print(f'len of k_num:{len(k_num)}')

        # 找出现最多的那一项
        most_common_item, count = counter.most_common(1)[0]
        print(f"most_common_item:{most_common_item}")
        print(f"count:{count}")
        print(f"len of length:{len(length)}")
        print(f"len of field:{len(field)}")
        ratio = count / len(length)
        if ratio > 0.95 and most_common_item >= 0:
            return True,count,len(length)
        else:
            return False,None, None
    else:
        return False,None,None


def find_common_element(data):
    counter = Counter(data)
    # 找出现最多的那一项
    most_common_item, count = counter.most_common(1)[0]
    return most_common_item, count


def n_gram_field_LE(data, n, target_index):
    length = []
    field = []
    print(f"{n}-gram-field")
    max_len = len(data[0].content)

    max_len = len(data[0].content)
    for line in data:
        msg_len = len(line.content)
        if msg_len < max_len:
            max_len = msg_len

    if target_index[0] + n - 1 <= max_len:
        for line in data:
            msg = line.content
            msg_length = line.bytelen
            start = target_index[0]
            end = target_index[0] + n
            target_field = msg[start:end]
            target_field = target_field[::-1]
            target_field = [''.join(target_field)]
            length.append(msg_length)
            field.extend(target_field)
        k_num = []

        print(f"target_field:{field}")
        for i in range(len(length)):
            if n > 1:
                num = ''.join(field[i])
                val = int(num, 16)
                # print(f"num:{num}")
            else:
                val = int(field[i], 16)
            k = length[i] - val
            k_num.append(k)

        # 计数
        unique_k = list(set(k_num))
        print(f"unique_k:{unique_k}")
        most_common_item, count = find_common_element(k_num)
        print(f"most_common_item:{most_common_item}")
        print(f"count:{count}")
        print(f"len of length:{len(length)}")
        print(f"len of field:{len(field)}")
        ratio = count / len(length)
        if ratio > 0.95 and most_common_item >= 0:
            return True, count, len(length)
        else:
            return False, None, None
    else:
        return False, None, None


def n_gram_unfixed_field_LE(data, n, target_index):
    length = []
    field = []
    print(f"{n}-gram-field")

    max_len = len(data[0].content)
    for line in data:
        msg_len = len(line.content)
        if msg_len < max_len:
            max_len = msg_len
    print(f"max_len:{max_len}")
    if target_index[0] + n <= max_len:
        for line in data:
            msg = line.content
            msg_length = line.bytelen
            start = target_index[0]
            end = target_index[0] + n
            target_field = msg[start:end]
            target_field = target_field[::-1]
            length.append(msg_length)
            field.append(target_field)

        print(f"field:{field}")
        k_num = []
        for i in range(len(length)):
            if n > 1:
                num1 = field[i][0]
                num2 = field[i][1]
                val = int(num1, 16) * 128 - 128 + int(num2, 16)
            else:
                val = int(field[i][0], 16)
            k = length[i] - val
            k_num.append(k)

        unique_k = list(set(k_num))
        print(f"unique_k:{unique_k}")
        most_common_item, count = find_common_element(k_num)
        print(f"most_common_item:{most_common_item}")
        print(f"count:{count}")
        print(f"len of length:{len(length)}")
        print(f"len of field:{len(field)}")
        ratio = count / len(length)
        if ratio > 0.95 and most_common_item >= 0:
            return True, count, len(length)
        else:
            return False,None, None
    else:
        return False, None, None


def n_gram_unfixed_field_BE(data, n, target_index):
    length = []
    field = []
    print(f"{n}-gram-field")

    if target_index[0] + 2 - n >= 0:
        for line in data:
            msg = line.content
            msg_length = line.bytelen
            start = target_index[0]
            end = target_index[0] + n
            target_field = msg[start:end]
            length.append(msg_length)
            field.append(target_field)

        #print(f"field:{field}")
        k_num = []
        for i in range(len(length)):
            if n > 1:
                num = ''.join(field[i])
                val = int(num, 16)
            else:
                val = int(field[i][0], 16)
            k = length[i] - val
            k_num.append(k)

        unique_k = list(set(k_num))
        print(f"unique_k:{unique_k}")
        most_common_item, count = find_common_element(k_num)
        print(f"most_common_item:{most_common_item}")
        print(f"count:{count}")
        print(f"len of length:{len(length)}")
        print(f"len of field:{len(field)}")
        ratio = count / len(length)
        if ratio > 0.85 and most_common_item <= 128:
            return True, count, len(length)
        else:
            return False, None, None
    else:
        return False, None, None


def fixed_little_endian_field(data, target_index):
    field_length = 0
    T_count = 0
    total = 0
    for i in range(4):
        isfeild,count,total_len = n_gram_field_LE(data, i + 1, target_index)
        if isfeild:
            field_length = i + 1
        if count and total_len:
            T_count = count
            total = total_len
    return field_length,T_count,total


def fixed_big_endian_field(data, target_index):
    field_length = 0
    T_count = 0
    total = 0
    for i in range(4):
        isfeild,count,total_len = n_gram_fixed_field_BE(data, i + 1, target_index)
        if isfeild:
            field_length = i + 1
        if count and total_len:
            T_count = count
            total = total_len
    return field_length,T_count,total


def unfixed_little_endian_field(data, len_rank, target_offset):
    field_length = []
    T_count = []
    total = []
    print(f"len_rank[-1]:{len_rank[-1]}")
    for samples in data.values():
        temp_length = 0
        temp_count = 0
        temp_total = 0
        for i in range(len_rank[-1]):
            isfeild,count,total_len = n_gram_unfixed_field_LE(samples, i + 1, target_offset)
            if isfeild:
                temp_length = i + 1
            if count and total_len:
                temp_count = count
                temp_total = total_len
        field_length.append(temp_length)
        T_count.append(temp_count)
        total.append(temp_total)
    print(f"field_length:{field_length}")
    return field_length,T_count,total


def unfixed_big_endian_field(data, len_rank, target_offset):
    field_length = []
    T_count = []
    total = []
    for samples in data.values():
        temp_length = 0
        temp_count = 0
        temp_total = 0
        for i in range(len_rank[-1]):
            isfeild,count,total_len = n_gram_unfixed_field_BE(samples, i + 1, target_offset)
            if isfeild:
                temp_length = i + 1
            if count and total_len:
                temp_count = count
                temp_total = total_len
        field_length.append(temp_length)
        T_count.append(temp_count)
        total.append(temp_total)
    print(f"field_length:{field_length}")
    return field_length,T_count,total


def cluster_by_values_k(cluster_data, values_k, target_offset):
    results = defaultdict(list)
    for samples in cluster_data:
        for data_len in samples:
            msg_length = data_len[0].bytelen
            first_msg = data_len[0].content
            val = int(first_msg[target_offset[0]], 16)
            k = msg_length - val
            results[k].extend(data_len)

    results = dict(results)

    return results


def cluster_to_whole_data(cluster_data):
    results = []
    for samples in cluster_data:
        for data_len in samples:
            for line in data_len:
                results.append(line)

    return results


def detemine_len_field(cluster_data, offset, len_rank, values_k, target_offset):
    print(f"target_offset:{target_offset},offset:{offset}")
    print(f"values_k:{values_k}")
    isLE = True
    if not target_offset:
        print(f"This protocol doesn't exist length field!!")
    else:
        if target_offset == [offset]:
            print(f"this procotol exist variable-length field ")
            results = cluster_by_values_k(cluster_data, values_k, target_offset)
            field_length,count,total = unfixed_big_endian_field(results, len_rank, target_offset)

            field_offset = target_offset[0]
            data_num = count[0] + count[1]
            total_num = total[0] + total [1]
            print(f"offset of length field:{field_offset},field length :{field_length}")
            print(f"data_num:{data_num},total_num:{total_num},ration:{data_num/total_num}")
            # unfixed_big_endian_field(results,target_offset,values_k)
        else:
            print(f"this procotol exist fixed-length field ")
            results = cluster_to_whole_data(cluster_data)
            field_length,data_num,total_num= fixed_big_endian_field(results, target_offset)
            if not field_length:
                field_length,data_num,total_num = fixed_little_endian_field(results, target_offset)
                isLE = True
            if field_length > 1:
                if isLE:
                    field_offset = target_offset[0]
                else:
                    field_offset = target_offset[0] + 1 - field_length
            else:
                field_offset = target_offset[0]
            if field_offset == 0:
                field_length = field_length - 1
                field_offset = target_offset[0] + 1 - field_length
            print(f"offset of length field:{field_offset},field length :{field_length}")
            print(f"data_num:{data_num},total_num:{total_num},ration:{data_num/total_num}")


def unfixed_len_BE(entropy,target_offset,column_data):
    len_idx = 0
    FN = 0
    missed_data = []
    for i in range(target_offset[0], len(entropy) + 1):
        if i + 1 <= len(entropy) - 1:
            tuple_entropy = entropy[i + 1]
            h = entropy[i][1]
            h1 = tuple_entropy[1]
            if h1 != 0.0:
                if (h - h1) >= 1.5:
                    print(f"(h - h1) >= 1.0----len_idx:{len_idx}")
                    len_idx = i + 1
                    break
            else:
                row = column_data[i + 1]
                most_common_item, count = find_common_element(row)
                print(f"most_common_item:{most_common_item}, count:{count}, total_num:{len(row)}")
                ratio = count / len(row)
                if most_common_item == '00' and ratio > 0.95:
                    for idx, item in enumerate(row):
                        if item != '00':
                            missed_data.append(idx)
                    FN = len(row) - count
                    len_idx = i + 1
                    print(f"H = 0.0----len_idx:{len_idx}")
                    break
        else:
            len_idx = i + 1
            break
    print(f"len_idx:{len_idx}")
    print(f"FN:{FN},missed_data:{missed_data}")
    return len_idx, FN, missed_data


def unfixed_len_LE(entropy,target_offset,column_data):
    len_idx = 0
    FP = 0
    missed_data = []
    for i in range(target_offset[0], len(entropy) + 1):
        if i + 1 <= len(entropy) - 1:
            tuple_entropy = entropy[i + 1]
            h = entropy[i][1]
            h1 = tuple_entropy[1]
            if h1 != 0.0:
                if(h1 - h) >= 1.5:
                    print(f"(h1 - h) >= 1.0----len_idx:{len_idx}")
                    len_idx = i + 1
                    break
            else:
                row = column_data[i + 1]
                most_common_item, count = find_common_element(row)
                print(f"most_common_item:{most_common_item}, count:{count}, total_num:{len(row)}")
                ratio = count / len(row)
                if most_common_item == '00' and ratio > 0.95:
                    for idx, item in enumerate(row):
                        if item != '00':
                            missed_data.append(idx)
                    FP = len(row) - count
                    len_idx = i + 1
                    print(f"H = 0.0----len_idx:{len_idx}")
                    break
        else:
            len_idx = i + 1
            break
    print(f"len_idx:{len_idx}")
    print(f"FP:{FP},missed_data:{missed_data}")
    return len_idx,FP,missed_data


def fixed_len_LE(entropy,target_offset,column_data):
    len_idx = 0
    FP = 0
    missed_data = []
    for i in range(target_offset[0],len(entropy) + 1):
        if i + 1 <= len(entropy) - 1:
            print(i)
            tuple_entropy = entropy[i]
            h = entropy[i-1][1]
            h1 = tuple_entropy[1]
            print(f"h1:{h1},h:{h}")
            if (h1 - h) >= 1.0:
                len_idx = i - 1
                print(f"(h - h1) >= 1.0----len_idx:{len_idx}")
                break
            else:
                if h1 < 0.06:
                    row = column_data[i]
                    most_common_item, count = find_common_element(row)
                    print(f"most_common_item:{most_common_item}, count:{count}, total_num:{len(row)}")
                    ratio = count / len(row)
                    if most_common_item == '00' and ratio > 0.95:
                        for idx, item in enumerate(row):
                            if item != '00':
                                missed_data.append(idx)
                        FP = len(row) - count
                        len_idx = i
                        print(f"H = 0.0----len_idx:{len_idx}")
                else:
                    len_idx = i - 1
                    break
        else:
            len_idx = i+1
            break
    print(f"len_idx:{len_idx}")
    print(f"FP:{FP},missed_data:{missed_data}")
    return len_idx,FP,missed_data


def fixed_len_BE(entropy,target_offset,column_data):
    len_idx = 0
    FN = 0
    missed_data = []
    fixed_type = None
    for i in range(target_offset[0],-1,-1):
        if i - 1 >= 0:
            print(i)
            tuple_entropy = entropy[i + 1]
            h = entropy[i][1]
            h1 = tuple_entropy[1]
            print(f"h1:{h1},h:{h}")
            if (h - h1) >= 1.0:
                len_idx = i
                print(f"(h - h1) >= 1.0-----len_idx:{len_idx}")
                fixed_type = 1
                break
            else:
                if h < 0.05:
                    row = column_data[i]
                    most_common_item, count = find_common_element(row)
                    print(f"most_common_item:{most_common_item}, count:{count}, total_num:{len(row)}")
                    ratio = count / len(row)
                    if most_common_item == '00' and ratio > 0.95:
                        for idx, item in enumerate(row):
                            if item != '00':
                                missed_data.append(idx)
                        FN = len(row) - count
                        len_idx = i
                        print(f"H = 0.0----len_idx:{len_idx}")
                    else:
                        len_idx = i + 1
                        break
        else:
            if len_idx == 0:
                len_idx = 1
            break
    print(f"len_idx:{len_idx}")
    print(f"FN:{FN},missed_data:{missed_data}")
    return len_idx,FN,missed_data,fixed_type


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


def evalution_unfixed_msg_BE(field_offset,field_length,missed_data,msg_data):
    values_k = []
    msg_count = 0
    TN = 0
    FP = 0
    for key, item in enumerate(msg_data):
        for idx,line in enumerate(item):
            for msg_len in line:
                msg_count += 1
                msg = msg_len.content
                if missed_data:
                    if idx not in missed_data:
                        field = msg[field_offset:field_offset + field_length[key]]
                        if field_length[key] == 1:
                            val = int(field[0], 16)
                            k = msg_len.bytelen - val
                            if k == 2:
                                TN += 1
                            else:
                                FP += 1
                                print(f"key:{key},field_length:{field_length[key]},msg:{msg}")
                        elif field_length[key] == 3:
                            if field[0] == '7e':
                                TN += 1
                            else:
                                FP += 1
                                print(f"key:{key},field_length:{field_length[key]},msg:{msg}")
                        else:
                            FP += 1
                            print(f"key:{key},field_length:{field_length[key]},msg:{msg}")
                else:
                    field = msg[field_offset:field_offset + field_length[key]]
                    if field_length[key] == 1:
                        val = int(field[0], 16)
                        k = msg_len.bytelen - val
                        if k == 2:
                            TN += 1
                    elif field_length[key] == 3:
                        if field[0] == '7e':
                            TN += 1
                        else:
                            FP += 1
                            print(f"key:{key},field_length:{field_length[key]},msg:{msg}")
                    else:
                        FP += 1
                        print(f"key:{key},field_length:{field_length[key]},msg:{msg}")
    return TN, FP


def evalution_unfixed_msg_LE(field_offset,field_length,missed_data,msg_data):
    values_k = []
    msg_count = 0
    TP = 0
    FP = 0
    for key, item in enumerate(msg_data):
        for idx,line in enumerate(item):
            for msg_len in line:
                msg_count += 1
                msg = msg_len.content
                if missed_data:
                    if idx not in missed_data:
                        field = msg[field_offset:field_offset + field_length[key]]
                        if field_length[key] == 1:
                            val = int(field[0], 16)
                            k = msg_len.bytelen - val
                            if k == 2:
                                TP += 1
                            else:
                                FP += 1
                                print(f"key:{key},field_length:{field_length[key]},msg:{msg}")
                        elif field_length[key] == 2:
                            num1 = field[1]
                            num2 = field[0]
                            val = int(num1, 16) * 128 - 128 + int(num2, 16)
                            k = msg_len.bytelen - val
                            if k == 3:
                                TP += 1
                            else:
                                FP += 1
                                print(f"key:{key},field_length:{field_length[key]},msg:{msg}")
                        else:
                            FP += 1
                            print(f"key:{key},field_length:{field_length[key]},msg:{msg}")
                else:
                    field = msg[field_offset:field_offset + field_length[key]]
                    if field_length[key] == 1:
                        val = int(field[0], 16)
                        k = msg_len.bytelen - val
                        if k == 2:
                            TP += 1
                        else:
                            FP += 1
                            print(f"key:{key},field_length:{field_length[key]},msg:{msg}")
                    elif field_length[key] == 2:
                        num1 = field[1]
                        num2 = field[0]
                        val = int(num1, 16) * 128 - 128 + int(num2, 16)
                        k = msg_len.bytelen - val
                        if k == 3:
                            TP += 1
                        else:
                            FP += 1
                            print(f"key:{key},field_length:{field_length[key]},msg:{msg}")
                    else:
                        FP += 1
                        print(f"key:{key},field_length:{field_length[key]},msg:{msg}")
    return TP, FP


def unfixed_field_boundy(data,target_offset):
    msg_data = []
    messages_length = []
    isLE = False
    FN = []
    FNs = 0
    missed_data = []
    processed_data = []
    isfirst = True

    for item in data:
        temp_list = []
        temp_len = 0
        for msg in item:
            for msg_len in msg:
                temp_list.append(msg_len.content)
            temp_len += len(msg)
        messages_length.append(temp_len)
        msg_data.append(temp_list)
    min_length = min(messages_length)
    print(f"min_length:{min_length},messages_length:{messages_length}")

    field_length = []
    for item in msg_data:
        if len(item) == min_length and not isfirst and min_length < 200:
            FNs += min_length
            isfirst = True
            continue
        column_data = list(zip(*item))
        entropy_results = []

        for idx, column in enumerate(column_data):
            entropy = calculate_entropy(column)
            entropy_results.append((idx, entropy))
        print(f"entropy_results:{entropy_results}")
        len_idx,fn,misse_idx = unfixed_len_LE(entropy_results, target_offset,column_data)
        #len_idx,fn,misse_idx = unfixed_len_BE(entropy_results, target_offset, column_data)
        field_length.append(len_idx - target_offset[0])
        FN.append(fn)
        missed_data.append(misse_idx)
    field_offset = target_offset[0]
    print(f"missed:{missed_data}")

    missed = []
    if missed_data:
        for item in missed_data:
            missed += item
    print(missed)

    for item in data:
        temp_len = 0
        for msg in item:
            temp_len += len(msg)
        if temp_len == min_length and isfirst:
            isfirst = False
            continue
        processed_data.append(item)
    if isLE:
        TN, FP = evalution_unfixed_msg_LE(field_offset, field_length, missed, processed_data)
    else:
        TN, FP = evalution_unfixed_msg_BE(field_offset, field_length, missed, processed_data)

    print(f"TN:{TN},FP:{FP},FN:{FP+FNs}")
    return field_offset,field_length


def evalution_msg_BE(field_offset,field_length,missed_data,msg_data):
    values_k = []
    for idx, line in enumerate(msg_data):
        msg = line
        if missed_data:
            if idx not in missed_data:
                field = ''.join(msg[field_offset:field_offset + field_length])
                val = int(field,16)
                k = line.bytelen - val
                values_k.append(k)
        else:
            field = ''.join(msg[field_offset:field_offset + field_length])
            val = int(field, 16)
            k = line.bytelen - val
            if k != 5:
                print(msg)
            values_k.append(k)

    unique_values = list(set(values_k))
    most_common_item,count=find_common_element(values_k)
    print(f"most_common_item:{most_common_item},count:{count}")
    print(f"unique_values:{unique_values}")
    TN = count
    FP = len(msg_data) - len(missed_data) - count
    return TN,FP


def evalution_msg_LE(field_offset,field_length,missed_data,msg_data):
    values_k = []
    for idx, line in enumerate(msg_data):
        msg = line.content
        if missed_data:
            if idx not in missed_data:
                field = msg[field_offset:field_offset + field_length]
                reversed_field = ''.join(field[::-1])
                val = int(reversed_field,16)
                k = line.bytelen - val
                values_k.append(k)
        else:
            field = ''.join(msg[field_offset:field_offset + field_length])
            val = int(field, 16)
            k = line.bytelen - val
            values_k.append(k)

    most_common_item,count=find_common_element(values_k)
    print(f"most_common_item:{most_common_item},count:{count}")
    TN = count
    FP = len(msg_data) - len(missed_data) - count
    return TN,FP


def fixed_field_boundy(data,target_offset,overtow):
    FN = 0
    processed_offset = 0
    msg_data = []
    isLE = False
    fixed_type = None
    isfirst = False
    field_offset = []
    messages_length = []

    if overtow:
        if isLE:
            processed_offset = [target_offset[0] + 1]
        else:
            processed_offset = [target_offset[0] - 1]
    else:
        processed_offset = [target_offset[0] - 1]

    for item in data:
        temp_list = []
        temp_len = 0
        for msg in item:
            for msg_len in msg:
                temp_list.append(msg_len.content)
            temp_len += len(msg)
        messages_length.append(temp_len)
        msg_data.append(temp_list)
    min_length = min(messages_length)
    print(f"min_length:{min_length},messages_length:{messages_length}")
    field_length = []
    for item in msg_data:
        if len(item) == min_length and not isfirst and min_length < 200:
            FN += min_length
            isfirst = True
            continue
        column_data = list(zip(*item))
        entropy_results = []

        for idx, column in enumerate(column_data):
            entropy = calculate_entropy(column)
            entropy_results.append((idx, entropy))
        print(f"entropy_results:{entropy_results}")
        len_idx,temp_FN,missed_data,fixed_type = fixed_len_BE(entropy_results, processed_offset, column_data)
        #len_idx,temp_FN,missed_data = fixed_len_LE(entropy_results, processed_offset, column_data)
        FN += temp_FN
        if isLE:
            length = len_idx - target_offset[0] + 1
            field_length.append(length)
            field_offset.append(target_offset[0])
        else:
            if fixed_type == 1:
                length = target_offset[0] - len_idx
                field_length.append(length)
                field_offset.append(len_idx + 1)
            else:
                length = target_offset[0] - len_idx + 1
                field_length.append(length)
                field_offset.append(len_idx)

    print(f"FN:{FN}")
    return field_offset, field_length


def determine_field(cluster_data, offset, values_k, target_offset):
    if target_offset:
        target_offset = [item for item in target_offset if target_offset and item != 0]
    print(f"target_offset:{target_offset},offset:{offset}")
    print(f"values_k:{values_k}")
    isovertow = False
    if values_k:
        for item in values_k:
            if item > 256:
                isovertow = True
    if not target_offset:
        print(f"This protocol doesn't exist length field!!")
    else:
        if target_offset == [offset]:
            print(f"this procotol exist variable-length lebgth field ")
            field_offset, field_length = unfixed_field_boundy(cluster_data,target_offset)
            print(f"offset of length field:{field_offset},field length :{field_length}")
        else:
            print(f"this procotol exist fixed-length length field ")
            field_offset, field_length = fixed_field_boundy(cluster_data,target_offset,isovertow)
            print(f"offset of length field:{field_offset},field length :{field_length}")