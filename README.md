# tizen_tools

Tizen cross-compilation toolchain for building the Flutter engine.

## Generating toolchains

You need a Linux x64 host with [Tizen Studio](https://developer.tizen.org/development/tizen-studio/download) 4.0 or later installed. It is assumed that `tizen-studio` is installed in the default location (_HOME_), and the required package (_NativeToolchain-Gcc-9.2_) is already installed. Run the following commands in this directory to copy required files from `tizen-studio` to `toolchains`. Typically, you have to run this only once.

```sh
TIZEN_STUDIO=$HOME/tizen-studio

mkdir -p toolchains
cp -r $TIZEN_STUDIO/tools/llvm-10/* toolchains
```

<details open>
<summary>For arm</summary><p>

```sh
for f in $TIZEN_STUDIO/tools/arm-linux-gnueabi-gcc-9.2/bin/arm-linux-*; do
  b=`basename $f`
  cp $f toolchains/bin/armv7l-tizen-${b:4}
done
```

</details>

<details>
<summary>For arm64 (optional)</summary><p>

Make sure you already have created a sysroot for arm64 (below) before running the following.

```sh
for f in $TIZEN_STUDIO/tools/aarch64-linux-gnu-gcc-9.2/bin/aarch64-linux-*; do
  b=`basename $f`
  cp $f toolchains/bin/aarch64-tizen-${b:8}
done

# FIXME: https://github.com/flutter-tizen/tizen_tools/pull/7#discussion_r611339789
ln -s aarch64-tizen-linux-gnu-ld toolchains/bin/ld

# FIXME: This should not be necessary.
cp -r $TIZEN_STUDIO/tools/aarch64-linux-gnu-gcc-9.2/lib/gcc/aarch64-tizen-linux-gnu/9.2.0/*.{o,a} \
  sysroot/arm64/usr/lib
```

</details>

<details>
<summary>For x86 (optional)</summary><p>

```sh
for f in $TIZEN_STUDIO/tools/i586-linux-gnueabi-gcc-9.2/bin/i586-linux-*; do
  b=`basename $f`
  cp $f toolchains/bin/i586-tizen-${b:5}
done

# FIXME: This should not be necessary.
mkdir -p toolchains/lib/gcc
cp -r $TIZEN_STUDIO/tools/i586-linux-gnueabi-gcc-9.2/lib/gcc/i586-tizen-linux-gnueabi \
  toolchains/lib/gcc
```

</details>

## Generating a sysroot

Run `build-rootfs.py` to generate a sysroot for each target architecture. You have to re-generate the sysroot whenever this repo has been updated.

<details open>
<summary>For arm (Tizen 5.5+)</summary><p>

```sh
sysroot/build-rootfs.py --arch arm
```

</details>

<details>
<summary>For different architectures (optional)</summary><p>

```sh
# For arm64 (Tizen 5.5+)
sysroot/build-rootfs.py --arch arm64

# For x86 (Tizen 5.5+)
sysroot/build-rootfs.py --arch x86

# For arm (Tizen 4.0)
sysroot/build-rootfs.py --arch arm \
--base-repo http://download.tizen.org/snapshots/tizen/4.0-base/latest/repos/arm/packages \
--unified-repo http://download.tizen.org/snapshots/tizen/4.0-unified/latest/repos/standard/packages \
--output arm_40

# For x86 (Tizen 4.0)
sysroot/build-rootfs.py --arch x86 \
--base-repo http://download.tizen.org/snapshots/tizen/4.0-base/latest/repos/emulator32/packages \
--unified-repo http://download.tizen.org/snapshots/tizen/4.0-unified/latest/repos/standard/packages \
--output x86_40
```

</details>
