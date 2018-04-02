---
layout: post
title: Blockchain－Merkle Patricia Tree详解
date: 2018-03-30
author: lyton
tags: Merkle Patricia Tree
---
### Merkle Patricia Tree简介
Merkle Patricia Tree是一种经过改良的数据结构，其融合了默克尔树和前缀树两种树的结构优点，在以太坊中用来组织管理账户数据、生成交易集合哈希的重要数据。
MPT树具有一下几个作用：
* 存储任意长度的Key－value键值对数据；
* 提供一种快速计算所维护数据集哈希标识的机制；
* 提供快速状态回滚的机制；
* 提供一种称为默克尔证明的证明方法，进行轻节点扩展，实现简单支付验证；

### 默克尔树
Merkle树是由计算机科学家Ralph Merkle在很多年前提出并由此命名，在比特币的网络中通过Merkle验证数据的正确性。在比特币的网络中，Merkle被用来归纳一个区块中的交易，同时生成整个交易集合的数字指纹。由于Merkle的存在，将比特币这种公链的产物，扩展为轻节点，使支付验证更加简单。
###### 原理
在比特币网络中，merkle从下向上构建。在如下的例子中，首先将L1-L4四个单元数据哈希化，然后将哈希值存储到相应的叶子节点中，这些节点是Hash0－0，Hash0-1，Hash1-0，Hash1-1，通过合并相邻的两个哈希值，形成新的字符串，重复此步骤到根节点。
![avatar](/assets/img/merklepatriciatree/merkletheory.png)
具体根节点的计算可参考以太坊Merkle博客，上图中的一颗有着四个叶子节点的树，计算代表整个树的哈希需要7次计算，如果采用将这四个节点拼接到一起，只需要计算一次hash。但是为什么使用Merkle？

###### 特点
* Merkle是一种树结构，可以是二叉树、多叉树，无论几叉树，都具有数结构的特点。
* Merkle树叶子节点的value是数据项的内容，或者是数据项的哈希值
* 非叶子节点的value是根据孩子的信息，通过hash算法计算得出

###### 优势
* 快速重哈希 <br>

当Merkle节点发生变化的时候，只需要在当前发生变化的节点上计算，把跟发生变化的节点相关的节点再计算一次，便能得到新的根节点哈希值。

###### 劣势
* 轻节点扩展<br>

采用Merkle，只需存储区块头数据，不需要存储整个交易列表，回值列表等数据。

### 前缀树
前缀树（又称为字典树），用于保存关联数组，其键（key）的内容通常为字符串。前缀树节点在树中的位置是由其键的内容所决定的，即前缀树的key值被编码在根节点到该节点的路径中。如图所示：图中有六个叶子节点，其key值分别为to,tea,ted,ten,inn,A
<div align=center>
![avatar](/assets/img/merklepatriciatree/dictionarytree.png)

###### 优势
相对于哈希表，使用前缀树来进行查询拥有共同前缀key的数据时十分高效，例如在字典中查找前缀为pre的单词，对于哈希表而言，需要遍历整个表，时间效率为O(n)；对于前缀树，只需要在树中找到pre的几点，且遍历这个根节点的子树即可。相对于前缀树，不存在哈西冲突问题。

###### 劣势
* 直接查找效率低下<br>

前缀树查找效率为O(m)，m为所查节电的key长度，而哈希表的查找效率为O(1)。且一次查找会有M次IO开销，相比于直接查找，无论速度还是对磁盘的压力都比较大。
* 可能会造成空间浪费

当存在一个节点，其key值的内容比较长，当树中没有与之对应的前缀分支时，为了存储该节点，需要创建许多非叶子节点来存储路径，造成存储空间浪费。

### MPT结构设计
通过上述部分，前缀树可以通过key－value维护，但是其具有明显的局限性。无论是查询操作，还是对应数据的增删改查，效率低下，浪费存储空间。所以在以太坊中，为MPT新增不同的类型的树节点，压缩书的高度，降低复杂度。

MPT树中可以将树节点分为以下四类：
* 空节点
* 分支节点
* 叶子节点
* 扩展节点

###### 分支节点
分支节点用来表示MPT树中多有拥有超过1个孩子节点以上的非叶子节点，其定义如下：
```go
type fullNode struct {
        Children [17]node // Actual trie node data to encode/decode (needs custom encoder)
        flags    nodeFlag
}

// nodeFlag contains caching-related metadata about a node.
type nodeFlag struct {
    hash  hashNode // cached hash of the node (may be nil)
    gen   uint16   // cache generation counter
    dirty bool     // whether the node has changes that must be written to the database
}
```
与前缀树相同，MPT同样是把Key－value数据项的key编码在树的路径中，但是key的每一个字节值的范围太大（［0-127］），因此在以太坊中，操作树之前，利用key编码的转换，将一个子节点高低四位内容分拆成两个字节存储。编码转换后，key‘的每一位的值范围都在［0，15］内。因此，一个分支节点的孩子至多只有16个。以太坊通过此方式，减少每个分支节点的容量，但实在一定程度上增加了树高。
分支节点的孩子列表中，最后一个元素是用来存储自身的内容。此外，每个分支节点会有一个附带的字段nodeFlag，记录一些辅助数据：
* 节点哈希：若该字段不为空，则当需要进行哈希计算时，可以跳过计算过程而直接使用上次计算的结果（当节点变脏时，该字段置空）
* 脏标志：当节点被修改时，该标志被置为1
* 诞生标志：当该节点第一次被载入内存中（或被修改时），会被赋予一个计数值作为诞生标志，该标志会被作为节点驱逐的依据，清除内存中“old”节点，节省内存资源。

