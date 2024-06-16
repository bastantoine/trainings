import json
from pathlib import Path
import shutil

import click
import frontmatter
from loguru import logger
import jinja2


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
def cli():
    pass


@cli.command(help="Merge markdown files into a single file")
@click.option(
    "-c",
    "--config-file",
    type=click.Path(exists=True),
    help="Path to the config file",
    required=True,
)
def merge(config_file):
    config_file = Path(config_file)
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
@click.option(
    "-c",
    "--config-file",
    type=click.Path(exists=True),
    help="Path to the config file",
    required=True,
)
def collect(config_file):
    config_file = Path(config_file)
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


@cli.command(help="Generate index.html from template")
@click.option(
    "-c",
    "--configs",
    help="List of config files to generate the template",
    multiple=True,
    required=True,
)
@click.option(
    "-d",
    "--destination",
    help="Destination of the generated file",
    type=click.Path(exists=True),
    required=True,
)
def template(configs, destination):
    index_configs = []
    for c in configs:
        with open(c, "r") as f:
            index_configs.append(json.loads(f.read())["index_config"])
    destination = Path(destination)
    template = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates/")
    ).get_template("index.html.j2")
    content = template.render(index_configs=index_configs)

    with open(destination / "index.html", mode="w", encoding="utf-8") as index:
        index.write(content)


if __name__ == "__main__":
    cli()
