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

For more information about RDK Docker Toolchain, please check [RDK Docker Toolchain](https://github.com/rdkcentral/ut-core/wiki/FAQ:-RDK-Docker-Toolchain)

Set below environment variable:

- AIDL_BIN: Path to the `AIDL` compiler (e.g., /path/to/linux_binder_idl/out/aidl).

- LINUX_BINDER_OUT_DIR: Path to the Linux binder output directory (e.g., /path/to/linux_binder_idl/local).

- UT_CORE_VERSION: Specific version of the UT-Core framework (e.g., 4.7.3). Defaults to the latest tagged version.

- RDK_HALIF_AIDL_VERSION: Specific version of the AIDL HALIF Specification (e.g, 0.12.0). Defaults to the latest HEAD.

- GST_LIB_PATH: Path to the pre-built GStreamer libraries used for compiling the L4 test cases.

Example:

```bash
export UT_CORE_VERSION=4.7.3
export RDK_HALIF_AIDL_VERSION=0.12.0
export AIDL_BIN=/path/linux_binder_idl/out/aidl
export LINUX_BINDER_OUT_DIR=/path/linux_binder_idl/local/
export GST_LIB_PATH=/path/gstreamer_lib/
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

- Generates binaries and packages the binaries in the `build/vts_unified.tar.gz.bz` directory.

## Run test

- Transfer to Target Device:

Copy the tarball to the target device (e.g., using scp):

```bash
scp vts_unified.tar.gz root@target-device:/home/root/

```

- Extract on Target Device:

Log into the target device and extract the tarball:

```bash
ssh root@target-device
cd /home/root
tar -zxf vts_unified.tar.gz
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
