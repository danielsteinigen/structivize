import json
import multiprocessing
import os
import re
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

from tqdm import tqdm

from structivize.renderer import Renderer
from structivize.renderers.biology import *
from structivize.renderers.business import *
from structivize.renderers.charts import *
from structivize.renderers.chemistry import *
from structivize.renderers.culture import *
from structivize.renderers.datastructure import *
from structivize.renderers.drawing import *
from structivize.renderers.electronics import *
from structivize.renderers.modeling import *
from structivize.utils import load_json, load_jsonl, save_json, save_text


def build_sample(sample_process):

    id = sample_process["id"]
    sample = sample_process["sample"]
    save_dir = sample_process["save_dir"]
    category_key = sample["input"]["category_key"]
    lang_key = sample["input"]["lang_key"]
    output_base_path = f"{save_dir}/images/{category_key}_{lang_key}/{id}"

    dataset_sample = {
        "id": id,
        "input": sample["input"],
        "language_generated": sample["language_generated"] if "language_generated" in sample else "",
        "problem": sample["problem"] if "problem" in sample else "",
        "description": sample["description"] if "description" in sample else "",
        "answer": sample["answer"] if "answer" in sample else "",
        "code": sample["code"],
        "path_code": "",
        "path_img_1": "",
        "path_img_2": "",
        "path_log": "",
        "tool_1": "",
        "tool_2": "",
        "debug_message": "",
        "size": {},
        "statistics": {},
    }
    exception = None
    try:
        renderer = Renderer.from_dict(
            renderer=sample_process["renderer"], code=sample["code"], output_base_path=output_base_path, category=category_key
        )
        result = renderer.render()
        print(f'{output_base_path} - {"success" if result.success else "failed"}')
        dataset_sample["path_code"] = result.path_code
        dataset_sample["path_img_1"] = result.path_image
        dataset_sample["path_log"] = result.path_log
        dataset_sample["tool_1"] = result.tool
        dataset_sample["debug_message"] = result.debug_message
        dataset_sample["size"] = result.size.model_dump()
        dataset_sample["statistics"] = result.statistics.model_dump()
        del renderer

    except Exception as e:
        exception = f"\nAn exception occurred for {sample_process['renderer']}: {e}"
        print(exception)
        path_code = f"{save_dir}/code/{category_key}_{lang_key}/{id}.txt"
        save_text(filename=path_code, data=sample["code"])
        dataset_sample["path_code"] = path_code
        if "renderer" in vars(): del renderer

    return dataset_sample, exception


if __name__ == "__main__":
    max_workers = multiprocessing.cpu_count()
    print(f"Max workers: {max_workers}")

    data_files = [
    ]
    save_dirs = [
    ]

    for data_file, save_dir in zip(data_files, save_dirs):
        start = time.time()
        data = load_jsonl(filename=data_file)
        save_dir = save_dir

        code_categories = load_json(filename="categories_all.json")

        os.makedirs(save_dir, exist_ok=True)
        os.makedirs(f"{save_dir}/code/", exist_ok=True)
        os.makedirs(f"{save_dir}/images/", exist_ok=True)

        for category, content in code_categories.items():
            for lang, lang_cont in content["language"].items():
                os.makedirs(f"{save_dir}/images/{category}_{lang}/", exist_ok=True)
                os.makedirs(f"{save_dir}/code/{category}_{lang}/", exist_ok=True)

        idx = 0
        samples_prepared = []
        for sample in data:
            idx += 1
            samples_prepared.append(
                {
                    "id": f"{sample['input']['category_key']}_{idx}",
                    "sample": sample,
                    "save_dir": save_dir,
                    "renderer": code_categories[sample["input"]["category_key"]]["language"][sample["input"]["lang_key"]]["renderer"],
                }
            )

        dataset = []
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(build_sample, sample_process): sample_process for sample_process in samples_prepared}

            with open(f"{save_dir}/dataset.jsonl", "a", encoding="utf-8") as f, tqdm(total=len(futures)) as pbar:
                with open(f"{save_dir}/exceptions.jsonl", "a", encoding="utf-8") as f_exc:
                    for future in as_completed(futures):
                        pbar.update(1)
                        result, exc = future.result()

                        dataset.append(result)
                        f.write(f"{json.dumps(result, ensure_ascii=False)}\n")
                        if exc:
                            f_exc.write(f"{exc}\n-------------------------------------\n\n")

        save_json(filename=f"{save_dir}/dataset.json", data=dataset)

        for dirpath, dirnames, filenames in os.walk(f"{save_dir}/code/", topdown=False):
            if not dirnames and not filenames:
                try:
                    os.rmdir(dirpath)
                except OSError as e:
                    print(f"Failed to delete {dirpath}: {e}")

        for dirpath, dirnames, filenames in os.walk(f"{save_dir}/images/", topdown=False):
            if not dirnames and not filenames:
                try:
                    os.rmdir(dirpath)
                except OSError as e:
                    print(f"Failed to delete {dirpath}: {e}")

        print("Elapsed time:", time.time() - start)
        time.sleep(3)
