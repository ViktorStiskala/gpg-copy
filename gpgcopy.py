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

    total_length = sum(1 for item in src.rglob('*'))

    with click.progressbar(src.rglob('*'), length=total_length, show_pos=True, bar_template='[%(bar)s]  %(info)s  %(label)s') as bar:
        for srcfile in bar:
            if not srcfile.is_file():
                continue

            rel = srcfile.relative_to(src)
            bar.label = rel

            if len(rel.parents) > 1:
                (dest / rel.parent).mkdir(parents=True, exist_ok=True)

            dstfile = (dest / rel).with_suffix(srcfile.suffix + '.gpg')

            # do not overwrite existing files which are larger or same as src file
            if dstfile.exists() and dstfile.stat().st_size >= srcfile.stat().st_size:
                continue

            recipient_args = itertools.chain.from_iterable(('-r', r) for r in recipient)
            try:
                params = ['gpg', '--batch', '--always-trust', '--yes', '-e', '-o', dstfile, *recipient_args, srcfile]
                subprocess.run(params, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError as exc:
                click.echo(click.style('\n{}\n{}'.format(exc, exc.stderr.decode('utf-8', errors='ignore')), fg='red', bold=True), err=True)
                sys.exit(1)


if __name__ == '__main__':
    copy_files()
