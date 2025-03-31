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
You are an expert TypeScript programmer, and here is your task: Write a function to find the similar elements from the given two tuple lists. Your code should pass these tests:
assert similar_elements((3, 4, 5, 6),(5, 7, 4, 10)) == (4, 5)
assert similar_elements((1, 2, 3, 4),(5, 4, 3, 7)) == (3, 4) 
assert similar_elements((11, 12, 14, 13),(17, 15, 14, 13)) == (13, 14) 
[BEGIN]
"function similarElements(testTup1: any[], testTup2: any[]): any[] {{
    const set1 = new Set(testTup1);
    const set2 = new Set(testTup2);
    const result = Array.from(set1).filter(element => set2.has(element));
    return result;
}}"
[DONE]  

You are an expert TypeScript programmer, and here is your task: Write a TypeScript function to identify non-prime numbers. Your code should pass these tests:
assert is_not_prime(2) == False 
assert is_not_prime(10) == True 
assert is_not_prime(35) == True 
[BEGIN]
'function isNotPrime(n: number): boolean {{
    let result = false;
    for (let i = 2; i <= Math.sqrt(n); i++) {{
        if (n % i === 0) {{
            result = true;
        }}
    }}
    return result;
}}'
[DONE]  

You are an expert TypeScript programmer, and here is your task: Write a function to find the largest integers from a given list of numbers using heap queue algorithm. Your code should pass these tests:
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],3)==[85, 75, 65] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],2)==[85, 75] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],5)==[85, 75, 65, 58, 35] 
[BEGIN]
'function heapQueueLargest(nums: number[], n: number): number[] {{
    const sortedNums = [...nums].sort((a, b) => b - a); 
    return sortedNums.slice(0, n);
}}' 
[DONE]  

You are an expert TypeScript programmer, and here is your task: {} Your code should pass these tests:
{}
[BEGIN]
'''.format(item.get("description"), "\n".join(tests))

    elif lang.lower() == "php":
        prompt = '''\
You are an expert PHP programmer, and here is your task: Write a function to find the similar elements from the given two tuple lists. Your code should pass these tests:
assert similar_elements((3, 4, 5, 6),(5, 7, 4, 10)) == (4, 5)
assert similar_elements((1, 2, 3, 4),(5, 4, 3, 7)) == (3, 4) 
assert similar_elements((11, 12, 14, 13),(17, 15, 14, 13)) == (13, 14) 
[BEGIN]
"<?php
function similarElements(array $testTup1, array $testTup2): array {{
    $set1 = array_unique($testTup1);
    $set2 = array_unique($testTup2);

    $result = array_values(array_intersect($set1, $set2));

    return $result;
}}"
[DONE]  

You are an expert PHP programmer, and here is your task: Write a PHP function to identify non-prime numbers. Your code should pass these tests:
assert is_not_prime(2) == False 
assert is_not_prime(10) == True 
assert is_not_prime(35) == True 
[BEGIN]
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
[DONE]  

You are an expert PHP programmer, and here is your task: Write a function to find the largest integers from a given list of numbers using heap queue algorithm. Your code should pass these tests:
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],3)==[85, 75, 65] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],2)==[85, 75] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],5)==[85, 75, 65, 58, 35] 
[BEGIN]
'<?php

function heapQueueLargest(array $nums, int $n): array {{
    rsort($nums);
    return array_slice($nums, 0, $n);
}}' 
[DONE]  

You are an expert PHP programmer, and here is your task: {} Your code should pass these tests:
{}
[BEGIN]
'''.format(item.get("description"), "\n".join(tests))

    elif lang.lower() == "javascript" or lang.lower() == "js":
        prompt = '''\
You are an expert JavaScript programmer, and here is your task: Write a function to find the similar elements from the given two tuple lists. Your code should pass these tests:
assert similar_elements((3, 4, 5, 6),(5, 7, 4, 10)) == (4, 5)
assert similar_elements((1, 2, 3, 4),(5, 4, 3, 7)) == (3, 4) 
assert similar_elements((11, 12, 14, 13),(17, 15, 14, 13)) == (13, 14) 
[BEGIN]
"function similarElements(testTup1, testTup2) {{
    const set1 = new Set(testTup1);
    const set2 = new Set(testTup2);

    const result = [...set1].filter(element => set2.has(element));

    return result;
}}"
[DONE]  

You are an expert JavaScript programmer, and here is your task: Write a JavaScript function to identify non-prime numbers. Your code should pass these tests:
assert is_not_prime(2) == False 
assert is_not_prime(10) == True 
assert is_not_prime(35) == True 
[BEGIN]
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
[DONE]  

You are an expert JavaScript programmer, and here is your task: Write a function to find the largest integers from a given list of numbers using heap queue algorithm. Your code should pass these tests:
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],3)==[85, 75, 65] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],2)==[85, 75] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],5)==[85, 75, 65, 58, 35] 
[BEGIN]
'function heapQueueLargest(nums, n) {{
    const sortedNums = [...nums].sort((a, b) => b - a);
    return sortedNums.slice(0, n);
}}' 
[DONE]  

You are an expert JavaScript programmer, and here is your task: {} Your code should pass these tests:
{}
[BEGIN]
'''.format(item.get("description"), "\n".join(tests))

    elif lang.lower() == "java":
        prompt = '''\
You are an expert Java programmer, and here is your task: Write a function to find the similar elements from the given two tuple lists. Your code should pass these tests:
assert similar_elements((3, 4, 5, 6),(5, 7, 4, 10)) == (4, 5)
assert similar_elements((1, 2, 3, 4),(5, 4, 3, 7)) == (3, 4) 
assert similar_elements((11, 12, 14, 13),(17, 15, 14, 13)) == (13, 14) 
[BEGIN]
"import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.stream.Collectors;

