#!/usr/bin/env python3
# Copyright 2020 Samsung Electronics Co., Ltd. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import argparse
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request

basePackages = [
    'gcc',
    'glibc',
    'glibc-devel',
    'libffi',
    'libgcc',
    'libstdc++',
    'libstdc++-devel',
    'linux-glibc-devel',
    'zlib-devel',
]
unifiedPackages = [
    'atk-devel',
    'at-spi2-atk-devel',
    'capi-appfw-application',
    'capi-appfw-application-devel',
    'capi-appfw-app-common',
    'capi-appfw-app-common-devel',
    'capi-appfw-app-control',
    'capi-appfw-app-control-devel',
    'capi-base-common',
    'capi-base-common-devel',
    'capi-base-utils',
    'capi-base-utils-devel',
    'capi-system-info',
    'capi-system-info-devel',
    'capi-system-system-settings',
    'capi-system-system-settings-devel',
    'capi-ui-efl-util',
    'capi-ui-efl-util-devel',
    'cbhm',
    'cbhm-devel',
    'coregl',
    'coregl-devel',
    'ecore-con-devel',
    'ecore-core',
    'ecore-core-devel',
    'ecore-evas',
    'ecore-evas-devel',
    'ecore-file-devel',
    'ecore-imf',
    'ecore-imf-devel',
    'ecore-imf-evas',
    'ecore-imf-evas-devel',
    'ecore-input',
    'ecore-input-devel',
    'ecore-wayland',
    'ecore-wayland-devel',
    'ecore-wl2',
    'ecore-wl2-devel',
    'edje-devel',
    'eet',
    'eet-devel',
    'efl-devel',
    'efl-extension',
    'efl-extension-devel',
    'efreet-devel',
    'eina',
    'eina-devel',
    'eina-tools',
    'elementary',
    'elementary-devel',
    'emile-devel',
    'eo-devel',
    'ethumb-devel',
    'evas',
    'evas-devel',
    'freetype2-devel',
    'glib2-devel',
    'jsoncpp',
    'jsoncpp-devel',
    'libatk',
    'libatk-bridge-2_0-0',
    'libfeedback',
    'libfeedback-devel',
    'libdlog',
    'libdlog-devel',
    'libglib',
    'libgobject',
    'libpng-devel',
    'libtbm',
    'libtbm-devel',
    'libtdm-client',
    'libtdm-client-devel',
    'libtdm-devel',
    'libwayland-client',
    'libwayland-cursor',
    'libwayland-egl',
    'libwayland-extension-client',
    'libxkbcommon',
    'libxkbcommon-devel',
    'tzsh',
    'tzsh-devel',
    'vulkan-headers',
    'vulkan-loader',
    'vulkan-loader-devel',
    'wayland-extension-client-devel',
    'wayland-devel',
    'xdgmime',
    'xdgmime-devel',
]
daliPackages = [
    'dali2',
    'dali2-adaptor',
    'dali2-adaptor-devel',
    'dali2-devel',
    'dali2-toolkit',
    'dali2-toolkit-devel',
]

# Use the Tizen 5.5 package repository by default for glibc version compatibility.
# The only exceptions are dali2-related packages which were added in Tizen 6.5.
base_repo = 'http://download.tizen.org/snapshots/tizen/5.5-base/latest/repos/standard/packages'
unified_repo = 'http://download.tizen.org/snapshots/tizen/5.5-unified/latest/repos/standard/packages'
dali_repo = 'http://download.tizen.org/snapshots/tizen/6.5-unified/latest/repos/standard/packages'

# Execute only if run as a script.
if __name__ != "__main__":
    sys.exit()

# Check dependencies.
for dep in ['rpm2cpio', 'cpio', 'git']:
    if not shutil.which(dep):
        sys.exit(f'{dep} is not installed. To install, run:\n'
                 f'  sudo apt install {dep}')

# Parse arguments.
parser = argparse.ArgumentParser(
    description='Tizen rootfs generator (for Flutter)')
parser.add_argument(
    '-a', '--arch', type=str, choices=['arm', 'arm64', 'x86'],
    help='target architecture (defaults to "arm")',
    default='arm')
parser.add_argument(
    '-o', '--output', metavar='STR', type=str,
    help='name of the output directory (defaults to arch)')
parser.add_argument(
    '-c', '--clean', action='store_true',
    help='clean up the output directory before proceeding')
args = parser.parse_args()

if not args.output:
    args.output = args.arch
outpath = os.path.abspath(f'{__file__}/../{args.output}')

if args.clean and os.path.exists(outpath):
    shutil.rmtree(outpath)

downloadPath = os.path.join(outpath, '.rpms')
os.makedirs(downloadPath, exist_ok=True)
existingRpms = [f for f in os.listdir(downloadPath) if f.endswith('.rpm')]

if args.arch == 'arm':
    archName = 'armv7l'
elif args.arch == 'arm64':
    archName = 'aarch64'
elif args.arch == 'x86':
    archName = 'i686'
else:
    sys.exit(f'Undefined arch: {args.arch}')

# Retrieve html documents.
documents = {}
for url in [f'{base_repo}/{archName}',
            f'{base_repo}/noarch',
            f'{unified_repo}/{archName}',
            f'{unified_repo}/noarch',
            f'{dali_repo}/{archName}']:
    request = urllib.request.Request(url)
    with urllib.request.urlopen(request) as response:
        documents[url] = response.read().decode('utf-8')

# Download packages.
for package in basePackages + unifiedPackages + daliPackages:
    quoted = urllib.parse.quote(package)
    pattern = f'{re.escape(quoted)}-\\d+\\.[\\d_\\.]+-[\\d\\.]+\\..+\\.rpm'

    if any([re.match(pattern, f) for f in existingRpms]):
        print(f'Already downloaded {package}')
        continue

    for parent, doc in documents.items():
        match = re.findall(f'<a href="({pattern})">.+?</a>', doc)
        if len(match) > 0:
            url = f'{parent}/{match[0]}'
            break

    if len(match) == 0:
        sys.exit(f'Could not find a package {package}')
    else:
        print(f'Downloading {url}...')
        urllib.request.urlretrieve(url, f'{downloadPath}/{match[0]}')

# Extract files.
for rpm in [f for f in os.listdir(downloadPath) if f.endswith('.rpm')]:
    abspath = f'{os.path.abspath(downloadPath)}/{rpm}'
    command = f'cd {outpath} && rpm2cpio {abspath} | cpio -idum --quiet'
    subprocess.run(command, shell=True, check=True)

# Create symbolic links.
if not os.path.exists(f'{outpath}/usr/include/asm'):
    os.symlink(f'asm-{args.arch}', f'{outpath}/usr/include/asm')
if args.arch == 'arm64' and not os.path.exists(f'{outpath}/usr/lib/pkgconfig'):
    os.symlink(f'../lib64/pkgconfig', f'{outpath}/usr/lib/pkgconfig')

# Copy objects required by the linker, such as crtbeginS.o and libgcc.a.
if args.arch == 'arm64':
    libpath = f'{outpath}/usr/lib64'
else:
    libpath = f'{outpath}/usr/lib'
subprocess.run(
    f'cd {libpath} && cp gcc/*/*/*.o gcc/*/*/*.a .', shell=True, check=True)

# Apply a patch if applicable.
patchFile = os.path.abspath(f'{__file__}/../{args.arch}.patch')
if os.path.exists(patchFile):
    command = f'git apply --directory sysroot/{args.output} {patchFile}'
    subprocess.run(command, shell=True, check=True)

print('Complete')
