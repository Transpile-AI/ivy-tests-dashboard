import argparse
from collections import defaultdict
import datetime
from pymongo import MongoClient


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Write the test results for the remote MongoDB to the dashboard")
    parser.add_argument("--db-key", type=str, help="Key for the MongoDB database")

    args = parser.parse_args()

    uri = f"mongodb+srv://{args.db_key}@ivytestdashboard.mnzyom5.mongodb.net/?retryWrites=true&w=majority&appName=IvyTestDashboard"
    client = MongoClient(uri)
    db = client.ivytestdashboard
    collection = db["test_results"]

    records = collection.find()

    missing_button = f"[![missing](https://img.shields.io/badge/missing-gray)]()"
    test_results = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {'numpy': missing_button, 'jax': missing_button, 'tensorflow': missing_button, 'torch': missing_button})))

    color_codes = {
        "passed": "green",
        "failed": "red",
        "skipped": "yellow",
        "missing": "gray",
    }

    for record in records:
        path = record['path']
        
        if path.startswith("test_frontends/test_jax/"):
            path = path.replace("test_frontends/test_jax/", "")
            base = "JAX Frontends"
        elif path.startswith("test_frontends/test_numpy/"):
            path = path.replace("test_frontends/test_numpy/", "")
            base = "Numpy Frontends"
        elif path.startswith("test_frontends/test_tensorflow/"):
            path = path.replace("test_frontends/test_tensorflow/", "")
            base = "TensorFlow Frontends"
        elif path.startswith("test_frontends/test_torch/"):
            path = path.replace("test_frontends/test_torch/", "")
            base = "PyTorch Frontends"
        elif path.startswith("test_functional/test_core/"):
            path = path.replace("test_functional/test_core/", "")
            base = "Ivy Functional API - Core"
        elif path.startswith("test_functional/test_nn/"):
            path = path.replace("test_functional/test_nn/", "")
            base = "Ivy Functional API - NN"
        elif path.startswith("test_functional/test_experimental/test_core/"):
            path = path.replace("test_functional/test_experimental/test_core/", "")
            base = "Ivy Functional API - Experimental Core"
        elif path.startswith("test_functional/test_experimental/test_nn/"):
            path = path.replace("test_functional/test_experimental/test_nn/", "")
            base = "Ivy Functional API - Experimental NN"
        else:
            base = "Other"
        
        function = record['function']
        backend = record['backend']
        outcome = record['outcome']
        workflow_link = record['workflow_link']
        color = color_codes.get(outcome, 'yellow')
        button = f"[![{outcome}](https://img.shields.io/badge/{outcome}-{color})]({workflow_link})"
        if workflow_link not in [None, "null"]:
            test_results[base][path][function][backend] = button

    # sort the paths & functions
    sorted_paths = sorted(test_results.keys())
    sorted_test_results = {path: dict(sorted(test_results[path].items())) for path in sorted_paths}

    now = datetime.datetime.now()
    current_date = now.date()

    readme_content = "# Ivy Test Dashboard\n\n"
    readme_content += f"### Last updated: {current_date}\n\n"

    for base, path_functions in sorted_test_results.items():
        readme_content += f"<div style='margin-top: 35px; margin-bottom: 20px; margin-left: 25px;'>\n"
        readme_content += f"<details>\n<summary style='margin-right: 10px;'><span style='font-size: 1.5em; font-weight: bold'>{base}</span></summary>\n\n"

        for path, functions in path_functions.items():
            readme_content += f"<div style='margin-top: 7px; margin-botton: 1px; margin-left: 25px;'>\n"
            readme_content += f"<details>\n<summary><span style=''>{path}</span></summary>\n\n"
            readme_content += "| Function | numpy | jax | tensorflow | torch |\n"
            readme_content += "|----------|-------|-----|------------|-------|\n"

            for function, results in functions.items():
                readme_content += f"| {function} | {results['numpy']} | {results['jax']} | {results['tensorflow']} | {results['torch']} |\n"

            readme_content += "</details>\n\n"
            readme_content += "</div>\n\n"
        readme_content += "</details>\n\n"
        readme_content += "</div>\n\n"
    readme_content += "\n\n*This dashboard is automatically updated nightly. If it hasn't been updated in within the last couple of days, feel free to raise an issue on the ivy repo.*"

    with open("DASHBOARD.md", "w") as f:
        f.write(readme_content)

    with open("DASHBOARD.md", "r") as f:
        lines = f.readlines()
        for line in lines:
            print(line)
