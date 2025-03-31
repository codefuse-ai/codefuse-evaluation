# Copyright (c) 2022-2025 Ant Group
""" evaluate scripts """
import os
import fire
import json
import gzip
import numpy as np
import re
from typing import *
from tqdm.auto import tqdm
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from util import IMPORT_HELPER, read_dataset
from metrics.metric import estimate_pass_at_k
from execution import check_correctness, check_currentmetric
from generation import EVAL_DATASET

LANGUAGE_NAME = {
    "cpp": "CPP",
    "go": "Go",
    "java": "Java",
    "js": "JavaScript",
    "python": "Python",
    "rust": "Rust",
}

METRIC_SUPPORT = [
    "pass@k",
    "accuracy",
    "precision",
    "bleu",
    'super_glue',
    'indic_glue',
    'bertscore',
    'glue',
    'coval',
    'brier_score',
    'seqeval',
    'sari',
    'codebleu',
    'poseval',
    'spearmanr',
    'xnli',
    'meteor',
    'smape',
    'competition_math',
    'character',
    'matthews_correlation',
    'cuad',
    'wiki_split',
    'mean_iou',
    'sacrebleu',
    'google_bleu',
    'recall',
    'mape',
    'xtreme_s',
    'trec_eval',
    'comet',
    'ter',
    'perplexity',
    'mase',
    'pearsonr',
    'mae',
    'roc_auc',
    'mse',
    'squad_v2',
    'squad',
    'bleurt',
    'nist_mt',
    'mahalanobis',
    'f1',
    'wer',
    'rouge',
    'frugalscore',
    'exact_match',
    'rl_reliability',
    'chrf'
]

def extract_code_before_main(code_str):
    lines = code_str.split('\n')
    main_index = -1
    for i in range(len(lines)):
        if "main()" in lines[i]:
            main_index = i
            break
    if main_index == -1:
        return code_str
    else:
        return '\n'.join(lines[:main_index])

def remove_empty_lines(code):
    lines = code.split("\n")  # 将代码按行分割成列表
    new_code = ""
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() != "":  # 如果当前行不是空行
            if line.strip().startswith("def ") or line.strip().startswith("class ") or line.strip().startswith("import ") :  # 如果当前行是def函数的定义行
                break  # 停止循环
            new_code += line + "\n"  # 将非空行添加到新的代码字符串中
        i += 1
    new_code += "\n".join(lines[i:])  # 将剩余的代码添加到新的代码字符串中
    return new_code

def process_dataset(sample, problems, test_groundtruth=False):
    task_id = sample["task_id"]
    language = task_id.split("/")[0].lower()
    if "ds1000" in language:
        language = "ds1000"
    if test_groundtruth:
        code = sample.get("reference", None)
        if code is None:
            code = sample.get("canonical_solution", None)
            if code is None:
                raise ValueError("can not find reference for sample in test_groundtruth mode", sample)
        sample["generation"] = code
    # supplement reference,prevent indicators that call non-pass@k metrics from being able to obtain reference information
    if sample.get("reference", None) is None:
        if sample.get("canonical_solution", None) is not None:
            sample["reference"] = sample["canonical_solution"]
        else:
            if problems[task_id].get("reference", None) is not None:
                sample["reference"] = problems[task_id]["reference"]
            elif problems[task_id].get("canonical_solution", None) is not None:
                sample["reference"] = problems[task_id]["canonical_solution"]
            else:
                raise ValueError("can not find reference answer for sample", sample)


