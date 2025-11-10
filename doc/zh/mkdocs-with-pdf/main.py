import shutil
import os
import subprocess


def call(c: str):
    return subprocess.run(c, check=True, shell=True)


def main() -> None:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    os.chdir(f'{root}')
    shutil.rmtree('doc/zh/mkdocs-with-pdf/docs/contzht', ignore_errors=True)
    shutil.rmtree('doc/zh/mkdocs-with-pdf/docs/img', ignore_errors=True)
    shutil.copytree(os.path.join(root, 'doc/zh/markdown/contzht'), 'doc/zh/mkdocs-with-pdf/docs/contzht')
    shutil.copytree(os.path.join(root, 'doc/zh/markdown/img'), 'doc/zh/mkdocs-with-pdf/docs/img')

    os.chdir(f'{root}/doc/zh/mkdocs-with-pdf')
    if shutil.which('mkdocs') is not None:
        call('mkdocs build')


if __name__ == '__main__':
    main()
