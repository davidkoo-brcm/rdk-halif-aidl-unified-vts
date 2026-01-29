# VTS AV Module L4 Test Procedure

## Table of Contents

- [Acronyms, Terms and Abbreviations](#acronyms-terms-and-abbreviations)
- [Run L4 Tests Manually without Python](#run-l4-tests-manually-without-python)
- [Run L4 Tests using Python Automation](#run-l4-tests-using-python-automation)
  - [Setting Up Test Environment](#setting-up-test-environment)
  - [Test setup to run on VDevice](#test-setup-to-run-on-vdevice)
  - [Update Configuration Files](#update-configuration-files)
  - [Run on Windows Environment](#run-on-windows-environment)
  - [Run Test Cases](#run-test-cases)

## Acronyms, Terms and Abbreviations

- `HAL`    - Hardware Abstraction Layer
- `L4`     - Level 4 Testing
- `DUT`    - Device Under Test
- `RAFT`   - Rapid Automation Framework for Testing
- `YAML`   - YAML Ain't Markup Language

## Run L4 Tests Manually without Python

Refer [Running L4 Tests Manually](https://github.com/rdkcentral/rdk-halif-aidl-unified-vts/blob/develop/README.md#run-tests-manually)

## Run L4 Tests using Python Automation

### Setting Up Test Environment

To execute `HAL` `L4` Python test case, need a Python environment. Follow these steps mentioned in [Python Set up](https://github.com/rdkcentral/ut-raft/wiki/Guide-for-Setting-up-the-Python-RAFT-Testing-Suite) and [Raft Setup](https://github.com/rdkcentral/python_raft/?tab=readme-ov-file#installation)

### Test setup to run on vDevice

To validate Test cases on vDevice, create a password for the root user using the following command:

```bash
passwd root

```

Then, update the same password in the vts_rack_config.yml file.

Note: Currently, the Python paramiko library does not support empty passwords on vDevice, so setting a password is necessary.

### Update Configuration Files

#### Rack Configuration File

Example Rack Configuration File: [vts_rack_config.yml](../host/tests/configs/vts_rack_config.yml)

For more details refer [RAFT](https://github.com/rdkcentral/python_raft/blob/1.0.0/README.md) and [example_rack_config.yml](https://github.com/rdkcentral/python_raft/blob/1.0.0/examples/configs/example_rack_config.yml)

In this file, update the configuration to define the console sessions for the `DUT` and the outbound settings:

|Console Session|Description|
|---------------|-----------|
|default|Used by raft to download artifacts|
|ssh_hal_test_0|To run the first instance `HAL` binary|
|ssh_hal_test_N|To run the (N-1) instance `HAL` binary|
|ssh_player|Plays the stream required for test case|

```yaml
rackConfig:
  rack1:
    slot1:
      devices:
        - dut:
            ip: "XXX.XXX.XXX.XXX"  # IP Address of the device
            description: "Device under test"
            platform: "vDevice"
            consoles:
              - default:
                  type: "ssh"
                  port: "30033"
                  username: "root"
                  ip: "XXX.XXX.XXX" # IP address of the device
                  password: ""
              #For multiple instance tests, corresponding SSH configs are used, single instance uses 0th ssh config.
              - ssh_hal_test_0:
                  type: "ssh"
                  port: "30033"
                  username: "root"
                  ip: "XXX.XXX.XXX" # IP address of the device
                  password: ""
              - ssh_hal_test_1:
                  type: "ssh"
                  port: "30033"
                  username: "root"
                  ip: "XXX.XXX.XXX" # IP address of the device
                  password: ""
              - ssh_player:
                  type: "ssh"
                  port: "30033"
                  username: "root"
                  ip: "XXX.XXX.XXX" # IP address of the device
                  password: ""
            outbound:
              download_url: "http://localhost:8000/"    # download location for the CPE device
              httpProxy:   # Local Proxy if required
              workspaceDirectory: './logs/workspace'   # Local working directory
```

#### Device Configuration File

Example Device configuration File: [vts_deviceConfig.yml](../host/tests/configs/vts_deviceConfig.yml)

For more details refer [RAFT](https://github.com/rdkcentral/python_raft/blob/1.0.0/README.md) and [example_device_config.yml](https://github.com/rdkcentral/python_raft/blob/1.0.0/examples/configs/example_device_config.yml)

Update below fields in the device configuration file:

- Set the path for `target_directory` where `HAL` binaries will be copied onto the device.
- Ensure the `platform` name should match with the `DUT` `platform` in vts_rack_config.yml
- Choose the appropriate `soc_vendor` for the `DUT` listed in `host/tests/raft/framework/plugins/ut_raft/configs/utPlayerConfig.yml` to ensure feasible GStreamer playback.
- Verify that the `download_path` is set to `assets/streams/input/` where the L4 streams are copied from the URL and used for test verification.
- `playback_manual_verification` can be enable (1) or disable (0) :
  - When enabled (1) – L4 AV playback verification requires manual (human) intervention.
  - When disabled (0) – L4 AV playback is auto-verified as “Yes” without human intervention.
- Make sure the device profile exists in `profiles/<device profile>.yaml` and provide the `profile` path for it.
- Make sure to specify the correct `streams_download_url` to enable downloading streams for L4 test cases.

```yaml
deviceConfig:
    cpe1:
        platform:   "vDevice"
        model:      "UK"
        soc_vendor: "intel"
        target_directory: "/tmp/"
        prompt: "~#" # Prompt string on console
        download_path: "assets/streams/input/" #Download path where streams are saved inside the bin folder
        playback_manual_verification: 0 # flag to enable manual playback verification
        test:
            #TODO: Use the single profile file which contains all details (ds, hdmi, etc)
            profile: "../../../profiles/hfp-vdevice.yaml"
            streams_download_url: "<http stream path>" #URL path from which the streams are downloaded to the device

```

#### L4 Test Setup Configuration File

Example Test Setup configuration File: [vts_L4_test_setup.yaml](../host/tests/TestCases/vts_l4_test_setup.yaml)

The `yaml` file contain the list of AV Module L4 test_cases to execute.

Note : By default, all AV module L4 test cases are added in the setup file.

To execute specific test cases, update the corresponding YAML files accordingly.

```yaml
VTS:
  description: "VTS L4 test setup"
  num_of_instances: 1
  test:
    artifacts:
      - "../../../build/vts_unified.tar.gz.bz"
    execute: "./run.sh"
    type: UT-C # C (UT-C Cunit) / C++ (UT-G (g++ ut-core gtest backend))
    suites:
      0:
        name: "VTS_L4_AVMODULE"
        tests:
          - NormalPlay
          - playBackWithTrickModes

```

#### Number of Instances

The `num_of_instances` field in the test setup configuration specifies how many parallel instances of the test should run at the same time.

- If set to `1`, the test runs in a single instance.
- If set to `2`, the framework will open two SSH connections to the DUT, run the HAL test binary in both instances, and execute the test cases in parallel.
- Increasing the number of instances can speed up overall execution time by leveraging parallel testing, provided the DUT and test environment support concurrent runs.

#### L4 Test info Configuration file

Example Test info configuration File: [vts_L4_test_info.yaml](../host/tests/TestCases/vts_l4_test_info.yaml)

This `YAML` file includes the list of activated L4 stream configuration files located in the `host/tests/TestCases/streams_config` directory, which are used to execute tests and verify playback status.

To verify specific L4 streams playback, update the corresponding YAML files accordingly.

```yaml
AVModule:
  input_streams_path: "assets/streams/input" # Target path where input streams are stored
  player: "gstreamer"

  # Explicit include_N ordering retained per runner expectations
  include_0: streams_config/H265_config.yaml
  include_1: streams_config/AC3_config.yaml
  include_2: streams_config/VP9_Opus_config.yaml
  include_3: streams_config/AV1_config.yaml
```

### Run on Windows Environment

To run the AVModule L4 tests in a Windows environment, follow these additional steps after checking out the repository and compiling the binaries:

1. Install the python env as usual in your Linux environment using the script (host/install.sh).

2. Move the entire project folder (including `host`) to your Windows machine where python is installed.

3. If running through VS code then ensure Git Bash is installed on your system (Required to run shell scripts such as install.sh and activate_venv.sh.) and choose Git Bash as the terminal type.

4. Open the file located at `host/tests/raft/framework/plugins/ut_raft/interactive_shell.py`.

   - Comment out or remove the following import lines to avoid errors on Windows:

     ```python
     import pty
     import fcntl
     ```

5. Make sure the config files (rack and device configs) are updated.

6. After making the changes, Activate the virtual environment (source host/activate_venv.sh) and run the test cases using Python on your Windows system as usual.

### Run Test Cases

Once the environment is set up, can able to execute the test cases with the following command:

#### To execute L4 Tests

The `vts_avmodules_l4_test.py` script executes L4 tests to verify AV playback for the activated stream configuration files.

**Run Command:**

```bash
python3 host/tests/TestCases/vts_avmodules_l4_test.py --config </PATH>/host/tests/configs/vts_rack_config.yml --deviceConfig </PATH>/host/tests/configs/vts_deviceConfig.yml
```

#### To execute All Tests

The `vts_avmodules_all_tests.py` script executes all activated L1, L2, L3, and L4 tests.

**Run Command:**

```bash
python3 host/tests/TestCases/vts_avmodules_all_tests.py --config </PATH>/host/tests/configs/vts_rack_config.yml --deviceConfig </PATH>/host/tests/configs/vts_deviceConfig.yml
```
