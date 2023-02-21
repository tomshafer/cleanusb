"""Clean up a USB thumb drive for Honda audio."""

import logging
import os
import shutil
from collections import defaultdict
from pathlib import Path
from subprocess import run

import click
import mutagen

logging.basicConfig(format="%(message)s")
log = logging.getLogger(__name__)


def remove_spotlight(path: Path) -> None:
    log.info("Removing Spotlight index.")
    if os.path.isdir(path / ".Spotlight-V100"):
        log.info("  Prompting for an admin password.")
        run(f'sudo mdutil -v -X "{path}"', shell=True)
        return
    log.info("  No index directory found, skipping this step.")


def remove_lostdir(path: Path) -> None:
    log.info("Checking for `LOST.DIR` to remove.")
    if os.path.isdir(subpath := path / "LOST.DIR"):
        log.info("  Removing `LOST.DIR`.")
        os.rmdir(subpath)


def clean_dotfiles(path: Path) -> None:
    log.info("Cleaning up dotfiles with `dot_clean`.")
    run(f'dot_clean -v "{path}"', shell=True)


def remove_remaining_dotfiles(path: Path) -> None:
    log.info("Removing any remaning dotfiles.")

    queue = []
    for pwd, dirs, files in os.walk(path):
        basepwd = os.path.basename(pwd)
        queue += [
            os.path.join(pwd, x)
            for x in dirs + files
            if x.startswith(".") or basepwd.startswith(".")
        ]

    log.info(f"  Found {len(queue)} dotfile{'s' * (len(queue) != 1)} to remove.")

    for item in reversed(queue):
        log.debug(f'  * Removing "{item}".')
        os.rmdir(item) if os.path.isdir(item) else os.remove(item)


def organize_library(path: Path) -> None:
    """Find all artists and albums and organize the data."""
    log.info("Organizing MP3 files on disk.")

    # Queue up the files
    data: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(lambda: []))
    for pwd, _, files in os.walk(path):
        for file in files:
            fh = mutagen.File(os.path.join(pwd, file))

            album = resolve_keys(fh.tags, "TALB", "soal")
            artist = resolve_keys(fh.tags, "TPE2", "TPE1", "aART", "soar")
            file_path = os.path.join(pwd, file)
            log.debug(f'  Mapped "{file_path}" -> {artist} – {album}')
            data[artist][album] += [file_path]

    # Move the files
    for artist in data:
        artist_dir = path / artist
        log.info(f'  Ensuring directory "{artist_dir}"')
        os.makedirs(artist_dir, exist_ok=True)
        for album in data[artist]:
            album_dir = artist_dir / album
            log.info(f'  Ensuring directory "{album_dir}"')
            os.makedirs(album_dir, exist_ok=True)
            for file in data[artist][album]:
                if file == os.path.join(album_dir, os.path.basename(file)):
                    log.debug(f'  "{file}" exists. Skipping.')
                    continue
                log.debug(f'  Moving "{file}" -> "{album_dir}"')
                shutil.move(file, album_dir)


def resolve_keys(d: dict[str, str | list[str]], *keys: str) -> str:
    for k in keys:
        if (item := d.get(k)) is not None:
            return str(item[-1] if isinstance(item, list) else item)
    raise ValueError("could not resolve value from keys")


@click.command()
@click.help_option("-h", "--help")
@click.option("-v", "--verbose", is_flag=True, help="Be more verbose.")
@click.argument("ROOT", type=click.Path(True, False, dir_okay=True, path_type=Path))
def main(root: Path, verbose: bool) -> None:
    log.setLevel("DEBUG" if verbose else "INFO")
    log.info(f'Target = "{root}".')

    # Remove dotfiles
    remove_lostdir(root)
    remove_spotlight(root)
    clean_dotfiles(root)
    remove_remaining_dotfiles(root)

    # Organize the library
    organize_library(root)


if __name__ == "__main__":
    main()
