import shutil
import os
import subprocess
import sys


def main() -> None:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    os.chdir(f'{root}')
    if sys.platform == 'linux':
        result = subprocess.run(['fc-list', ':lang=zh'], capture_output=True, text=True)
        # sudo apt-get install -y fonts-noto-cjk fonts-noto-cjk-extra
        assert 'Noto Sans CJK SC' in result.stdout
    shutil.rmtree('doc/zh/mkdocs-to-pdf/docs/content', ignore_errors=True)
    shutil.rmtree('doc/zh/mkdocs-to-pdf/docs/img', ignore_errors=True)
    shutil.copytree(os.path.join(root, 'doc/zh/markdown/content'), 'doc/zh/mkdocs-to-pdf/docs/content')
    shutil.copytree(os.path.join(root, 'doc/zh/markdown/img'), 'doc/zh/mkdocs-to-pdf/docs/img')

    os.chdir(f'{root}/doc/zh/mkdocs-to-pdf')
    if shutil.which('mkdocs') is not None:
        subprocess.run('mkdocs build', check=True, shell=True)


if __name__ == '__main__':
    main()