def process_humaneval_test(sample, problems, codeTrans=False, test_groundtruth=False):
    task_id = sample["task_id"]
    language = task_id.split("/")[0].lower()
    if "ds1000" in language:
        language = "ds1000"
    prompt = problems[task_id]["prompt"]+"\n"
    if test_groundtruth:
        code = sample.get("reference", None)
        if code is None:
            code = sample.get("canonical_solution", "None")
        sample["generation"] = code
    code = sample["generation"]
    test = problems[task_id]["test"]
    data_type = sample.get("Difficulty")
    if codeTrans:
        # codeTrans part of the code processing
        if language == "python":
            code = remove_empty_lines( code )
            test_setup = "\n".join( IMPORT_HELPER["python"] ) + "\n"
            if code.startswith( ("def", "import") ):
                prompt_method_name = re.search( r'def\s+(\w+)', prompt ).group( 1 )
                generation_method_name = re.search( r'def\s+(\w+)', code ).group( 1 )
                if prompt_method_name != generation_method_name:
                    code = re.sub( r'def\s+(\w+)', f'def {prompt_method_name}', code )
                test_string = test_setup + code + "\n" + test + "\n"
            else:
                test_string = test_setup + prompt + code + "\n" + test + "\n"

            print( "**********Test-python****************" )
            print( test_string )
            # test_string = code + "\n" + test + "\n"
        elif language == "cpp":
            test_set_up = ""
            for s in IMPORT_HELPER["cpp"]:
                if s not in prompt:
                    test_set_up += s + "\n"
            use_std = "using namespace std;"
            test_string = ""
            if code is not None:
                match = re.search( r'\b(\w+)\(', code )
                if match:
                    method_name = match.group( 1 )
                else:
                    method_name = None

                entry_point = sample.get( "entry_point" )
                func_title = sample.get( "func_title" )
                if func_title:
                    func_title = re.search( r'(\w+)\(', func_title ).group( 1 )
                if entry_point and method_name and entry_point != method_name:
                    code = re.sub( r'\b(\w+)\(', f'{entry_point}(', code )
                elif func_title and method_name and func_title != method_name:
                    code = re.sub( r'\b(\w+)\(', f'{func_title}(', code )

                if use_std not in code:
                    test_string = "\n".join( [test_set_up, use_std, extract_code_before_main( code ), test] )
                else:
                    test_string = "\n".join( [test_set_up, extract_code_before_main( code ), test] )

            else:
                print( "无解决方法 task_id: " )
                print( task_id )
            print( "**********TestCPP****************" )
            print( test_string )
        elif language == "java":
            test_setup = "\n".join( IMPORT_HELPER["java"] ) + "\n"
            if data_type is not None and data_type == 'mbpp':
                # 代码翻译mbpp
                test_string = "\n".join( [code, test, ""] )

            elif code.split( "\n" )[0].startswith( ("class", "import") ):
                test_string = test_setup + code + "\n" + test
            else:
                test_string = test_setup + prompt + code + "\n" + test
            print( "**********Test-JAVA****************" )
            print( test_string )
        elif language == "rust":
            # print("**********Test-Rust****************")
            main = "\nfn main(){ \n } \n"
            test_string = main + prompt + code + test
            print( test_string )
        elif language == "js" or language == "javascript":
            generation = ""
            for line in code.split( "\n" ):
                generation += line + "\n"
                if line == "}" or line == "};":
                    break
            test_string = prompt + generation + "\n" + test
            # test_string = code + "\n" + test
            print( "**********Test-JS****************" )
            print( test_string )
        elif language == "go":
            import_string = problems[task_id]["import"]
            prompt = prompt.replace( import_string, "" )
            test = problems[task_id]["test"]
            test_setup = problems[task_id]["test_setup"]
            other_pkgs = []
            for pkg in IMPORT_HELPER["go"]:
                if pkg not in test_setup:
                    p = pkg.split( "/" )[-1]
                    if p + "." in code:
                        other_pkgs.append( f"\"{pkg}\"" )
            if other_pkgs:
                import_other_pkgs = "import (\n" + "    ".join( [p + "\n" for p in other_pkgs] ) + ")"
                test_string = test_setup + "\n" + import_other_pkgs + "\n" + prompt + code + "\n" + test
            else:
                test_string = test_setup + "\n" + prompt + code + "\n" + test
        else:
            raise ValueError(f"codetrans target language: {language} not supported")
        return test_string

    else:
        # Pre-process for different languages
        if language == "python":
            code_ = []
            for line in code.split("\n"):
                if "def " in line and line[0] != ' ' and line[0] != '\t':
                    code_.append("def " + line.split("def ")[1])
                    continue
                if "class" in line and line.strip().endswith(":"):
                    code_.append(line)
                    continue
                if (len(line.strip()) > 0 and line[0] != ' ' and line[0] != '\t'):
                    continue
                code_.append(line)
            code = "\n".join(code_)
            test_setup = "\n".join(IMPORT_HELPER["python"]) + "\n"
            if isinstance(test, List):
                test = "\n".join(test)

            if code.startswith("def"):
                test_string = test_setup + code + "\n\n" + test + "\n"
            else:
                test_string = test_setup + prompt + code + "\n" + test
        elif language == "cpp":
            test_set_up = ""
            for s in IMPORT_HELPER["cpp"]:
                if s not in prompt:
                    test_set_up += s + "\n"
            test_string = test_set_up + "\n" + prompt + code + "\n" + test
        elif language == "java":
            test_string = prompt + code + "\n" + test
        elif language == "js" or language == "javascript":
            test_string = prompt + code + "\n" + test
        elif language == "go":
            import_string = problems[task_id]["import"]
            prompt = prompt.replace(import_string, "")
            test_setup = problems[task_id]["test_setup"]
            other_pkgs = []
            for pkg in IMPORT_HELPER["go"]:
                if pkg not in test_setup:
                    p = pkg.split("/")[-1]
                    if p + "." in code:
                        other_pkgs.append(f"\"{pkg}\"")
            if other_pkgs:
                import_other_pkgs = "import (\n" + "    ".join([p + "\n" for p in other_pkgs]) + ")"
                test_string = test_setup + "\n" + import_other_pkgs + "\n" + prompt + code + "\n" + test
            else:
                test_string = test_setup + "\n" + prompt + code + "\n" + test
        elif language == "rust":
            main = "\nfn main(){ \n } \n"
            prompt = problems[task_id]["prompt"]
            test_string = main + prompt + code + test
        elif language == "ds1000":
            code_context = problems[task_id]["code_context"]
            test_string = code_context.replace("[insert]", code)
        else:
            raise ValueError("current language: " + language + "not supported")
        return test_string


