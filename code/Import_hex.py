from scapy.all import *
import csv
import os
from pathlib import Path

def Non_deal(df):
    list_data = []
    rows = len(df)
    for i in range(0, rows):
        list = df[i]
        list_con = []
        cols = len(list)
        for j in range(0, cols):
            if list[j] != "nan":
                list_con.append(list[j])  # 如果用remove法需要倒序去除，否则无法去除干净（因为每一次去除会导致len-1)
        list_data.append(list_con)
    return list_data

def export_pcapng_to_hex(pcapng_file, output_file):
    packets = rdpcap(pcapng_file)  # 读取pcapng文件
    with open(output_file, 'w') as file:
        for packet in packets:
            hexdump = ','.join([f"{byte:02x}" for byte in bytes(packet)])  # 将数据包转换为十六进制表示，并用逗号分隔每个字节
            # hexdump = ''.join([f"{byte:02x}" for byte in bytes(packet)])  # 将数据包转换为十六进制表示，并用逗号分隔每个字节
            file.write(hexdump + '\n')  # 将十六进制表示写入文件，每行一个协议

    print("导出完成！")


def import_file(pcapng_file, output_file, protocol_name):
    filename = protocol_name + "_file"

    export_pcapng_to_hex(pcapng_file, output_file)
    # 数据导入
    header = ['{}'.format(i) for i in range(0, 1460)]
    # 创建csv文件并写入表头
    with open(output_file, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        data = [row for row in reader]
    data.insert(0, header)
    # 写入新的csv文件
    with open('new.txt', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

    with open('new.txt', 'r')as file:
        reader = csv.reader(file)
        next(reader)
        data = list(reader)
    data = Non_deal(data)
    data_str = []

    if pcapng_file == 'coap_file' or pcapng_file == 'snmp_file':
        data = [row[44:] for row in data]
    elif pcapng_file == 'qq.pcapng' or filename == 'stun_file':
        data = [row[42:] for row in data]
    elif pcapng_file == 'dns_file':
        data = [row[28:] for row in data]
    elif pcapng_file == 'dnp3_file':
        data = [row[66:] for row in data]
    elif pcapng_file == 'nbns_file':
        print("1")
        data = [row[58:] for row in data]
    elif pcapng_file == 'mqtt_file':
        data = [row[68:] for row in data]
        print("1")
    else:
        data = [row[54:] for row in data]
        print(f"data:{data[:10]}")
        print("0")


    if not data_str:
        for line in data:
            combined_str = ''.join(line)
            data_str.append([combined_str])

    return data_str
