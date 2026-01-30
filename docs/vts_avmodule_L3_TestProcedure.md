# VTS AV Module L3 Test Procedure

## Table of Contents

- [Acronyms, Terms and Abbreviations](#acronyms-terms-and-abbreviations)
- [Run L3 Tests Manually without Python](#run-l3-tests-manually-without-python)
- [Run L3 Tests using Python Automation](#run-l3-tests-using-python-automation)
  - [Setting Up Test Environment](#setting-up-test-environment)
  - [Test setup to run on VDevice](#test-setup-to-run-on-vdevice)
  - [Update Configuration Files](#update-configuration-files)
  - [Run on Windows Environment](#run-on-windows-environment)
  - [Run Test Cases](#run-test-cases)

## Acronyms, Terms and Abbreviations

- `HAL`    - Hardware Abstraction Layer
- `L3`     - Level 3 Testing
- `DUT`    - Device Under Test
- `RAFT`   - Rapid Automation Framework for Testing
- `YAML`   - YAML Ain't Markup Language

## Run L3 Tests Manually without Python

Refer [Running L3 Test Cases Manually](https://github.com/rdkcentral/rdk-halif-aidl-unified-vts/blob/develop/README.md#run-tests-manually)

## Run L3 Tests using Python Automation

### Setting Up Test Environment

To execute `HAL` `L3` Python test case, need a Python environment. Follow these steps mentioned in [Python Set up](https://github.com/rdkcentral/ut-raft/wiki/Guide-for-Setting-up-the-Python-RAFT-Testing-Suite) and [Raft Setup](https://github.com/rdkcentral/python_raft/?tab=readme-ov-file#installation)

### Test setup to run on vDevice

To validate test cases on a vDevice, first create a password for the `root` user by running the following command:

```bash
passwd root
```

After setting the password, update the same in the `vts_rack_config.yml` file.

**Note:** The Python paramiko library currently does not support empty passwords on a vDevice. Therefore, configuring a root password is required for test execution.

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
- Verify that the `download_path` is set to `assets/streams/input/` where the L3 streams are copied from the URL and used for test verification.
- Make sure the device profile exists in `profiles/<device profile>.yaml` and provide the `profile` path for it.
- Make sure to specify the correct `streams_download_url` to enable downloading streams for L3 test cases.

```yaml
deviceConfig:
    cpe1:
        platform:   "vDevice"
        model:      "UK"
        soc_vendor: "intel"
        target_directory: "/tmp/"
        prompt: "~#" # Prompt string on console
        download_path: "assets/streams/input/" #Download path where streams are saved inside the bin folder
        test:
            #TODO: Use the single profile file which contains all details (ds, hdmi, etc)
            profile: "../../../profiles/hfp-vdevice.yaml"
            streams_download_url: "<http stream path>" #URL path from which the streams are downloaded to the device

```

#### L3 Test Setup Configuration File

Example Test Setup configuration File: [vts_L3_test_setup.yaml](../host/tests/TestCases/vts_l3_test_setup.yaml)

The `yaml` file contain the list of AV Module L3 test_cases to execute.

Note : By default, all AV Module L3 test cases are added in the setup file.

To execute specific test cases, update the corresponding YAML file accordingly.

```yaml
VTS:
  description: "VTS L3 test setup"
  num_of_instances: 1
  test:
    artifacts:
      - "../../../build/vts_unified.tar.gz.bz"
    execute: "./run.sh"
    type: UT-C # C (UT-C Cunit) / C++ (UT-G (g++ ut-core gtest backend))
    suites:
      0:
        name: "VTS_L3_AudioDecoder"
        streams:
          - /Audio_Decoder/AAC_LC/Valid/tones_8k_2_64.aac
          - /Audio_Decoder/AAC_LC/Valid/tones_11.025k_2_64.aac
          - /Audio_Decoder/DOLBY_AC3/Invalid/tones_48k_2_192_random.ac3
          - /Audio_Decoder/DOLBY_AC3/Invalid/tones_48k_2_192_sync.ac3
        tests:
          - Decode_Sequential_NonTunnel_NonSecure
          - Decode_Sequential_NonTunnel_NonSecure_Error
          - Decode_Sequential_NonTunnel_NonSecure_Trim
          - Decode_Sequential_NonTunnel_NonSecure_Discontinuity
      1:
        name: "VTS_L3_AVBuffer"
        tests:
          - seq_nonsec_audiopool
          - seq_nonsec_audiopoolpcm
          - seq_nonsec_audiopool_alloc
          - seq_nonsec_audiopool_trim
```

#### Number of Instances

The `num_of_instances` field in the test setup configuration specifies how many parallel instances of the test should run at the same time.

- If set to `1`, the test runs in a single instance.
- If set to `2`, the framework will open two SSH connections to the DUT, run the HAL test binary in both instances, and execute the test cases in parallel.
- Increasing the number of instances can speed up overall execution time by leveraging parallel testing, provided the DUT and test environment support concurrent runs.

### Run on Windows Environment

To run the AVModule L3 tests in a Windows environment, follow these additional steps after checking out the repository and compiling the binaries:

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

#### To execute L3 Tests

The `vts_avmodules_l3_test.py` script executes the activated AV Module L3 tests as specified in the test_setup YAML file.

**Run Command:**

```bash
python3 host/tests/TestCases/vts_avmodules_l3_test.py --config </PATH>/host/tests/configs/vts_rack_config.yml --deviceConfig </PATH>/host/tests/configs/vts_deviceConfig.yml
```

#### To execute All Tests

The `vts_avmodules_all_tests.py` script executes all activated L1, L2, L3, and L4 tests.

**Run Command:**

```bash
python3 host/tests/TestCases/vts_avmodules_all_tests.py --config </PATH>/host/tests/configs/vts_rack_config.yml --deviceConfig </PATH>/host/tests/configs/vts_deviceConfig.yml
```
