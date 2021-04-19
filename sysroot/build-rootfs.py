#!/usr/bin/env python3
# Copyright 2020 Samsung Electronics Co., Ltd. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import argparse
import os
import re
import shutil
import subprocess
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
    'capi-appfw-application',
    'capi-appfw-application-devel',
    'capi-appfw-app-common',
    'capi-appfw-app-common-devel',
    'capi-appfw-app-control',
    'capi-appfw-app-control-devel',
    'capi-base-common-devel',
    'capi-base-utils',
    'capi-base-utils-devel',
    'capi-system-info',
    'capi-system-info-devel',
    'capi-system-system-settings',
    'capi-system-system-settings-devel',
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
    'jsoncpp',
    'jsoncpp-devel',
    'libdlog',
    'libdlog-devel',
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
    'xdgmime',
    'xdgmime-devel',
    'wayland-extension-client-devel',
    'wayland-devel',
]

# Execute only if run as a script.
if __name__ != "__main__":
    exit(1)

if not shutil.which('rpm2cpio'):
    print('rpm2cpio is not installed. To install:\n'
          '  sudo apt install rpm2cpio')
    exit(1)
if not shutil.which('cpio'):
    print('cpio is not installed. To install:\n'
          '  sudo apt install cpio')
    exit(1)

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
parser.add_argument(
    '-b', '--base-repo', metavar='URL', type=str,
    help='url to the base packages repository',
    default='http://download.tizen.org/snapshots/tizen/5.5-base/latest/repos/standard/packages')
parser.add_argument(
    '-u', '--unified-repo', metavar='URL', type=str,
    help='url to the unified packages repository',
    default='http://download.tizen.org/snapshots/tizen/5.5-unified/latest/repos/standard/packages')
args = parser.parse_args()

if not args.output:
    args.output = args.arch
outpath = os.path.abspath(f'{__file__}/../{args.output}')

if args.clean:
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
    print(f'Undefined arch: {args.arch}')
    exit(1)

# Retrieve html documents.
documents = {}
for url in [f'{args.base_repo}/{archName}',
            f'{args.base_repo}/noarch',
            f'{args.unified_repo}/{archName}',
            f'{args.unified_repo}/noarch']:
    request = urllib.request.Request(url)
    with urllib.request.urlopen(request) as response:
        documents[url] = response.read().decode('utf-8')

# Download packages.
for package in basePackages + unifiedPackages:
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
        print(f'Could not find a package {package}')
    else:
        print(f'Downloading {url}...')
        urllib.request.urlretrieve(url, f'{downloadPath}/{match[0]}')

# Extract files.
for rpm in [f for f in os.listdir(downloadPath) if f.endswith('.rpm')]:
    abspath = f'{os.path.abspath(downloadPath)}/{rpm}'
    command = f'cd {outpath} && rpm2cpio {abspath} | cpio -idum --quiet'
    subprocess.run(command, shell=True, check=True)

# Create symbolic links. Any errors are ignored.
subprocess.run(f'ln -s asm-{args.arch} {outpath}/usr/include/asm', shell=True)
subprocess.run(f'ln -s libecore_input.so.1 {outpath}/usr/lib/libecore_input.so',
               shell=True)
if args.arch == 'arm64':
    subprocess.run(f'ln -s ../lib64/pkgconfig {outpath}/usr/lib/pkgconfig',
                   shell=True)

# Apply a patch if applicable.
patchFile = os.path.abspath(f'{__file__}/../{args.arch}.patch')
if os.path.exists(patchFile):
    command = f'git apply --directory sysroot/{args.output} {patchFile}'
    subprocess.run(command, shell=True, check=True)

print('Complete')
