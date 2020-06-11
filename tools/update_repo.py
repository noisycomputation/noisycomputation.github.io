import hashlib
import os
from pkginfo import Wheel, SDist
import re
import shutil
import sys

REPO_PATH = os.path.abspath(os.path.join('.', 'repo'))
REPO_URL = 'https://noisycomputation.github.io'


def get_pkgname(pkgpath, normalized=True):
    if pkgpath.endswith('.tar.gz'):
        dist = SDist
    elif pkgpath.endswith('.whl'):
        dist = Wheel
    else:
        raise ValueError('Package must end with .tar.gz or .whl')
    pkg = dist(pkgpath)

    # normalization follows PEP 426
    if normalized:
        name = re.sub(r'[-_.]+', '-', pkg.name).lower()
    else:
        name = pkg.name

    return name

def sha256_digest(filepath):
    buffer_size = 65536  # Don't read entire file into RAM
    file_hash = hashlib.sha256()
    with open(filepath, 'rb') as f:
        fb = f.read(buffer_size)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = f.read(buffer_size)
    return file_hash.hexdigest()



# accept only a single argument, path to new packages
if len(sys.argv) != 2 or not os.path.exists(sys.argv[1]):
    raise ValueError("This script requires one argument, the path to new packages")
    exit(1)

new_package_path = sys.argv[1]
new_packages = [
    os.path.abspath(os.path.join(new_package_path,x)) for x in os.listdir(new_package_path)
    if x.endswith('.tar.gz') or x.endswith('.whl')
    ]

# copy all new package files into the appropriate normalized package name directories
## - all destination files are overwritten if they exist
## - directories must be normalized per PEP 426, since the directory IS the package name
## - filenames do not need to conform, though hyphens and underscores are equivalent
for package_file in new_packages:
    pkg_name = get_pkgname(package_file)

    destination_dir_full = os.path.join(REPO_PATH, pkg_name)
    destination_basename = os.path.basename(package_file)
    if not os.path.isdir(destination_dir_full):
        os.mkdir(destination_dir_full, mode=0o775)

    print(f"copying {package_file}")
    print(f"     to {os.path.join(destination_dir_full, destination_basename)}")
    shutil.copy(package_file, os.path.join(destination_dir_full, destination_basename))

# regenerate repo index.html from scratch
def generate_header(title):
    return f'''<!DOCTYPE html>
<html>
  <head>
    <title>{title}</title>
    <style>
        div.package {{
            font-size: 16px;
            padding: 20px;
        }}
    </style>
  </head>
  <body>
    <h1>{title}</h1>
    <div class="package" >
'''

pkg_names = os.listdir(REPO_PATH)

main_index = generate_header("noisycomputation python repository")
for pkg_name in os.listdir(REPO_PATH):
    main_index += f'            <a href="{REPO_URL}/repo/{pkg_name}/">{pkg_name}</a><br/>\n'

    package_index = generate_header(f"{pkg_name}")
    package_files = [
        x for x in os.listdir(os.path.join(REPO_PATH, pkg_name))
        if x.endswith('.tar.gz') or x.endswith('.whl')
    ]
    for package_file in package_files:
        package_file_fullpath = os.path.join(REPO_PATH, pkg_name, package_file)
        file_hash = sha256_digest(package_file_fullpath)
        package_entry = (
            f'            <a href="{REPO_URL}/repo/{pkg_name}/{package_file}#sha256={file_hash}">'
            f'{package_file}</a><br/>\n'
        )
        package_index += package_entry
    package_index += f'''    </div>
  </body>
</html>
'''
    with open(os.path.join(REPO_PATH, pkg_name, 'index.html'), 'wt') as f:
        f.write(package_index)


main_index += f'''    </div>
  </body>
</html>
'''

with open('index.html', 'wt') as f:
    f.write(main_index)










