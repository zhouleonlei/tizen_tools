# tizen_tools

Tizen cross-compilation toolchain for building the Flutter engine.

## Installing the toolchain

You need a Linux x64 host to build the Flutter engine for Tizen devices.

### Building the toolchain from source (recommended)

Run the following commands to build LLVM 15 from source.

```sh
# Install prerequisites for build. We use ninja and clang-11 for the build.
sudo apt update
sudo apt install git zip build-essential cmake ninja-build clang-11

# Run the build script.
./build-llvm.sh

# Install extra packages required by the linker.
sudo apt install binutils-arm-linux-gnueabi binutils-aarch64-linux-gnu binutils-i686-linux-gnu
```

### Using Tizen Studio's built-in toolchain (deprecated)

Run the following commands in this directory. We assume that [Tizen Studio](https://developer.tizen.org/development/tizen-studio/download) is already installed to the default location (_$HOME_) on your local drive. The required package (_NativeToolchain-Gcc-9.2_) must also be installed.

<details><p>

```sh
rm -rf toolchains && mkdir -p toolchains
cp -r ~/tizen-studio/tools/llvm-10/* toolchains

# For arm.
cp ~/tizen-studio/tools/arm-linux-gnueabi-gcc-9.2/bin/arm-linux-gnueabi-* toolchains/bin

# For arm64.
cp ~/tizen-studio/tools/aarch64-linux-gnu-gcc-9.2/bin/aarch64-linux-gnu-* toolchains/bin

# For x86.
for f in ~/tizen-studio/tools/i586-linux-gnueabi-gcc-9.2/bin/i586-linux-gnueabi-*; do
  b=`basename $f`
  cp $f toolchains/bin/i686-linux-gnu-${b:19}
done
```

The toolchain shipped with Tizen Studio (LLVM 10) is pretty old. You need to disable the following unsupported compile options (or more in the future) before running the engine build.

```patch
--- a/build/config/compiler/BUILD.gn
+++ b/build/config/compiler/BUILD.gn
@@ -617,17 +617,13 @@ if (is_win) {

  if (!use_xcode) {
    default_warning_flags += [
-      "-Wno-unused-but-set-parameter",
-      "-Wno-unused-but-set-variable",
      "-Wno-implicit-int-float-conversion",
      "-Wno-c99-designator",
      "-Wno-deprecated-copy",
      # Needed for compiling Skia with clang-12
-      "-Wno-psabi",
    ]
    if (!is_fuchsia) {
      default_warning_flags += [
-        "-Wno-non-c-typedef-for-linkage",
        "-Wno-range-loop-construct",
      ]
    }
```

</details>

## Constructing a sysroot

Run `build-rootfs.py` to generate a sysroot for each target architecture. You have to re-run the command whenever this repo is updated.

```sh
# For arm.
sysroot/build-rootfs.py --arch arm

# For arm64.
sysroot/build-rootfs.py --arch arm64

# For x86.
sysroot/build-rootfs.py --arch x86
```
