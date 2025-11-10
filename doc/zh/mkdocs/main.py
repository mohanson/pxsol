import shutil
import os
import subprocess


def main() -> None:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    os.chdir(f'{root}')
    shutil.rmtree('doc/zh/mkdocs/docs/content', ignore_errors=True)
    shutil.rmtree('doc/zh/mkdocs/docs/img', ignore_errors=True)
    shutil.copytree(os.path.join(root, 'doc/zh/markdown/content'), 'doc/zh/mkdocs/docs/content')
    shutil.copytree(os.path.join(root, 'doc/zh/markdown/img'), 'doc/zh/mkdocs/docs/img')

    os.chdir(f'{root}/doc/zh/mkdocs')
    if shutil.which('mkdocs') is not None:
        subprocess.run('mkdocs build', check=True, shell=True)


if __name__ == '__main__':
    main()
