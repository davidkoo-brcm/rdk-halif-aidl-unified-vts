# Unified Vendor Testing Suite For AIDL HAL

This document outlines the steps to build and run the Unified Vendor Testing Suite (VTS) for AIDL HAL, targeting Linux or ARM platforms. The test suite depends on the Linux Binder with AIDL support and requires specific setup, build, and execution steps.

## Setup

### Configure SSH for GitHub

- To avoid conflict between your organization GitHub and RDK Central GitHub, add the following in your ssh config (`~/.ssh/config`):

<!-- -->

    Host github.code.rdkcentral.com
      Hostname github.com
      User
      IdentityFile ~/.ssh/

- The instruction to generate SSK key for GitHub:

  - <https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account>

## Build linux binder for Target Linux

The test suite depends on the Linux binder with `AIDL` support. Follow these steps to build it:

For detail build instruction, please refer to [Linux Binder](https://github.com/rdkcentral/linux_binder_idl)

Here outline the simplest steps are

```bash
git clone -b develop 'git@github.com:rdkcentral/linux_binder_idl.git'

cd linux_binder_idl

sc docker run vdevice-docker /bin/bash

./build-linux-binder-aidl.sh 64
```

**Use Prebuilt Linux Binder for ARM :**

## Build Unified VTS

### Clone the Repository

```bash
git clone git@github.code.rdkcentral.com:rdkcentral/rdk-halif-aidl-unified-vts.git
cd rdk-halif-aidl-unified-vts
```

### Set Up Docker Environment

**for Linux:**

```bash
sc docker run vdevice-docker /bin/bash
```

**for ARM:**

```bash
sc docker run rdk-kirkstone /bin/bash
source /opt/toolchains/rdk-glibc-x86_64-arm-toolchain/environment-setup-armv7vet2hf-neon-oe-linux-gnueabi
```

Set below environment variable:

- AIDL_BIN: Path to the `AIDL` compiler (e.g., /path/to/linux_binder_idl/out/aidl).

- LINUX_BINDER_OUT_DIR: Path to the Linux binder output directory (e.g., /path/to/linux_binder_idl/local).

- UT_CORE_VERSION: Specific version of the UT-Core framework (e.g., 4.6.0). Defaults to the latest tagged version.

- RDK_HALIF_AIDL_VERSION: Specific version of the AIDL HALIF Specification (e.g, 0.7.1). Defaults to the latest HEAD.

- EGL_PATH: Specific Path for EGL libraries.

- Ensure that the pre-built GStreamer libraries are placed in the `build/usr/` directory before compiling the L4 test cases.

Example:

```bash
export UT_CORE_VERSION=4.7.3
export RDK_HALIF_AIDL_VERSION=0.7.1
export AIDL_BIN=/path/linux_binder_idl/out/aidl
export LINUX_BINDER_OUT_DIR=/path/linux_binder_idl/local/
export EGL_PATH=/path/egl_libraries/
```

By default, UT logs are disabled. To enable them, Set below environment variable

```bash
export ENABLE_UT_INFO_LOGGING=1
```

Run the build script for Target ARM:

```bash
sc docker run rdk-kirkstone /bin/bash
./build.sh Target=arm
```

Run the build script for Target Linux:

```bash
sc docker run vdevice-docker /bin/bash
./build.sh Target=linux
```

The build.sh script:

- Clones the `rdk-halif-aidl` repository, Vendor test modules and UT-Core framework.

- Compiles the test suite.

- Generates binaries in the `build/bin` directory.

## Run test

- Package the Binaries:

```bash
cd build
tar -zcf unified_vts.tar.gz bin
```

- Transfer to Target Device:

Copy the tarball to the target device (e.g., using scp):

```bash
scp unified_vts.tar.gz root@target-device:/home/root/

```

- Extract on Target Device:

Log into the target device and extract the tarball:

```bash
ssh root@target-device
cd /home/root
tar -zxf unified_vts.tar.gz
cd bin
```

- Run the Test:
Execute the run.sh script as root:
Please use platform specific profile

```bash
sudo ./run.sh -p profiles/hfp-vdevice.yaml
```

## Setting Python environment for L1, L2, L3 and L4 automation test cases

- For running the L1, L2, L3 and L4 test suite, a host PC with a Python environment is required.
- Install Python Environment and Activation Scripts as detailed in [Python Installation](https://github.com/rdkcentral/ut-raft/wiki/Guide-for-Setting-up-the-Python-RAFT-Testing-Suite)

## Running L1, L2 and L3 automation test cases

- To run the `L1`, `L2` and `L3` test cases of AV Modules follow the `L1` `L2` and `L3` Test Procedure document - [vts_avmodule_L1_L2_L3_TestProcedure.md](docs/vts_avmodule_L1_L2_L3_TestProcedure.md)

## Running L4 automation test cases

- To run the `L4` test cases of AV Modules follow the `L4` Test Procedure document - [vts_avmodule_L4_TestProcedure.md](docs/vts_avmodule_L4_TestProcedure.md)
