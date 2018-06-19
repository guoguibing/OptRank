# OptRank

需求环境：
Linux，python3.6

1.paper原文

2.如何获取训练数据集？
  demo-word.sh中会自动下载text8数据集，约100MB
  还可以通过以下两种方式获得不同大小的wiki语料库数据集
  wiki_256M
  wiki_512M

3.如何训练词向量？
  参看demo-word.sh
  time ./OptRank3 -train text8 -output OptRank3_vectors -cbow 1 -size 300 -window 8 -negative 15 -hs 0 -sample 1e-4 -threads 20 -min-count 5 -binary 1 -iter 10

  -train        选择要使用的训练语料库，这里使用的是text8
  -output       训练好的词向量保存时的文件名
  -cbow         是否使用cbow模型，1为使用，0为使用skip-gram
  -size         词向量的维度
  -window       上下文的窗口大小
  -negative     选取的负样本个数
  -hs           1为使用hs模型，0为使用负样本采样模型
  -threads      训练时使用的线程数
  -min-count    将出现频数小于一定数值的单词剔除掉
  -binary       训练好的词向量是否保存为二进制
  -iter         模型的迭代次数

  为了复现我们的实验结果，这里建议在使用text8，wiki_256M，wiki_512M 等中小训练语料库时将参数设置为
  -cbow 1 -size 300 -window 8 -negative 15 -hs 0 -sample 1e-4 -threads 20 -min-count 5 -binary 1 -iter 10

4.如何对生成的词向量进行评测？
  由于不同词嵌入算法保存的词向量的形式不同，有些为二进制形式，有些则不是。我们提供了两种版本的评测程序，compute-accuracy和evaluate.py对应非二进制存储的词向量，加了后缀“_binary”的对应二进制形式存储的词向量

  compute-accuracy使用的是questions-words.txt测试数据集，对应paper中word analogy部分的实验
  以评测二进制存储的OptRank3_vectors为例
  使用如下命令：  ./compute-accuracy_binary OptRank3_vectors < questions-words.txt

  evaluate.py使用的是data/eval中的测试数据集，对应paper中word similarity部分的实验
  同样以评测二进制存储的OptRank3_vectors为例
  使用如下命令：   python evaluate_binary.py OptRank3_vectors 

  提示：在比较不同词嵌入算法的效果或不同参数设置下同一模型的训练效果时请使用同种存储形式的词向量，不同存储形式的词向量之间存在一定误差。

