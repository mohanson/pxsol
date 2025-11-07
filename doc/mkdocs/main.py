import shutil
import os
import subprocess


def call(c: str):
    return subprocess.run(c, check=True, shell=True)


def main() -> None:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    os.chdir(f'{root}')
    shutil.rmtree('doc/mkdocs/docs/content', ignore_errors=True)
    shutil.rmtree('doc/mkdocs/docs/img', ignore_errors=True)
    shutil.copytree(os.path.join(root, 'doc/markdown/content'), 'doc/mkdocs/docs/content')
    shutil.copytree(os.path.join(root, 'doc/markdown/img'), 'doc/mkdocs/docs/img')

    os.chdir(f'{root}/doc/mkdocs')
    if shutil.which('mkdocs') is not None:
        call('mkdocs build')


if __name__ == '__main__':
    main()
