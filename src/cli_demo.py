import argparse
import json
import os

import requests
from transformers import AutoTokenizer, AutoModel

parser = argparse.ArgumentParser()
parser.add_argument("--url_lucene_task1", required=True, help="法条检索对应部署的 pylucene 的地址")
parser.add_argument("--url_lucene_task2", required=True, help="类案检索对应部署的 pylucene 的地址")
args = parser.parse_args()

print("正在加载模型")

tokenizer = AutoTokenizer.from_pretrained("SDUIRLab/fuzi.mingcha-v1.0", trust_remote_code=True)
model = AutoModel.from_pretrained("SDUIRLab/fuzi.mingcha-v1.0",
                                  trust_remote_code=True).half().cuda()
model = model.eval()

print("模型加载完毕")


def print_hello():
    print(
        "欢迎使用 夫子·明察 司法大模型，首先请选择任务：\n键入 1 进入基于法条检索回复任务；\n键入 2 进入基于案例检索回复任务；\n键入 3 进入三段论推理判决任务；\n键入 4 进入司法对话任务；\n键入 "
        "stop 终止程序；\n进入任务后键入 home 退出当前任务")


def print_hello_task(mod):
    task_description = [
        "欢迎使用 基于法条检索回复 任务，此任务中模型首先根据用户输入案情，模型生成相关法条；根据生成的相关法条检索真实法条；最后结合真实法条回答用户问题。\n您可以尝试输入以下内容：小李想开办一家个人独资企业，他需要准备哪些信息去进行登记注册？",
        "欢迎使用 基于案例检索回复 任务，此任务中模型首先根据用户输入案情，模型生成相关案例；根据生成的相关案例检索真实案例；最后结合真实案例回答用户问题。\n您可以尝试输入以下内容：被告人夏某在2007年至2010年期间，使用招商银行和广发银行的信用卡在北京纸老虎文化交流有限公司等地透支消费和取现。尽管经过银行多次催收，夏某仍欠下两家银行共计人民币26379.85元的本金。2011年3月15日，夏某因此被抓获，并在到案后坦白了自己的行为。目前，涉案的欠款已被还清。请问根据上述事实，该如何判罚夏某？",
        "欢迎使用 三段论推理判决 任务，此任务中模型利用三段论的推理方式生成判决结果。\n您可以尝试输入以下内容：被告人陈某伙同王某（已判刑）在邵东县界岭乡峰山村艾窑小学法经营“地下六合彩”，由陈某负责联系上家，王某1负责接单卖码及接受投注，并约定将收受投注10％的提成按三七分成，陈某占三，王某1占七。该地下六合彩利用香港“六合彩”开奖结果作为中奖号码，买1到49中间的一个或几个数字，赔率为1：42。在香港六合彩开奖的当天晚上点三十分前，停止卖号，将当期购买的清单报给姓赵的上家。开奖后从网上下载香港六合彩的中奖号码进行结算赔付，计算当天的中奖数额，将当期卖出的总收入的百分之十留给自己，用总收入的百分之九十减去中奖的钱，剩余的为付给上家的钱。期间，二人共同经营“地下六合彩”40余期，收受吕某、吕永玉、王某2、王某3等人的投注额约25万余元，两人共计非法获利4万余元。被告人陈某于2013年11月18日被抓获，后被取保候审，在取保期间，被告人陈某脱逃。2015年1月21公安机关对其网上追逃。2017年6月21日被告人陈某某自动到公安机关投案。上述事实，被告人陈某在开庭审理过程中亦无异议，并有证人王某1、吕某、吕永玉、王某3等人的证言，扣押决定书，扣押物品清单，文件清单，抓获经过，刑事判决书，户籍证明等证据证实，足以认定。",
        "欢迎使用 司法对话 任务，此任务中您可以与模型进行直接对话。"]
    print(task_description[mod - 1])