def process_test_for_mbpp(sample, problems, language, test_groundtruth=False):
    task_id = sample["task_id"]
    test = problems[task_id]["test"]
    challenge_test = problems[task_id]["challenge_test_list"]
    if test_groundtruth:
        sample['generation'] = sample['canonical_solution']
    code = sample['generation']
    test_setup_mbpp = sample.get("test_setup", "")
    test_string = None
    if language == "python":
        test = '\n'.join(test)
        challenge_test = '\n'.join(challenge_test)
        test_setup = "\n".join(IMPORT_HELPER["python"]) + "\n"
        pattern = r"```(.*?)```"
        matches = re.findall(pattern, code, re.S)
        if matches:
            code = matches[0]
            code = code.replace('python', ' ')
        else:
            code = code

        test_string = "\n".join([test_setup, code, test_setup_mbpp, test, challenge_test, ""])

    elif language == "java":
        prompt_java = sample.get("prompt_java", "")
        test_string = "\n".join([prompt_java, code, test_setup_mbpp, test, ""])
    return test_string


def stream_jsonl_all(filename: str) -> Iterable[Dict]:
    """
    Read a list of all files and get the list of JSON data
    """
    results = []
    if filename.endswith(".gz"):
        fp = gzip.open(open(filename, "rb"), "rt")
    else:
        fp = open(filename, "r")
    for line in fp:
        if any(not x.isspace() for x in line):
            results.append(json.loads(line))
    fp.close()

    return results


