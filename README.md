# Unified Vendor Testing Suite For AIDL HAL

## Build Steps



### Setup

- To avoid conflict between your organization GitHub and RDK Central GitHub, add the following in your ssh config (`~/.ssh/config`):

<!-- -->

    Host rdkcentral-github.com
        IdentityFile <GitHub SSH key>

- The instruction to generate SSK key for GitHub:

  - <https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account>


### 1. Build linux binder

The test suite depends on the Linux binder with `AIDL` support. Follow these steps to build it:

For detail build instruction, please refer to [Linux Binder](https://github.com/rdk-e/linux_binder_idl/tree/main)

Here outline the simplest steps are

```bash
git clone -b develop 'ssh://git@github.com/rdk-e/linux_binder_idl.git'

cd linux_binder_idl

sc docker run vdevice-docker /bin/bash

./build-linux-binder-aidl.sh 64
```

### 2. Build Unified VTS

Clone and build the test suite:

```bash

git clone git@github.com:rdkcentral/rdk-halif-aidl-unified-vts.git`

```

Docker is required to build the test suite:

```bash
sc docker run vdevice-docker /bin/bash
```

Set below environment variable:

- AIDL_BIN: Path to the `AIDL` compiler (e.g., /path/to/linux_binder_idl/out/aidl).

- LINUX_BINDER_OUT_DIR: Path to the Linux binder output directory (e.g., /path/to/linux_binder_idl/local).

- UT_CORE_VERSION: Specific version of the UT-Core framework (e.g., 4.6.0). Defaults to the latest tagged version.

- RDK_HALIF_AIDL_VERSION: Specific version of the AIDL HALIF Specification (e.g, 0.7.1). Defaults to the latest HEAD.

Example:

```bash
export UT_CORE_VERSION=4.7.2
export RDK_HALIF_AIDL_VERSION=0.7.1
export AIDL_BIN=/path/linux_binder_idl/out/aidl
export LINUX_BINDER_OUT_DIR=/path//linux_binder_idl/local/
```

By default, UT logs are disabled. To enable them, Set below environment variable

```bash
export ENABLE_UT_INFO_LOGGING=1
```

Run the build script:

```bash
./build.sh all
```

The build.sh script:

- Clones the `rdk-halif-aidl` repository and UT-Core framework.

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

```bash
sudo ./run.sh -p profiles/hfp-vdevice.yaml
```
