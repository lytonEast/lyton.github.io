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


###### 特点
###### 优势

###### 劣势
