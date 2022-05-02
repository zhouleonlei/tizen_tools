###############################
### Stage for building LLVM ###
###############################

FROM ubuntu:20.04 AS llvm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y git zip build-essential cmake ninja-build clang-11 && \
    apt-get clean

COPY build-llvm.sh .

RUN /build-llvm.sh


######################################
### Stage for constructing sysroot ###
######################################

FROM ubuntu:20.04 AS sysroot

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y python3 rpm2cpio cpio git && \
    apt-get clean

COPY sysroot/build-rootfs.py /sysroot/
COPY sysroot/*.patch /sysroot/

RUN /sysroot/build-rootfs.py --arch arm
RUN /sysroot/build-rootfs.py --arch arm64
RUN /sysroot/build-rootfs.py --arch x86

# Remove cached packages.
RUN rm -r /sysroot/*/.rpms


##############################
### Create a release image ###
##############################

FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y binutils-arm-linux-gnueabi binutils-aarch64-linux-gnu binutils-i686-linux-gnu && \
    apt-get clean

# Copy build results from previous stages.
COPY --from=llvm /toolchains/ /tizen_tools/toolchains/
COPY --from=sysroot /sysroot/ /tizen_tools/sysroot/