def evaluate_functional_correctness(
        input_file: str = "../test/humaneval_generation_rust.jsonl",
        tmp_dir: str = "./",
        n_workers: int = 5,
        timeout: float = 120.0,
        metric: str = "pass@k",
        problem_file: str = "humaneval_python",
        out_dir: str = None,
        test_groundtruth: bool = False,
        evaluation_kwargs: Dict = {}
):
    problem_file = EVAL_DATASET.get(problem_file)
    if not os.path.exists(problem_file):
        raise FileNotFoundError("TestDataSet not exists, Please check parameter [problem_file] is correct.")

    if metric not in METRIC_SUPPORT:
        raise ValueError(f"Metric [{metric}] not supported. Supported metric list is {METRIC_SUPPORT}")

    if input_file is None or not os.path.exists(input_file):
        if not test_groundtruth:
            raise FileNotFoundError(
                "TestDataSet not exists or input_file is None, Please check parameter [input_file] is correct.")

    if test_groundtruth:
        # self-testing allows pass a folder, reads the jsonl or jsonl.gz file without recursive query
        if os.path.isdir(problem_file):
            problem_files = [os.path.join(problem_file, file) for file in os.listdir(problem_file) if
                             file.endswith(".jsonl") or file.endswith(".jsonl.gz")]
        elif os.path.isfile(problem_file):
            if problem_file.endswith(".jsonl") or problem_file.endswith(".jsonl.gz"):
                problem_files = [problem_file]
            else:
                raise ValueError("problem_file parameter is not support,please use jsonl or json.gz file")
        else:
            raise ValueError("problem_file parameter is illgal, can not load")
    else:
        if os.path.isdir(problem_file):
            raise ValueError("problem_file parameter is illgal, can not load dir，only load dir for self-test")
        elif os.path.isfile(problem_file):
            if problem_file.endswith(".jsonl") or problem_file.endswith(".jsonl.gz"):
                problem_files = [problem_file]
            else:
                raise ValueError("problem_file parameter is not support,please use jsonl or json.gz file")
        else:
            raise ValueError("problem_file parameter is illgal, can not load")

    suffix = "_evaluation_result.jsonl"

    for problemfile in problem_files:
        if "trans" in problemfile.lower():
            codeTrans = True
        else:
            codeTrans = False

        problems = read_dataset(problemfile, dataset_type="humaneval")

        if input_file is not None and not test_groundtruth:
            sample_jsonl = stream_jsonl_all(input_file)
        else:
            sample_jsonl = stream_jsonl_all(problemfile)

        if out_dir is not None:
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            if input_file is not None:
                out_file = os.path.join(out_dir, input_file.split('/')[-1].replace(".jsonl", suffix))
            else:
                out_file = os.path.join(out_dir, problemfile.split('/')[-1].replace(".jsonl", suffix))
        else:
            if input_file is not None and not test_groundtruth:
                out_file = os.path.join(input_file.replace(".jsonl", suffix))
            else:
                out_file = os.path.join(problemfile.replace(".jsonl", suffix))

        if metric == "pass@k":
            if sample_jsonl:
                sample = sample_jsonl[0]
                task_id = sample["task_id"]
                lang = task_id.split("/")[0].lower()
                if "ds1000" in lang and "tensorflow" in lang:
                    n_workers = 1
            with ThreadPoolExecutor(max_workers=n_workers) as executor:
                futures = []
                completion_id = Counter()
                n_samples = 0
                results = defaultdict(list)
                print("Reading samples...")
                for sample in tqdm(sample_jsonl):
                    task_id = sample["task_id"]
                    lang = task_id.split("/")[0].lower()
                    if "ds1000" in lang:
                        lang = "ds1000"
                    if lang == "javascript":
                        lang = "js"
                    tmp_dir_ = os.path.join(tmp_dir, lang, "evaluation")
                    if lang == "ds1000":
                        tmp_dir_ = os.path.join(tmp_dir, "CodeDataScinece", "evaluation")
                    sample["task_id"] = task_id
                    if "mbpp" in problem_file:
                        sample["test_code"] = process_test_for_mbpp(sample, problems, lang, test_groundtruth)
                    else:
                        sample["test_code"] = process_humaneval_test(sample, problems, codeTrans, test_groundtruth)
                    if sample["test_code"] is None:
                        continue
                    if "completion_id" in sample:
                        completion_id_ = sample["completion_id"]
                    else:
                        completion_id_ = completion_id[task_id]

                    args = (task_id, sample, lang, timeout, tmp_dir_, completion_id_)
                    future = executor.submit(check_correctness, *args)
                    futures.append(future)

                    completion_id[task_id] += 1
                    n_samples += 1

                print("Running test suites...")
                for future in tqdm(as_completed(futures), total=len(futures)):
                    result = future.result()
                    results[result["task_id"]].append((result["completion_id"], result))

            if len(completion_id) == len(problems):
                evaluate_pass_at_k = True
            else:
                evaluate_pass_at_k = False

            # Calculate pass@k.
            total, correct = [], []
            for result in results.values():
                passed = [r[1]["passed"] for r in result]
                total.append(len(passed))
                correct.append(sum(passed))
            total = np.array(total)
            correct = np.array(correct)
            if evaluate_pass_at_k:
                ks = [1, 10, 100]
                pass_at_k = {f"pass@{k}": estimate_pass_at_k(total, correct, k).mean()
                             for k in ks if (total >= k).all()}
                print(pass_at_k)
            else:
                print("Total:", np.sum(total))
                print("Correct:", np.sum(correct))
        else:
            if sample_jsonl:
                task_id = sample_jsonl[0]["task_id"]
                lang = task_id.split("/")[0].lower()
            else:
                lang = "python"
            if test_groundtruth:
                for sample in sample_jsonl:
                    process_dataset(sample, problems, test_groundtruth)
                results = check_currentmetric(sample_jsonl, metric, lang, **evaluation_kwargs)
                print(results)
            else:
                for sample in sample_jsonl:
                    process_dataset(sample, problems, test_groundtruth)
                results = check_currentmetric(sample_jsonl, metric, lang, **evaluation_kwargs)
                print(results)

        total_time_cost = sum( [sample.get( "processing_time", 0 ) for sample in sample_jsonl] )
        print(f"Generation Total time cost: {total_time_cost}")
        print(f"Generation Average time cost: {total_time_cost / len(list(sample_jsonl))}")
        print("Writing to: ", out_file)
        if metric == "pass@k":
            if out_file.endswith(".gz"):
                fp = gzip.GzipFile(fileobj=open(out_file, "wb"), mode="wb")
                for res in results.values():
                    for r in res:
                        fp.write((json.dumps(r[1]) + "\n").encode("utf-8"))
            else:
                fp = open(out_file, 'w')
                for res in results.values():
                    for r in res:
                        fp.write(json.dumps(r[1]) + "\n")
            fp.close()
        else:
            if out_file.endswith(".gz"):
                fp = gzip.GzipFile(fileobj=open(out_file, "wb"), mode="wb")
                fp.write((json.dumps(results) + "\n").encode("utf-8"))
            else:
                fp = open(out_file, 'w')
                fp.write(json.dumps(results) + "\n")
            fp.close()

        print("Evaluation finished.")

    print(f"evaluation all dataset {[problem.split(os.sep)[-1] for problem in problem_files]} finish")


if __name__ == "__main__":
    fire.Fire(evaluate_functional_correctness)
