
# -*- coding: utf-8 -*-

import numpy as np

class DPSegment(object):
    def __init__(self, corpus):
        text_file_path = corpus
        self.prob_dict, self.word_set = self.get_prob_dict(text_file_path)
        
    '''
    get_prob_dict()函数得到带有概率的词典，返回一个dict类型的prob_dict和一个set类型的word_set，
    其中prob_dict的key为语料中出现过的词，value为其对应的概率；word_set中的元素为语料中出现过的词。
    prob_dict形式为：
    {'，': 0.06709451692308926,
     '的': 0.049341874289061734,
     '。': 0.0347409325905136,
     '、': 0.015311127650909499,
     '了': 0.011208499762268261,
     '在': 0.011003869911587867,
     '和': 0.009627633857011883,
     '是': 0.008911429379630503,
     '“': 0.006502013196619194,
     '”': 0.006443834121425749,
     '一': 0.006285346295898777,
     '有': 0.004233029264074822,
     '不': 0.003805713987653999,
     '他': 0.0037776275375606115,
     '这': 0.0035890470869335816,
     '中': 0.0035549421118201826,
     '对': 0.0034646642365200086,
     '为': 0.003404478986319893,
     '上': 0.0033523184361464588,
     '说': 0.003252009685812932,
     ...}
    '''
    def get_prob_dict(self, text_file): # 参数text_file为语料文件的路径
        # 初始化词频词典为空dict
        freq_dict = {}
        # 初始化词典为空set
        word_set = set()
        # 初始化语料中词的总数
        word_count = 0
        with open(text_file, encoding='utf8') as f:
            for line in f:            
                line = line.strip()
                if not line:
                    continue
                word_list = line.split()
                
                ##########  # 更新词的集合
                word_set.update(word_list)
    
                for w in word_list:
                    word_count += 1
                    ##########  # 更新词频（每个词的出现次数）
                    freq_dict[w] = freq_dict.get(w, 0) + 1
                    
        # 得到每个词的概率
        prob_dict = {k: v / word_count for k, v in freq_dict.items()}
        return prob_dict, word_set

    '''
    编写get_graph()函数得到连接图，连接图的节点定义课参考第六周课件。连接图graph可以用一个dict来表示，其key为一对节点序号所表示的边，
    value为该边(词)所对应概率的负对数。给定词典和待分词的句子，其连接图可以为如下形式：
    
    {(0, 1): 7.926323779729214,
     (0, 2): 7.861785258591642,
     (1, 2): 10.074758192896,
     (2, 3): 10.346691908379643,
     (2, 4): 11.327521161391369,
     (3, 4): 8.914588011228458,
     (4, 5): 8.944893360723787,
     (5, 6): 12.426133450059478,
     (6, 7): 9.787076120444219,
     (7, 8): 7.108013456215262,
     (8, 9): 12.426133450059478,
     (8, 10): 8.960397547259753,
     (8, 11): 11.327521161391369,
     (9, 10): 10.480223301004164,
     (10, 11): 10.174841651452983}
    
    '''
    def get_graph(self, text):
        graph={}
        
        # 得到graph的每对key的value，key为一对节点序号,表示一个词,value为每个词的概率的负对数。利用已有的self.prob_dict和self.word_set.
        ##########
        for i in range(len(text) - 1):
            for j in range(i + 1, len(text) + 1):
                word = text[i:j]
                if word in self.prob_dict:
                # 计算概率的负对数，这里可以根据具体情况调整
                    prob_neg_log = -np.log(self.prob_dict[word])
                    graph[(i, j)] = prob_neg_log

        
        return graph
                
    '''
    get_in_edge()函数得到每个节点的输入节点列表，返回的in_edge为list类型，in_edge可以为如下形式：
    [[], [0], [0, 1], [2], [2, 3], [4], [5], [6], [7], [8], [8, 9], [8, 10]]
    上式表示第0个节点的输入为空，第1个节点的输入为节点0，第2个节点的输入为节点0与节点1，...
    '''
    def get_in_edge(self, text):
        in_edge = []
        for i in range(len(text)+1):
            in_edge.append([k[0] for k in self.graph if k[1] == i])
        return in_edge
    
    
    
    '''
    编写viterbi()函数，以递归形式计算最短路径的值，并同时修改属性self.last_node，记录最优路径。
    '''
    def viterbi(self, target):
        if target == 0:
            return 0.
        else:
            # 初始化最短路径
            min_dis = np.inf
            for i in self.in_edge[target]:
                if min_dis > self.graph[(i,target)] + self.viterbi(i):
                    # 更新节点0到节点target的最短路径
                    ##########
                    min_dis = self.graph[(i, target)] + self.viterbi(i)
                    # 更新target节点的上一个节点
                    self.last_node[target] = i
            return min_dis
    
    
    def cut(self, text):
        L = len(text)
        # get_in_edge()函数得到输入text对应的连接图
        self.graph = self.get_graph(text)
        # get_in_edge()函数得到输入text的连接图中每个节点的输入节点列表
        self.in_edge = self.get_in_edge(text)
        # 初始化last_node，last_node每个元素为最优路径中该位置的传入节点
        self.last_node = [0] * (L + 1)
        # viterbi()函数返回最短路径，并同时修改self.last_node中元素的值，记录最优路径
        distance = self.viterbi(L)
        best_cut = []
        i = L
        while i > 0:
            # 根据self.last_node中记录的最短路径，得到分词结果。
            k = self.last_node[i]
            best_cut.append(text[k:i])
            i = k
        return best_cut[::-1] # 逆序输出


# 实例化DPSegment测试
cutter = DPSegment('./data/trainCorpus.txt_utf8')

# 查看词典
dictionary = cutter.prob_dict
sorted_by_freq = sorted(dictionary.items(), key=lambda item:item[1], reverse=True)[:20] # 取概率最大前20个查看
print(sorted_by_freq)

# 测试
result = cutter.cut('完成普通的分隔问题不大')
print(result)
result = cutter.cut('如果输入生僻词会怎么样')
print(result)