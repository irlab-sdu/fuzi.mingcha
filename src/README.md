## 依赖库安装

1. 本项目的检索部分提供了两种检索方式（您可以选择其中实现）

a. 使用 [PyLucene](https://lucene.apache.org/pylucene/index.html) 实现，其安装步骤请参考[官方说明](https://lucene.apache.org/pylucene/install.html)。
Pylucene 安装过程较为繁琐，我们提供了 Pylucene 的 [Singularity](https://getsingularity.com/) 环境镜像，您可以参考 [Singularity 安装文档](./Singularity安装与使用.md) 安装 Singularity 并[下载镜像](https://pan.baidu.com/s/1PqUnX7YRNMt9co3RKUwExw)（提取码：jhhl）。然后运行以下代码即可完成部署
```shell
cd "/src/pylucene_task1" && singularity exec -B "/src/pylucene_task1":/mnt "/xxx/pylucene_singularity.sif" python /mnt/api.py --port "port"
```
请将`"/src/pylucene_task1"`换成自己实际的目录，`"/xxx/pylucene_singularity.sif"`是下载得到镜像。

b. 我们还提供了 [Elasticsearch](https://www.elastic.co/cn/elasticsearch) 的检索部署代码，需要提前安装好 ES

2. 夫子•明察的部署与 [ChatGLM](https://github.com/THUDM/ChatGLM-6B/tree/main#%E4%BD%BF%E7%94%A8%E6%96%B9%E5%BC%8F) 相同，在命令行下执行 ` pip install -r requirements.txt` 即可

## 检索模块部署

我们提供了两种检索系统部署方式 **pylucene** 和 **Elasticsearch**
1. **pylucene** 的部署方式。 
    
    如果您安装好 pylucene 的环境，您可以直接运行以下代码进行部署。或者您可以用上面“依赖库安装”中的部署方式。

    ```python
    python ./pylucene_task1/api.py --port "端口"
    python ./pylucene_task2/api.py --port "端口"
    ```

2. **ES** 部署方式

    ```python
    python ./es_task1/api.py --port "端口"
    python ./es_task2/api.py --port "端口"
    ```

注：

如果想更换检索数据集，可以参考我们的检索数据库格式自行进行修改： `./pylucene_task/csv_files/data_task.csv`。
您也可以简单的修改 `./pylucene_task/csv_files/api.py` 中的代码支持更多的数据类型。
- [task1 的数据库](./pylucene_task1/csv_files/) (法律法规数据集) 来自于 [LawRefBook](https://github.com/RanKKI/LawRefBook)

- [task2 的数据库](./pylucene_task2/csv_files/) (案例判决数据集) 主要来自于 CAIL，[LeCaRD](https://github.com/myx666/LeCaRD) 以及我们的预训练数据。由于数据库规模较大，我们选取了 1k 条案例作为示例。

## 命令行 Demo

![img](../images/cli_demo_case1.png)
![img](../images/cli_demo_case2.png)

运行仓库中 [cli_demo.py](cli_demo.py)：

```python
python cli_demo.py --url_lucene_task1 "法条检索对应部署的 pylucene 地址"  --url_lucene_task2 "类案检索对应部署的 pylucene 地址"
```
