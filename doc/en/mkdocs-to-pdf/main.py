import shutil
import os
import subprocess


def main() -> None:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    os.chdir(f'{root}')
    shutil.rmtree('doc/en/mkdocs-to-pdf/docs/content', ignore_errors=True)
    shutil.rmtree('doc/en/mkdocs-to-pdf/docs/img', ignore_errors=True)
    shutil.copytree(os.path.join(root, 'doc/en/markdown/content'), 'doc/en/mkdocs-to-pdf/docs/content')
    shutil.copytree(os.path.join(root, 'doc/en/markdown/img'), 'doc/en/mkdocs-to-pdf/docs/img')

    os.chdir(f'{root}/doc/en/mkdocs-to-pdf')
    if shutil.which('mkdocs') is not None:
        subprocess.run('mkdocs build', check=True, shell=True)


if __name__ == '__main__':
    main()
