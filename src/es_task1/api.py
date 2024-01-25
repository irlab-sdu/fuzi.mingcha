# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
import uvicorn, json, datetime
import sys, os
import csv
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from tqdm import trange

# --------------接收参数--------------------
import argparse
import random

parser = argparse.ArgumentParser(description="服务调用方法：python XXX.py --port=xx")
parser.add_argument("--port", default=None, type=int, help="服务端口")
args = parser.parse_args()


def get_port():
    pscmd = "netstat -ntl |grep -v Active| grep -v Proto|awk '{print $4}'|awk -F: '{print $NF}'"
    procs = os.popen(pscmd).read()
    procarr = procs.split("\n")
    tt = random.randint(15000, 20000)
    if tt not in procarr:
        return tt
    else:
        return get_port()


# ----------------------------------

app = FastAPI()

# Elasticsearch 地址
es_host = ""
# 用户名和密码
username = ""
password = ""
# 创建带有认证信息的 Elasticsearch 客户端
es = Elasticsearch([es_host], http_auth=(username, password), request_timeout=60)
file_name = "src/pylucene_task1/csv_files/data_task1.csv"
index_name = "fuzi_fatiao"
# 删除索引
# response = es.indices.delete(index=index_name, ignore=[400, 404])
# 打印结果
# print(f"Index '{index_name}' deletion response:", response)
# exit()
data = []
with open(file_name, "r", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    headers = next(reader)
    id = 0
    for row in reader:
        if len(row) > 0:
            content = ""
            for i in range(len(headers)):
                content += row[i]
        data.append(content)


def save_to_es(data_from, data_to):
    """
    使用生成器批量写入数据到es数据库
    :param num:
    :return:
    """
    action = (
        {
            "_index": index_name,
            "_type": "_doc",
            "_id": i,
            "_source": {"content": data[i]},
        }
        for i in range(data_from, data_to)
    )
    helpers.bulk(es, action)


def build_index():
    CREATE_BODY = {
        "settings": {"number_of_replicas": 0},  # 副本的个数
        "mappings": {
            "properties": {"content": {"type": "text", "analyzer": "ik_smart"}}
        },
    }
    es.indices.create(index=index_name, body=CREATE_BODY)

    data_size_one_time = 1000
    for begin_index in trange(0, len(data), data_size_one_time):
        save_to_es(begin_index, min(len(data), begin_index + data_size_one_time))

    es.indices.refresh(index=index_name)


# 定义Lucene检索器，用输入语句查询Lucene索引
def search_index(query_str):
    query_body = {
        "query": {
            "match": {
                "content": query_str
            }
        },
        "size": 10
    }
    res = es.search(index=index_name, body=query_body, request_timeout=60)
    return res

@app.post("/")
async def create_item(request: Request):
    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    query_str = json_post_list.get("query")
    top_k = json_post_list.get("top_k")
    results = search_index(query_str)  # 检索
    docs = []
    for hit in results["hits"]["hits"]:
        docs.append(hit["_source"]["content"])
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    answer = {"docs": docs[0 : min(top_k, len(docs))], "status": 200, "time": time}
    return answer


if __name__ == "__main__":
    # build_index()
    print("web服务启动")
    if args.port:
        uvicorn.run(app, host="0.0.0.0", port=args.port)
    else:
        uvicorn.run(app, host="0.0.0.0", port=get_port())