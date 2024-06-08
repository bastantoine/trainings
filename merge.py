import argparse
import json
from pathlib import Path

import frontmatter
from loguru import logger


def merge_markdown_files(
    frontmatter_file: str | Path,
    input_files: list[str | Path],
    output_file: str | Path,
):
    merged = ""

    with open(frontmatter_file, "r") as f:
        merged = f.read()
    for file in input_files:
        with open(file, "r") as f:
            content = frontmatter.loads(f.read()).content
            merged += content + "\n\n---\n\n"

    merged = merged.replace("../Attachements", "Attachements")
    logger.info(f"Done merging {len(input_files)} file(s) into {output_file}")
    with open(output_file, "w") as output:
        output.write(merged)


def main():
    parser = argparse.ArgumentParser(description="Merge files together.")
    parser.add_argument("config_file", type=Path)
    args = parser.parse_args()

    config_file = Path(args.config_file)
    with open(config_file, "r") as f:
        config = json.loads(f.read())

    root_path = config_file.parent
    frontmatter_file = root_path / config["frontmatter_file"]
    for conf in config["configs"]:
        base_path = root_path / conf["base_path"]
        input_files = [base_path / file for file in conf["input_files"]]
        output_file = base_path / conf["output_file"]
        logger.info(f"Merging {len(input_files)} file(s) in {base_path}")
        merge_markdown_files(frontmatter_file, input_files, output_file)


if __name__ == "__main__":
    main()
