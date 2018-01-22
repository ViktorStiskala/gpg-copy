import subprocess
from pathlib import Path

import click
import itertools

import sys


@click.command()
@click.argument('src', type=click.Path(exists=True, file_okay=False))
@click.argument('dest', type=click.Path(exists=True, file_okay=False))
@click.option('--recipient', '-r', multiple=True, required=True)
def copy_files(src, dest, recipient):
    src = Path(src)
    dest = Path(dest)

    for r in recipient:
        try:
            subprocess.run(['gpg', '--list-keys', r], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            raise click.UsageError('Non-existent recipient: {}. Please import the key first.'.format(r))

    total_length = sum(1 for srcfile in src.rglob('*') if srcfile.is_file())

    with click.progressbar((i for i in src.rglob('*') if i.is_file()), length=total_length, show_pos=True, bar_template='[%(bar)s]  %(info)s  %(label)s') as bar:
        for srcfile in bar:
            rel = srcfile.relative_to(src)
            bar.label = rel

            if len(rel.parents) > 1:
                (dest / rel.parent).mkdir(parents=True, exist_ok=True)

            dstfile = (dest / rel).with_suffix(srcfile.suffix + '.gpg')

            # do not overwrite existing files
            if dstfile.exists() and dstfile.stat().st_size:
                continue

            recipient_args = itertools.chain.from_iterable(('-r', r) for r in recipient)
            try:
                params = ['gpg', '--batch', '--always-trust', '--yes', '-e', '-o', str(dstfile), *recipient_args, str(srcfile)]
                subprocess.run(params, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError as exc:
                click.echo(click.style('\n{}\n{}'.format(exc, exc.stderr.decode('utf-8', errors='ignore')), fg='red', bold=True), err=True)
                sys.exit(1)


if __name__ == '__main__':
    copy_files()