public class Main {{

    public static Set<Integer> similarElements(int[] array1, int[] array2) {{
        Set<Integer> set1 = Arrays.stream(array1).boxed().collect(Collectors.toSet());
        Set<Integer> set2 = Arrays.stream(array2).boxed().collect(Collectors.toSet());

        set1.retainAll(set2);

        return new HashSet<>(set1);
    }}
}}"
[DONE]  

You are an expert Java programmer, and here is your task: Write a Java function to identify non-prime numbers. Your code should pass these tests:
assert is_not_prime(2) == False 
assert is_not_prime(10) == True 
assert is_not_prime(35) == True 
[BEGIN]
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
[DONE]  

You are an expert Java programmer, and here is your task: Write a function to find the largest integers from a given list of numbers using heap queue algorithm. Your code should pass these tests:
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],3)==[85, 75, 65] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],2)==[85, 75] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],5)==[85, 75, 65, 58, 35] 
[BEGIN]
'import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class HeapQueueLargest {{

    public static List<Integer> heapQueueLargest(List<Integer> nums, int n) {{
        List<Integer> sortedNums = new ArrayList<>(nums);
        sortedNums.sort(Collections.reverseOrder());
        return sortedNums.subList(0, n);
    }}
}}' 
[DONE]  

You are an expert Java programmer, and here is your task: {} Your code should pass these tests:
{}
[BEGIN]
'''.format(item.get("description"), "\n".join(tests))

    elif lang.lower() == "go":
        prompt = """\
You are an expert Go programmer, and here is your task: Write a function to find the similar elements from the given two tuple lists. Your code should pass these tests:
assert similar_elements((3, 4, 5, 6),(5, 7, 4, 10)) == (4, 5)
assert similar_elements((1, 2, 3, 4),(5, 4, 3, 7)) == (3, 4) 
assert similar_elements((11, 12, 14, 13),(17, 15, 14, 13)) == (13, 14) 
[BEGIN]
'package main

import (
    "fmt"
)

func similarElements(testTup1, testTup2 []int) []int {{
    set := make(map[int]bool)
    var res []int
    for _, v := range testTup1 {{
        set[v] = true
    }}

    for _, v := range testTup2 {{
        if set[v] {{
            res = append(res, v)
            set[v] = false
        }}
    }}
    return res
}}'
[DONE]  

You are an expert Go programmer, and here is your task: Write a Go function to identify non-prime numbers. Your code should pass these tests:
assert is_not_prime(2) == False 
assert is_not_prime(10) == True 
assert is_not_prime(35) == True 
[BEGIN]
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
[DONE]  

You are an expert Go programmer, and here is your task: Write a function to find the largest integers from a given list of numbers using heap queue algorithm. Your code should pass these tests:
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],3)==[85, 75, 65] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],2)==[85, 75] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],5)==[85, 75, 65, 58, 35] 
[BEGIN]
'package main

import (
    "fmt"
    "sort"
)

func heapQueueLargest(nums []int, n int) []int {{
    sortedNums := append([]int{{}}, nums...)
    sort.Sort(sort.Reverse(sort.IntSlice(sortedNums)))
    return sortedNums[:n]
}}' 
[DONE]  

You are an expert Go programmer, and here is your task: {} Your code should pass these tests:
{}
[BEGIN]
""".format(item.get("description"), "\n".join(tests))

    elif lang.lower() == "cpp":
        prompt = '''\
You are an expert Cpp programmer, and here is your task: Write a function to find the similar elements from the given two tuple lists. Your code should pass these tests:
assert similar_elements((3, 4, 5, 6),(5, 7, 4, 10)) == (4, 5)
assert similar_elements((1, 2, 3, 4),(5, 4, 3, 7)) == (3, 4) 
assert similar_elements((11, 12, 14, 13),(17, 15, 14, 13)) == (13, 14) 
[BEGIN]
"#include <iostream>
#include <vector>
#include <set>
#include <algorithm>
#include <cassert>

std::vector<int> similarElements(const std::vector<int>& testTup1, const std::vector<int>& testTup2) {{
    std::set<int> set1(testTup1.begin(), testTup1.end());
    std::set<int> set2(testTup2.begin(), testTup2.end());
    
    std::vector<int> res;
    std::set_intersection(set1.begin(), set1.end(), set2.begin(), set2.end(), std::back_inserter(res));
    
    return res;
}}"
[DONE]  

You are an expert Cpp programmer, and here is your task: Write a Cpp function to identify non-prime numbers. Your code should pass these tests:
assert is_not_prime(2) == False 
assert is_not_prime(10) == True 
assert is_not_prime(35) == True 
[BEGIN]
'#include <iostream>
#include <cmath>

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
[DONE]  

You are an expert Cpp programmer, and here is your task: Write a function to find the largest integers from a given list of numbers using heap queue algorithm. Your code should pass these tests:
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],3)==[85, 75, 65] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],2)==[85, 75] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],5)==[85, 75, 65, 58, 35] 
[BEGIN]
'#include <iostream>
#include <vector>
#include <queue>

std::vector<int> heapQueueLargest(std::vector<int>& nums, int n) {{
    std::priority_queue<int> maxHeap;
    for (int num : nums) {{
        maxHeap.push(num);
    }}

    std::vector<int> largestNums;
    for (int i = 0; i < n && !maxHeap.empty(); ++i) {{
        largestNums.push_back(maxHeap.top());
        maxHeap.pop();
    }}
    return largestNums;
}}' 
[DONE]  

You are an expert Cpp programmer, and here is your task: {} Your code should pass these tests:
{}
[BEGIN]
'''.format(item.get("description"), "\n".join(tests))

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
