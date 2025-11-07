import shutil
import os
import subprocess


def call(c: str):
    return subprocess.run(c, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def main() -> None:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    os.chdir(f'{root}')
    shutil.rmtree('doc/mkdocs/docs', ignore_errors=True)
    os.makedirs('doc/mkdocs/docs')
    shutil.copytree(os.path.join(root, 'doc/markdown/content'), 'doc/mkdocs/docs/content')
    shutil.copytree(os.path.join(root, 'doc/markdown/img'), 'doc/mkdocs/docs/img')

    with open(os.path.join(root, 'doc/mkdocs/docs/index.md'), 'w') as f:
        f.write('![img](./img/cover.jpg)')
        f.write('\n')

    os.chdir(f'{root}/doc/mkdocs')
    call('mkdocs build')


main()
