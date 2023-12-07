# -*- coding: utf-8 -*-
# --------------接收参数--------------------
import argparse
import csv
import lucene
import os
import random

import datetime
import json
import uvicorn
from fastapi import FastAPI, Request
from java.nio.file import Paths
from org.apache.lucene.analysis.cn.smart import SmartChineseAnalyzer
from org.apache.lucene.document import Document, Field, StringField, TextField
from org.apache.lucene.index import IndexWriterConfig, IndexWriter, DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher, SortField
from org.apache.lucene.store import FSDirectory

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

# 设置CSV文件夹路径和Lucene索引文件夹路径
csv_folder_path = "./csv_files/"
INDEX_DIR = "./lucene_index/"

# 设定检索top k 条目数
top_k = 3


# 定义Lucene索引写入器，将CSV文件内容加入Lucene索引中
def create_index():
    if os.path.exists(INDEX_DIR) and len(os.listdir(INDEX_DIR)) > 0:
        print("已有索引")
        return
    analyzer = SmartChineseAnalyzer()
    config = IndexWriterConfig(analyzer)

    index_dir = FSDirectory.open(Paths.get(INDEX_DIR))
    writer = IndexWriter(index_dir, config)
    for filename in os.listdir(csv_folder_path):
        if filename.endswith(".csv"):
            path = os.path.join(csv_folder_path, filename)
            with open(path, "r", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)
                for row in reader:
                    if len(row) > 0:
                        content = ""
                        for i in range(len(headers)):
                            content += row[i]
                        doc = Document()
                        doc.add(Field("filename", filename, StringField.TYPE_STORED))
                        doc.add(Field("content", content, TextField.TYPE_STORED))
                        writer.addDocument(doc)
    writer.close()


# 定义Lucene检索器，用输入语句查询Lucene索引
def search_index(query_str):
    index_dir = FSDirectory.open(Paths.get(INDEX_DIR))
    reader = DirectoryReader.open(index_dir)

    # 定义检索器和排序器
    searcher = IndexSearcher(reader)
    sortField = SortField("score", SortField.Type.SCORE, True)

    # 设定QueryParser
    query_parser = QueryParser("content", SmartChineseAnalyzer())
    # query_parser.setDefaultOperator(QueryParserBase.Operator.AND)
    query = query_parser.parse(query_str)

    # 使用TopFieldCollector进行结果的排序和筛选
    # top_docs = TopFieldCollector.create(sortField, top_k, len(reader.maxDoc()))
    # top_docs = TopFieldCollector.create(sortField, top_k)
    # searcher.search(query, top_docs)
    # score_docs = top_docs.topDocs().scoreDocs
    score_docs = searcher.search(query, 50).scoreDocs

    result = []

    for scoredoc in score_docs:
        doc = searcher.doc(scoredoc.doc)
        filename = doc.get("filename")
        content = doc.get("content")
        result.append((scoredoc.score, filename, content))

    # result = list(set(result))
    return result


@app.post("/")
async def create_item(request: Request):
    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    query_str = json_post_list.get("query")
    top_k = json_post_list.get("top_k")
    results = search_index(query_str)  # 检索
    docs = []
    for result in results:
        # print("score:", result[0], "filename:", result[1], "content:", result[2], '\n')
        docs.append(result[2])
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    answer = {"docs": docs[0 : min(top_k, len(docs))], "status": 200, "time": time}
    return answer


if __name__ == "__main__":
    lucene.initVM(vmargs=["-Djava.awt.headless=true"])
    # 在每次测试运行前先创建Lucene索引
    create_index()

    print("web服务启动")
    if args.port:
        uvicorn.run(app, host="0.0.0.0", port=args.port)
    else:
        uvicorn.run(app, host="0.0.0.0", port=get_port())
