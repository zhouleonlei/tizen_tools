FROM ubuntu:latest
MAINTAINER Swift Kim <swift.kim@samsung.com>

# Install packages required by Tizen Studio/build-rootfs/gn.
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update
RUN apt install -y wget pciutils zip libncurses5 python libpython2.7
RUN apt install -y git python3 rpm2cpio cpio
RUN apt install -y pkg-config libfreetype6-dev
RUN apt clean

# Only non-root users can install Tizen Studio.
RUN useradd -ms /bin/bash user
USER user
WORKDIR /home/user

# Install Tizen Studio.
ENV TIZEN_STUDIO=/home/user/tizen-studio
RUN wget -O install.bin http://download.tizen.org/sdk/Installer/tizen-studio_4.0/web-cli_Tizen_Studio_4.0_ubuntu-64.bin
RUN chmod a+x install.bin
RUN ./install.bin --accept-license $TIZEN_STUDIO
RUN $TIZEN_STUDIO/package-manager/package-manager-cli.bin install NativeToolchain-Gcc-9.2

USER root
ENV TIZEN_TOOLS=/tizen_tools
WORKDIR $TIZEN_TOOLS

# Copy toolchains.
SHELL ["/bin/bash", "-c"]
RUN cp -r $TIZEN_STUDIO/tools/llvm-10 toolchains
RUN cp $TIZEN_STUDIO/tools/arm-linux-gnueabi-gcc-9.2/bin/arm-tizen-linux-gnueabi-gcc-9.2.0 toolchains/bin
RUN for f in $TIZEN_STUDIO/tools/arm-linux-gnueabi-gcc-9.2/bin/arm-linux-*; do \
      b=$(basename $f); \
      cp $f toolchains/bin/armv7l-tizen-${b:4:99}; \
    done
RUN cp $TIZEN_STUDIO/tools/i586-linux-gnueabi-gcc-9.2/bin/i586-tizen-linux-gnueabi-gcc-9.2.0 toolchains/bin
RUN for f in $TIZEN_STUDIO/tools/i586-linux-gnueabi-gcc-9.2/bin/i586-linux-*; do \
      b=$(basename $f); \
      cp $f toolchains/bin/i586-tizen-${b:5:99}; \
    done
RUN mkdir -p lib/gcc
RUN cp -r $TIZEN_STUDIO/tools/i586-linux-gnueabi-gcc-9.2/lib/gcc/i586-tizen-linux-gnueabi lib/gcc

# Remove Tizen Studio and clean up.
RUN userdel -r user

# Construct sysroots.
COPY sysroot/build-rootfs.py sysroot/
COPY sysroot/*.patch sysroot/
RUN sysroot/build-rootfs.py -a arm -o sysroot/arm
RUN sysroot/build-rootfs.py -a x86 -o sysroot/x86
RUN git apply sysroot/*.patch

ENV ENGINE=/engine
WORKDIR $ENGINE

# Install depot_tools and sync dependencies.
RUN git clone --depth=1 https://chromium.googlesource.com/chromium/tools/depot_tools.git
ENV PATH=$PATH:$ENGINE/depot_tools
RUN gclient config --name="src/flutter" --deps-file="DEPS" --unmanaged https://github.com/flutter-tizen/engine.git
RUN gclient sync

# Disable unsupported build flags.
RUN sed -i 's/"-Wno-non-c-typedef-for-linkage",//g' src/build/config/compiler/BUILD.gn
