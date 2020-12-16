# tizen_tools

Tizen cross-compilation toolchain for building the Flutter engine.

## How to generate toolchains

You need a Linux x64 host with [Tizen Studio](https://developer.tizen.org/development/tizen-studio/download) 4.0 or later installed. It is assumed that `tizen-studio` is installed in the default location (_HOME_), and the required package (_NativeToolchain-Gcc-9.2_) is already installed. Run the following commands in this directory to copy required files from `tizen-studio` to `toolchains`. Typically, you have to run this only once.

```sh
TIZEN_STUDIO=$HOME/tizen-studio

mkdir -p toolchains
cp -r $TIZEN_STUDIO/tools/llvm-10/* toolchains
cd toolchains/bin

# For arm
cp $TIZEN_STUDIO/tools/arm-linux-gnueabi-gcc-9.2/bin/arm-tizen-linux-gnueabi-gcc-9.2.0 .
for f in $TIZEN_STUDIO/tools/arm-linux-gnueabi-gcc-9.2/bin/arm-linux-*; do
  b=`basename $f`
  cp $f armv7l-tizen-${b:4:99}
done

# For x86
cp $TIZEN_STUDIO/tools/i586-linux-gnueabi-gcc-9.2/bin/i586-tizen-linux-gnueabi-gcc-9.2.0 .
for f in $TIZEN_STUDIO/tools/i586-linux-gnueabi-gcc-9.2/bin/i586-linux-*; do
  b=`basename $f`
  cp $f i586-tizen-${b:5:99}
done

cd ../lib
mkdir -p gcc
cp -r $TIZEN_STUDIO/tools/i586-linux-gnueabi-gcc-9.2/lib/gcc/i586-tizen-linux-gnueabi gcc
```

## How to generate sysroots

Run `build-rootfs.py` to generate sysroots for arm (device) and x86 (emulator).

```sh
cd sysroot

./build-rootfs.py --arch arm
./build-rootfs.py --arch x86

git apply *.patch
```

The sysroot should be re-generated if any dependencies are added by future updates (`git pull`).
