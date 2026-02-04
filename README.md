# Unified Vendor Testing Suite For AIDL HAL

This document outlines the steps to build and run the Unified Vendor Testing Suite (VTS) for AIDL HAL, targeting Linux or ARM platforms. The test suite depends on the Linux Binder with AIDL support and requires specific setup, build, and execution steps.

## Table of Contents

- [Unified Vendor Testing Suite For AIDL HAL](#unified-vendor-testing-suite-for-aidl-hal)
  - [Acronyms, Terms and Abbreviations](#acronyms-terms-and-abbreviations)
  - [Setup](#setup)
  - [Build linux binder for Target Linux](#build-linux-binder-for-target-linux)
  - [Build Unified VTS](#build-unified-vts)
  - [Run Tests Manually](#run-tests-manually)
  - [Setting Python environment for L1, L2, L3 and L4 automation test cases](#setting-python-environment-for-l1-l2-l3-and-l4-automation-test-cases)
  - [Running L1, L2, L3 and L4 Automation test cases](#running-l1-l2-l3-and-l4-automation-test-cases)
  - [AV Module Components](#av-module-components)

## Acronyms, Terms and Abbreviations

| Acronym / Term | Description |
|----------------|-------------|
| **AIDL** | Android Interface Definition Language |
| **HAL** | Hardware Abstraction Layer |
| **L1** | Level 1 Test Cases (Interface / basic validation tests) |
| **L2** | Level 2 Test Cases (Functional tests) |
| **L3** | Level 3 Test Cases (Integration tests) |
| **L4** | Level 4 Test Cases (End-to-End / System tests) |
| **RDK** | Reference Design Kit |
| **UT-Core** | RDK Unified Test Core Framework |
| **VTS** | Vendor Test Suite |
| **YAML** | Yet Another Markup Language (configuration format) |

## Setup

### Configure SSH for GitHub

- To avoid conflict between your organization GitHub and RDK Central GitHub, add the following in your ssh config (`~/.ssh/config`):

<!-- -->

    Host github.code.rdkcentral.com
      Hostname github.com
      User
      IdentityFile ~/.ssh/

- The instruction to generate SSH key for GitHub:

  - <https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account>

- You may face issue with repo init as repo-tool gets downloaded from different path
  - For SKY users, follow <https://skyswteam.com/-/user_settings/ssh_keys>

## Build linux binder for Target Linux

The test suite depends on the Linux binder with `AIDL` support. Follow these steps to build it:

For detail build instruction, please refer to [Linux Binder](https://github.com/rdkcentral/linux_binder_idl/tree/1.0.0)

Here outline the simplest steps are

```bash
git clone -b 1.0.0 'git@github.com:rdkcentral/linux_binder_idl.git'

cd linux_binder_idl

# for Linux:
sc docker run vdevice-docker /bin/bash

# for ARM:
sc docker run rdk-kirkstone /bin/bash

./build-linux-binder-aidl.sh 64
```

**Note:** **Use Prebuilt Linux Binder for ARM**

For more information about RDK Docker Toolchain, please check [RDK Docker Toolchain](https://github.com/rdkcentral/ut-core/wiki/FAQ:-RDK-Docker-Toolchain)

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

- RDK_VCOMPONENT_`<NON-AV-MODULE>` : Specific version of vcomponent module (eg, 0.1.0). Defaults to main.

- EGL_LIB_PATH: Specific Path for EGL libraries.

- GST_LIB_PATH: Path to the pre-built GStreamer libraries used for compiling the L4 test cases.

Example:

```bash
export UT_CORE_VERSION=4.7.3
export RDK_HALIF_AIDL_VERSION=0.12.0
export AIDL_BIN=/path/linux_binder_idl/out/aidl
export LINUX_BINDER_OUT_DIR=/path/linux_binder_idl/local/
export EGL_LIB_PATH=/path/egl_libraries/
export GST_LIB_PATH=/path/gstreamer_lib/
export RDK_VCOMPONENT_CEC=0.1.0
```

By default, UT logs are disabled. To enable them, Set below environment variable

```bash
export ENABLE_UT_INFO_LOGGING=1
```

Run the build script for Target ARM:

```bash
./build.sh Target=arm
```

Run the build script for Target Linux:

```bash
./build.sh Target=linux
```

The build.sh script:

- Clones the `rdk-halif-aidl` repository, Vendor test modules, vcomponent for non-av modules and UT-Core framework.

- Compiles the test suite.

- Generates binaries and packages the binaries in the `build/vts_unified.tar.gz.bz` directory.

## Run Tests Manually

- In order to run the test cases manually on target device:

Copy the tarball `build/vts_unified.tar.gz.bz` to the target device (e.g., using scp):

```bash
scp build/vts_unified.tar.gz.bz root@target-device:/home/root/

```

- Extract on Target Device:

Log into the target device and extract the tarball:

```bash
ssh root@target-device
cd /home/root
tar -zxf vts_unified.tar.gz.bz
cd bin
```

- Run the Test:

Execute the run.sh script as root by using the platform specific profile.

```bash
sudo ./run.sh -p profiles/hfp-vdevice.yaml
```

**Note:** For running the AV Module L3, L4 test cases manually make sure the test streams are copied into `bin/assets/streams/input` folder on target device.

## Setting Python environment for L1, L2, L3 and L4 automation test cases

- For running the L1, L2, L3 and L4 test suite, a host PC with a Python environment is required.
- Install Python Environment and Activation Scripts as detailed in [Python Installation](https://github.com/rdkcentral/ut-raft/wiki/Guide-for-Setting-up-the-Python-RAFT-Testing-Suite)

## Running L1 and L2 automation test cases

- To run the `L1` and `L2` test cases, follow the `L1` and `L2` Test Procedure document - [vts_L1_L2_TestProcedure.md](docs/vts_L1_L2_TestProcedure.md)

## Running L3 automation test cases

- To run the AV Module `L3` test cases follow the `L3` Test Procedure document - [vts_avmodule_L3_TestProcedure.md](docs/vts_avmodule_L3_TestProcedure.md)

- To run the non av `L3` test cases, follow the `non av L3` Test Procedure document - [vts_nonav_L3_TestProcedure.md](docs/vts_nonav_L3_TestProcedure.md)

## Running L4 Automation test cases

- To run the AV  Module `L4` test cases follow the `L4` Test Procedure document - [vts_avmodule_L4_TestProcedure.md](docs/vts_avmodule_L4_TestProcedure.md)

## Components list

Each individual component and their respective test repositories are listed below:

| #| Component Name | Repositories |
| -| ---------------| -------------|
| 1|AV Buffer       |[Test Repo](https://github.com/rdkcentral/rdk-halif-aidl-test-avbuffer)|
| 2|Audio Decoder   |[Test Repo](https://github.com/rdkcentral/rdk-halif-aidl-test-audiodecoder)|
| 3|Audio Sink      |[Test Repo](https://github.com/rdkcentral/rdk-halif-aidl-test-audiosink)|
| 4|Video Decoder   |[Test Repo](https://github.com/rdkcentral/rdk-halif-aidl-test-videodecoder)|
| 5|Video Sink      |[Test Repo](https://github.com/rdkcentral/rdk-halif-aidl-test-videosink)|
| 6|AV Clock        |[Test Repo](https://github.com/rdkcentral/rdk-halif-aidl-test-avclock)|
| 7|Plane Control   |[Test Repo](https://github.com/rdkcentral/rdk-halif-aidl-test-planecontrol)|
| 8|Hdmi Cec        |[Test Repo](https://github.com/rdkcentral/rdk-halif-aidl-test-cec)|
