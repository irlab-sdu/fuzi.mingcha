singularity参考文档
[https://sylabs.io/guides/3.8/admin-guide/admin_quickstart.html](https://sylabs.io/guides/3.8/admin-guide/admin_quickstart.html)
[https://sylabs.io/guides/3.8/user-guide/introduction.html](https://sylabs.io/guides/3.8/user-guide/introduction.html)
# 1、singularity安装
账号：root
## 1.1 go安装
由于singularity是用GO写的，所以需要先安装GO（实验室服务器**使用方式二，安装在/data目录下**）

1. 方式一 ：使用yum安装go
```shell
sudo yum install -y golang
```

2. **方式二：压缩包安装**
```shell
wget https://go.dev/dl/go1.18.2.linux-amd64.tar.gz
tar -C /data -xzf go1.18.2.linux-amd64.tar.gz      #-C后的路径是将go安装的位置   
# 将go的路径添加到环境变量中(添加到~/.bashrc的最后一行)
export PATH=/data/go/bin:$PATH

source ~/.bashrc
go version
```
## 1.2 singularity 安装
**方式一：**（我们使用**方式一，安装在/data目录下**）

1. 下载相应的依赖和安装包
```shell
# yum clean all && yum makecache
sudo yum groupinstall -y 'Development Tools'
sudo yum install -y epel-release
# 注意如果已经根据上述步骤安装了golang，就不要再安装
sudo yum install -y golang libseccomp-devel squashfs-tools cryptsetup

# yum install -y rpm-build
export VERSION=3.8.0
wget https://github.com/hpcng/singularity/releases/download/v${VERSION}/singularity-${VERSION}.tar.gz

```

2. 编译singularity
```shell
#若需要解压到自定义的位置，则在tar后添加 -C your_path
sudo tar -C /home/aizoo-slurm/ -xzf singularity-${VERSION}.tar.gz  
cd /data/singularity-${VERSION}
```
默认情况下，Singularity将安装在/usr/local 目录层次结构中。--prefix使用该选项指定自定义目录 .
如果想安装多个版本的 Singularity、或者如果想在安装后轻松删除 Singularity，则--prefix非常有用。
```shell
sudo ./mconfig --prefix=/data/singularity-3.8.0 && \
    sudo make -C ./builddir && \
    sudo make -C ./builddir install
#等待一小会儿后，编译完毕
#将装好的singularity添加到PATH中(~/.bashrc)
export PATH=/data/singularity-3.8.0/bin:$PATH

source ~/.bashrc
singularity --version
```
方式二： 
不建议使用以下方式安装。
```shell
#这种方式会将Singularity安装在/usr/local目录层次结构中，比较分散，可能在后续的配置中出现问题
#删除的时候并不方便，
#使用rpm安装，安装时由于国内网络原因，无法连接GO服务器进行校对，会报超时错误，但是貌似没有影响。
rpmbuild -tb singularity-${VERSION}.tar.gz
rpm -ivh ~/rpmbuild/RPMS/x86_64/singularity-${VERSION}-1.el7.x86_64.rpm
rm -rf ~/rpmbuild singularity-${VERSION}*.tar.gz
singularity version
```

# 2、singularity运行
运行示例：
```shell
singularity exec -B /data_local:/mnt /image/base-conda2.sif python /data/test_code.py --batch_size=64

# -B 后面需要接入要用到的路径，以便于singularity mount，默认会mount当前路径
#    这里的/data_local:/mnt 是将本地的/data_local目录挂载到镜像中的/mnt目录（也就是在镜像中对/mnt目录的操作就是对本地/data_local的操作）
#    若要挂载多个目录，则可以使用,连接  /data_localA:/mntA,/data_localB:/mntB
#    
#    若我们不使用 : 进行映射，直接在-B后写目录 比如-B /dataA/dataB/dataC 那么在镜像内就会
#    生成(覆盖)一个dataA目录dataA下有个目录是dataB，dataB下有个dataC
#    --dataA
#       --dataB
#          --dataC
#            --xxx.json
#            --bbb.txt
#     使用/dataA/dataB/dataC/xxx.json 访问
#     注意，只能在dataC目录下进行 读/写 操作，若要写个文件到/dataA/dataB/aaa.txt 会出错

# /image/base-conda2.sif   ---> singularity的镜像文件位置 
# /data/test_code.py       ---> 需要执行的文件路径（执行文件中的log等输出 可以写到挂载的/data文件中）
# --batch_size=64          ---> 用户自定义的python运行参数
```