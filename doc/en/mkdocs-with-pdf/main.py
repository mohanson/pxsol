import shutil
import os
import subprocess


def call(c: str):
    return subprocess.run(c, check=True, shell=True)


def main() -> None:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    os.chdir(f'{root}')
    shutil.rmtree('doc/en/mkdocs-with-pdf/docs/content', ignore_errors=True)
    shutil.rmtree('doc/en/mkdocs-with-pdf/docs/img', ignore_errors=True)
    shutil.copytree(os.path.join(root, 'doc/en/markdown/content'), 'doc/en/mkdocs-with-pdf/docs/content')
    shutil.copytree(os.path.join(root, 'doc/en/markdown/img'), 'doc/en/mkdocs-with-pdf/docs/img')

    os.chdir(f'{root}/doc/en/mkdocs-with-pdf')
    if shutil.which('mkdocs') is not None:
        call('mkdocs build')


if __name__ == '__main__':
    main()