###### 叶节点&&扩展节点
叶子节点和扩展节点的定义相似，如下所示：
```go
type shortNode struct {
        Key   []byte
        Val   node
        flags nodeFlag
}
* key：用来存储属于该节点范围的Key
* val：用来存储该节点的内容

其中key是MPT树实现树高压缩的关键，在本文开头部分，提到前缀树会影响内存的使用，严重浪费内存存储空间。

<div align="center">![avatar](/assets/img/merklepatriciatree/dictionarywaste.png)

在图中右侧存在一串字符串，这部分节点充当非叶子节点，用来构建路径，目的是存储该路径上的叶子节点。针对此情况，MPT树对此优化：当MPT树中试图插入一个节点，在插入的过程中发现目前没有与该节点Key拥有相同前缀的路径。此时MPT把剩余的Key存储在叶子／扩展节点的key字段中，充当一个Shortcut。

例如在图中，将红线圈出的节点称为node1，将紫线圈出的节点称为node2.node1和node2共享前缀t，在node1插入时，树中没有与oast有共同前缀的路径，因此node1的key为oast，实现编码路径的压缩。
<div align="center">![avatar](/assets/img/merklepatriciatree/searchfortoasting.jpeg)

其具备的优势如下：
* 提高节点的查找效率，避免过多的磁盘访问
* 减少存储空间浪费，避免存储无用的节点

val字段用来存储叶子／扩展节点的内容，对叶子节点而言，该字段存储的是一个数据项的内容；对扩展节点而言，存储以下两种内容：
* val字段存储是其孩子节点在数据库中存储的索引值（该索引值也是孩子节点的哈希值）；
* val字段存储是其孩子节点的引用

### 编码
由于使用场景不同，以太坊中采取三种编码形式，分别为，Raw编码（原生的字符）；Hex编码（扩展的16进制编码）；Hex－Prefix（16进制前缀编码）

###### Raw编码
Raw通过利用原生的key值，不进行改变。这种编码方式为key，是MPT树对外提供接口的默认编码方式。
> 例如一条key为“dog”，value为“cat”的数据项，其Raw编码为［‘d’，‘o’，‘g’］，换成ASCII表示为［63，61，74］

###### Hex编码
分支节点通过使用压缩字节，再编码，转换key的编码方式。
从Raw编码向Hex编码的转换规则为：
* 将raw编码的每个字符，根据不同的高低各四位进行拆分；
* 如果key对应的节点存储为数据项内容，在末位增加一个ASCII值为16的字符作为终止标志符
* 若该key对应的节点存储是另外一个节电的哈希索引（为扩展节点），不需要加任何字符

###### Hex－Prefix编码
在介绍叶子／扩展节点时，我们介绍了这两种即诶单定义是共享的，即便持久化到数据库中，存储方式一致。当节点加载到内存，同样需要一种额外的机制来区分节点的类型。以太坊通过提出HP编码方式来区分存储在数据库中的节点，将这两类节点持久化数据库钱，先会对该节点的key做编码转换，从Hex编码转化为HP编码。

HP编码规则如下：
* 若原key的末尾字节的值为16（即该节点是叶子节点），去掉该节点
* 在key之前增加一个半节点，其中最低位用来编码原本key长度的奇偶信息，key长度为奇数，则此位为1，低两位中编码一个特殊的终止标记符，若为叶子节点，此位为1
* 若原本key的长度为奇数，则在key前增加一个0x0的半字节
* 将原本的key内从作压缩，即将两个字符以高四位和低四位划分，存储在一个字节中（Hex扩展的逆过程）
> Hex编码为［3，15，3，13，4，10，16］，则HP编码为［32，63，61，74］

HP用于数据库中的编码，转换关系如下：
<div align="center">![avatar](/assets/img/merklepatriciatree/transferrelationship.jpeg)

以上三种编码方式转化关系：

* Raw编码：原生的key编码，是MPT对外提供接口中实用的编码方式，当数据项被插入到树中时，Raw编码被转化为Hex编码
* Hex编码：16进制扩展编码，用于对内存中树节点key编码，当树即诶单被持久化到数据库时，Hex编码被转换称HP编码；
* HP编码：16进制前缀编码，用于数据库中树节点key进行编码，当树节点被加载到内存时，HP被转化为Hex编码

### 安全的MPT
以上介绍了MPT树，可以用来存储任意长度内容的key－value数据项。倘若数据项的key长度没有限制时，当树中维护的数据量较大时，仍然会造成整棵树的深度加深，造成以下影响：

* 查找一个节点需要多次IO读取，降低效率
*系统遭受Dos攻击，攻击者可以通过合约中存储特定数据，构造一棵拥有一条呢很长路径的树，然后不断调用SLOAD指令读取内从，造成系统执行效率低
* 所有的key其实是一种明文的形式进行存储

为了解决以上问题，在以太坊中对MPT再次封装，对数据项的key进行一次哈希计算，因此最终作为参数传入到MPT接口的数据其实是（sha3（key），value）

###### 优势
传入MPT接口的key是固定长度（32字节），可以避免出现树中出现长度很长的路径

###### 劣势
每次计算需要增加一次哈希计算；需要在数据库中存储额外的sha（key）与key之间的对应关系

### 参考资料
* https://github.com/ethereum/wiki/wiki/Patricia-Tree
* http://gavwood.com/paper.pdf
* https://zh.wikipedia.org/wiki/Trie
* https://en.wikipedia.org/wiki/Merkle_tree
* https://github.com/ethereum/wiki/wiki/Design-Rationale
* https://github.com/ethereum/wiki/wiki/Light-client-protocol
