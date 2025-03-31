# Copyright (c) 2022-2025 Ant Group
from .base import BasePreProcessor
from typing import List, Dict
import time


def get_mbxp_cn_prompt(item: dict, lang: str) -> str:
    """
    组装 mbxp的中文 prompt
    """
    # 从item中获取测试用例，并确保其为列表形式
    tests = item.get("test")
    lang = item["task_id"].split("/")[0].lower()
    lang = "typescript" if lang == "ts" else lang
    if not isinstance(tests, list):
        tests = [tests] if tests is not None else []

    if lang.lower() == "ts" or lang.lower() == "typescript":
        prompt = '''\
你是一个 TypeScript 程序员专家, 下面是你的任务: 编写一个函数，这个函数从给定的两个元祖列表中查找相似的元素. 你的代码需要通以下测试:
assert similar_elements((3, 4, 5, 6),(5, 7, 4, 10)) == (4, 5)
assert similar_elements((1, 2, 3, 4),(5, 4, 3, 7)) == (3, 4) 
assert similar_elements((11, 12, 14, 13),(17, 15, 14, 13)) == (13, 14) 
[开始]
"function similarElements(testTup1: any[], testTup2: any[]): any[] {{
    const set1 = new Set(testTup1);
    const set2 = new Set(testTup2);
    const result = Array.from(set1).filter(element => set2.has(element));
    return result;
}}"
[结束] 

你是一个 TypeScript 程序员专家, 下面是你的任务: 编写一个 TypeScript 函数来识别非素数. 你的代码需要通以下测试:
assert is_not_prime(2) == False 
assert is_not_prime(10) == True 
assert is_not_prime(35) == True 
[开始]
'function isNotPrime(n: number): boolean {{
    let result = false;
    for (let i = 2; i <= Math.sqrt(n); i++) {{
        if (n % i === 0) {{
            result = true;
        }}
    }}
    return result;
}}'
[结束] 

你是一个 TypeScript 程序员专家, 下面是你的任务: 编写一个函数，使用堆队列算法从给定的数字列表中查找最大的整数. 你的代码需要通以下测试:
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],3)==[85, 75, 65] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],2)==[85, 75] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],5)==[85, 75, 65, 58, 35] 
[开始]
'function heapQueueLargest(nums: number[], n: number): number[] {{
    // 使用 JavaScript 的 Array.sort 模拟堆排序，返回最大的 n 个元素
    const sortedNums = [...nums].sort((a, b) => b - a); // 降序排序
    return sortedNums.slice(0, n); // 返回前 n 个最大的元素
}}' 
[结束] 

你是一个 TypeScript 程序员专家, 下面是你的任务: {} 你的代码需要通以下测试:
{}
[开始]
'''.format(item.get("description_cn"), "\n".join(tests))

    elif lang.lower() == "php":
        prompt = '''\
你是一个 php 程序员专家, 下面是你的任务: 编写一个函数，这个函数从给定的两个元祖列表中查找相似的元素. 你的代码需要通以下测试:
assert similar_elements((3, 4, 5, 6),(5, 7, 4, 10)) == (4, 5)
assert similar_elements((1, 2, 3, 4),(5, 4, 3, 7)) == (3, 4) 
assert similar_elements((11, 12, 14, 13),(17, 15, 14, 13)) == (13, 14) 
[开始]
"<?php
function similarElements(array $testTup1, array $testTup2): array {{
    // 将两个数组转换为集合
    $set1 = array_unique($testTup1);
    $set2 = array_unique($testTup2);

    // 使用 array_intersect 获取交集
    $result = array_values(array_intersect($set1, $set2));

    return $result;
}}"
[结束] 

你是一个 php 程序员专家, 下面是你的任务: 编写一个 php 函数来识别非素数. 你的代码需要通以下测试:
assert is_not_prime(2) == False 
assert is_not_prime(10) == True 
assert is_not_prime(35) == True 
[开始]
'<?php
function is_not_prime($n) {{
    $result = false;
    for ($i = 2; $i <= sqrt($n); $i++) {{
        if ($n % $i == 0) {{
            $result = true;
            break;
        }}
    }}
    return $result;
}}
' 
[结束] 

你是一个 php 程序员专家, 下面是你的任务: 编写一个函数，使用堆队列算法从给定的数字列表中查找最大的整数. 你的代码需要通以下测试:
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],3)==[85, 75, 65] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],2)==[85, 75] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],5)==[85, 75, 65, 58, 35] 
[开始]
'<?php

function heapQueueLargest(array $nums, int $n): array {{
    // 按降序排序
    rsort($nums);
    // 获取前 n 个最大的元素
    return array_slice($nums, 0, $n);
}}' 
[结束] 

你是一个 php 程序员专家, 下面是你的任务: {} 你的代码需要通以下测试:
{}
[开始]
'''.format(item.get("description_cn"), "\n".join(tests))

    elif lang.lower() == "javascript" or lang.lower() == "js":
        prompt = '''\
你是一个 JavaScript 程序员专家, 下面是你的任务: 编写一个 JavaScript 函数，这个函数从给定的两个元祖列表中查找相似的元素. 你的代码需要通以下测试:
assert similar_elements((3, 4, 5, 6),(5, 7, 4, 10)) == (4, 5)
assert similar_elements((1, 2, 3, 4),(5, 4, 3, 7)) == (3, 4) 
assert similar_elements((11, 12, 14, 13),(17, 15, 14, 13)) == (13, 14) 
[开始]
"function similarElements(testTup1, testTup2) {{
    // 将数组转换为 Set
    const set1 = new Set(testTup1);
    const set2 = new Set(testTup2);

    // 计算交集
    const result = [...set1].filter(element => set2.has(element));

    return result;
}}"
[结束] 

你是一个 JavaScript 程序员专家, 下面是你的任务: 编写一个 JavaScript 函数来识别非素数. 你的代码需要通以下测试:
assert is_not_prime(2) == False 
assert is_not_prime(10) == True 
assert is_not_prime(35) == True 
[开始]
"function isNotPrime(n) {{
    let result = false;
    for (let i = 2; i <= Math.sqrt(n); i++) {{
        if (n % i === 0) {{
            result = true;
            break;
        }}
    }}
    return result;
}}" 
[结束] 

你是一个 JavaScript 程序员专家, 下面是你的任务: 编写一个JavaScript函数，使用堆队列算法从给定的数字列表中查找最大的整数. 你的代码需要通以下测试:
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],3)==[85, 75, 65] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],2)==[85, 75] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],5)==[85, 75, 65, 58, 35] 
[开始]
'function heapQueueLargest(nums, n) {{
    // 使用排序模拟堆操作，按降序排列
    const sortedNums = [...nums].sort((a, b) => b - a);
    // 返回前 n 个最大的元素
    return sortedNums.slice(0, n);
}}' 
[结束] 

你是一个 JavaScript 程序员专家, 下面是你的任务: {} 你的代码需要通以下测试:
{}
[开始]
'''.format(item.get("description_cn"), "\n".join(tests))

    elif lang.lower() == "java":
        prompt = '''\
你是一个 java 程序员专家, 下面是你的任务: 编写一个函数，这个函数从给定的两个元祖列表中查找相似的元素. 你的代码需要通以下测试:
assert similar_elements((3, 4, 5, 6),(5, 7, 4, 10)) == (4, 5)
assert similar_elements((1, 2, 3, 4),(5, 4, 3, 7)) == (3, 4) 
assert similar_elements((11, 12, 14, 13),(17, 15, 14, 13)) == (13, 14) 
[开始]
"import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.stream.Collectors;

public class Main {{

    public static Set<Integer> similarElements(int[] array1, int[] array2) {{
        // 将两个数组转换为集合
        Set<Integer> set1 = Arrays.stream(array1).boxed().collect(Collectors.toSet());
        Set<Integer> set2 = Arrays.stream(array2).boxed().collect(Collectors.toSet());

        // 计算交集
        set1.retainAll(set2);

        return new HashSet<>(set1); // 返回交集的集合
    }}
}}"
[结束] 

你是一个 java 程序员专家, 下面是你的任务: 编写一个 java 函数来识别非素数. 你的代码需要通以下测试:
assert is_not_prime(2) == False 
assert is_not_prime(10) == True 
assert is_not_prime(35) == True 
[开始]
"public class Main {{
    public static boolean isNotPrime(int n) {{
        boolean result = false;
        for (int i = 2; i <= Math.sqrt(n); i++) {{
            if (n % i == 0) {{
                result = true;
            }}
        }}
        return result;
    }}"
[结束] 

你是一个 java 程序员专家, 下面是你的任务: 编写一个函数，使用堆队列算法从给定的数字列表中查找最大的整数. 你的代码需要通以下测试:
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],3)==[85, 75, 65] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],2)==[85, 75] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],5)==[85, 75, 65, 58, 35] 
[开始]
'import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class HeapQueueLargest {{

    public static List<Integer> heapQueueLargest(List<Integer> nums, int n) {{
        // 创建一个副本，避免修改原数组
        List<Integer> sortedNums = new ArrayList<>(nums);
        // 对数组进行降序排序
        sortedNums.sort(Collections.reverseOrder());
        // 返回前 n 个最大的元素
        return sortedNums.subList(0, n);
    }}
}}' 
[结束] 

你是一个 java 程序员专家, 下面是你的任务: {} 你的代码需要通以下测试:
{}
[开始]
'''.format(item.get("description_cn"), "\n".join(tests))

    elif lang.lower() == "go":
        prompt = """\
你是一个 go 程序员专家, 下面是你的任务: 编写一个函数，这个函数从给定的两个元祖列表中查找相似的元素. 你的代码需要通以下测试:
assert similar_elements((3, 4, 5, 6),(5, 7, 4, 10)) == (4, 5)
assert similar_elements((1, 2, 3, 4),(5, 4, 3, 7)) == (3, 4) 
assert similar_elements((11, 12, 14, 13),(17, 15, 14, 13)) == (13, 14) 
[开始]
'package main

import (
    "fmt"
)

// similarElements 返回两个切片中的共同元素
func similarElements(testTup1, testTup2 []int) []int {{
    set := make(map[int]bool)
    var res []int
    for _, v := range testTup1 {{
        set[v] = true
    }}

    for _, v := range testTup2 {{
        if set[v] {{
            res = append(res, v)
            set[v] = false // 确保每个元素只添加一次
        }}
    }}
    return res
}}'
[结束] 

你是一个 go 程序员专家, 下面是你的任务: 编写一个 go 函数来识别非素数. 你的代码需要通以下测试:
assert is_not_prime(2) == False 
assert is_not_prime(10) == True 
assert is_not_prime(35) == True 
[开始]
'package main

import (
    "fmt"
    "math"
)

func isNotPrime(n int) bool {{
    result := false
    for i := 2; i <= int(math.Sqrt(float64(n))); i++ {{
        if n%i == 0 {{
            result = true
        }}
    }}
    return result
}}
'
[结束] 

你是一个 go 程序员专家, 下面是你的任务: 编写一个函数，使用堆队列算法从给定的数字列表中查找最大的整数. 你的代码需要通以下测试:
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],3)==[85, 75, 65] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],2)==[85, 75] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],5)==[85, 75, 65, 58, 35] 
[开始]
'package main

import (
    "fmt"
    "sort"
)

func heapQueueLargest(nums []int, n int) []int {{
    // 创建一个副本，避免修改原始数组
    sortedNums := append([]int{{}}, nums...)
    // 按降序排序
    sort.Sort(sort.Reverse(sort.IntSlice(sortedNums)))
    // 返回前 n 个最大的元素
    return sortedNums[:n]
}}' 
[结束] 

你是一个 go 程序员专家, 下面是你的任务: {} 你的代码需要通以下测试:
{}
[开始]
""".format(item.get("description_cn"), "\n".join(tests))

    elif lang.lower() == "cpp":
        prompt = '''\
你是一个 cpp 程序员专家, 下面是你的任务: 编写一个函数，这个函数从给定的两个元祖列表中查找相似的元素. 你的代码需要通以下测试:
assert similar_elements((3, 4, 5, 6),(5, 7, 4, 10)) == (4, 5)
assert similar_elements((1, 2, 3, 4),(5, 4, 3, 7)) == (3, 4) 
assert similar_elements((11, 12, 14, 13),(17, 15, 14, 13)) == (13, 14) 
[开始]
"#include <iostream>
#include <vector>
#include <set>
#include <algorithm>
#include <cassert>

// 返回两个向量中的共同元素
std::vector<int> similarElements(const std::vector<int>& testTup1, const std::vector<int>& testTup2) {{
    std::set<int> set1(testTup1.begin(), testTup1.end());
    std::set<int> set2(testTup2.begin(), testTup2.end());
    
    std::vector<int> res;
    std::set_intersection(set1.begin(), set1.end(), set2.begin(), set2.end(), std::back_inserter(res));
    
    return res;
}}"
[结束] 

你是一个 cpp 程序员专家, 下面是你的任务: 编写一个 cpp 函数来识别非素数. 你的代码需要通以下测试:
assert is_not_prime(2) == False 
assert is_not_prime(10) == True 
assert is_not_prime(35) == True 
[开始]
'#include <iostream>
#include <cmath> // 用于 sqrt 函数

using namespace std;

bool isNotPrime(int n) {{
    bool result = false;
    for (int i = 2; i <= sqrt(n); i++) {{
        if (n % i == 0) {{
            result = true;
        }}
    }}
    return result;
}}' 
[结束] 

你是一个 cpp 程序员专家, 下面是你的任务: 编写一个函数，使用堆队列算法从给定的数字列表中查找最大的整数. 你的代码需要通以下测试:
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],3)==[85, 75, 65] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],2)==[85, 75] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],5)==[85, 75, 65, 58, 35] 
[开始]
'#include <iostream>
#include <vector>
#include <queue>

std::vector<int> heapQueueLargest(std::vector<int>& nums, int n) {{
    // 使用优先队列（最大堆）
    std::priority_queue<int> maxHeap;
    for (int num : nums) {{
        maxHeap.push(num);
    }}

    // 提取前 n 个最大的元素
    std::vector<int> largestNums;
    for (int i = 0; i < n && !maxHeap.empty(); ++i) {{
        largestNums.push_back(maxHeap.top());
        maxHeap.pop();
    }}
    return largestNums;
}}' 
[结束] 

你是一个 cpp 程序员专家, 下面是你的任务: {} 你的代码需要通以下测试:
{}
[开始]
'''.format(item.get("description_cn"), "\n".join(tests))

    else:
        prompt = ""

    return prompt


class MbxpCnBasePreProcessor(BasePreProcessor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def pre_process(self, dataset: List[Dict], language: str, task_mode: str, dataset_name: str, **kwargs) -> List[str]:
        prompt_list = []
        for data in dataset:
            prompt = get_mbxp_cn_prompt(data, language)
            prompt_list.append(prompt)
        print("prompt_real:", prompt_list[0])
        return prompt_list