def process_lucence_input(input):
    nr = ['(', ')', '[', ']', '{', '}', '/', '?', '!', '^', '*', '-', '+']
    for char in nr:
        input = input.replace(char, f"\\{char}")
    return input


def chat(prompt, history=None):
    if history is None:
        history = []
    response, history = model.chat(tokenizer, prompt, history=history if history else [], max_length=4096, max_time=100,
                                   top_p=0.7, temperature=0.95)
    return response, history


prompt1_task1 = "请根据以下问题生成相关法律法规: @用户输入@"
prompt2_task1 = """请根据下面相关法条回答问题
相关法条：
@检索得到的相关法条@
问题：
@用户输入@"""
prompt1_task2 = "请根据以下问题生成相关案例: "
prompt2_task2 = """请根据下面相关案例回答问题
相关案例：
@检索得到的相关案例@
问题：
@用户输入@"""
prompt_task3 = """请根据基本案情，利用三段论的推理方式得到判决结果，判决结果包括：1.罪名；2.刑期。
基本案情：@用户输入@"""


def main():
    history = []
    mod = 0
    print_hello()
    while True:
        query = input("\n用户：")
        if not query.strip():
            print("输入不能为空哦")
            continue
        if query.strip() == "stop":
            break
        if query.strip() == "home":
            mod = 0
            history = []
            print_hello()
            continue

        if mod == 0:  # 欢迎页
            if query in ["1", "2", "3", "4"]:
                mod = int(query)
                print_hello_task(mod)
                if mod == 4:
                    history = [["你好",
                                "您好，我是夫子·明察，一个由山东大学信息检索实验室制作的司法语言模型。我主要用于回答用户法律相关的问题，提供法律知识和建议。"]]
            else:
                print("输入无效")
                continue
        elif mod == 1:  # 基于法条检索回复
            # print(f"\n\n用户：{query}")
            generate_law, _ = chat(prompt1_task1.replace("@用户输入@", query))
            data = {"query": process_lucence_input(generate_law), "top_k": 3}
            response_retrieval = requests.post(args.url_lucene_task1, json=data)
            response_retrieval = json.loads(response_retrieval.content)
            docs = response_retrieval['docs']
            retrieval_law = ""
            for i, doc in enumerate(docs):
                retrieval_law = retrieval_law + f"第{i + 1}条：\n{doc}\n"
            response, _ = chat(
                prompt2_task1.replace("@检索得到的相关法条@", retrieval_law).replace("@用户输入@", query))
            print(f"\n\n夫子·明察·法条检索：\n{response}")
        elif mod == 2:  # 基于案例检索回复
            # print(f"\n\n用户：{query}")
            generate_law, _ = chat(prompt1_task2.replace("@用户输入@", query))
            data = {"query": process_lucence_input(generate_law), "top_k": 1}
            response_retrieval = requests.post(args.url_lucene_task2, json=data)
            response_retrieval = json.loads(response_retrieval.content)
            docs = response_retrieval['docs']
            retrieval_law = ""
            max_len = 1000  # 为避免对模型的输入过长，限制检索案例的长度，只保留最后 1000 个 tokens
            for i, doc in enumerate(docs):
                retrieval_law = retrieval_law + f"第{i + 1}条：\n{doc[-max_len / len(docs):]}\n"
            response, _ = chat(
                prompt2_task2.replace("@检索得到的相关案例@", retrieval_law).replace("@用户输入@", query))
            print(f"\n\n夫子·明察·类案检索：\n{response}")
        elif mod == 3:  # 三段论推理判决
            # print(f"\n\n用户：{query}")
            response, _ = chat(prompt_task3.replace("@用户输入@", query))
            print(f"\n\n夫子·明察·三段论：\n{response}")
        else:  # 司法对话
            # print(f"\n\n用户：{query}")
            response, history = chat(query, history)
            print(f"\n\n夫子·明察：\n{response}")


if __name__ == "__main__":
    main()
