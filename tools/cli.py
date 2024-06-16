import json
from pathlib import Path
import shutil

import click
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
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as output:
        output.write(merged)


@click.group(help="CLI for managing the build and compile steps")
@click.option(
    "-c",
    "--config-file",
    type=click.Path(exists=True),
    help="Path to the config file",
    required=True,
)
@click.pass_context
def cli(ctx, config_file):
    ctx.ensure_object(dict)
    ctx.obj["config_file"] = config_file


@cli.command(help="Merge markdown files into a single file")
@click.pass_obj
def merge(ctx):
    config_file = Path(ctx["config_file"])
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


@cli.command(help="Collect generated files in a dedicated folder")
@click.pass_obj
def collect(ctx):
    config_file = Path(ctx["config_file"])
    with open(config_file, "r") as f:
        config = json.loads(f.read())

    root_path = config_file.parent
    destination = config_file.parent / config["collect_destination"]
    destination.mkdir(parents=True, exist_ok=True)
    output_files = [
        root_path / conf["base_path"] / conf["output_file"]
        for conf in config["configs"]
    ]
    logger.info(f"Collecting {len(output_files)} file(s) in {destination}")
    for file in output_files:
        logger.info(f"Copying {file}")
        shutil.copy(file, destination)


if __name__ == "__main__":
    cli()
