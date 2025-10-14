# AV Module L4 Test Procedure

## Table of Contents

- [Acronyms, Terms and Abbreviations](#acronyms-terms-and-abbreviations)
- [Run L4 using python](#run-l4-using-python)
  - [Setting Up Test Environment](#setting-up-test-environment)
  - [Test setup on VDevice](#test-setup-on-vdevice)
  - [Update Configuration Files](#update-configuration-files)
  - [Run on Windows Environment](#run-on-windows-environment)
  - [Run Test Cases](#run-test-cases)

## Acronyms, Terms and Abbreviations

- `HAL`    - Hardware Abstraction Layer
- `L4`     - Level 4 Testing
- `DUT`    - Device Under Test
- `RAFT`   - Rapid Automation Framework for Testing
- `YAML`   - YAML Ain't Markup Language

## Run L4 using python

### Setting Up Test Environment

To execute `HAL` `L4` Python test case, need a Python environment. Follow these steps mentioned in [Python Set up](https://github.com/rdkcentral/ut-raft/wiki/Guide-for-Setting-up-the-Python-RAFT-Testing-Suite) and [Raft Setup](https://github.com/rdkcentral/python_raft/?tab=readme-ov-file#installation)

### Test setup on vDevice

To validate automation on vDevice, create a password for the root user using the following command:

```bash
passwd root
```

Then, update the set password in the File: [vts_rack_config.yml](../host/tests/configs/vts_rack_config.yml)

Note: Currently, the Python paramiko library does not support empty passwords on vDevice, so setting a password is necessary.

### Update Configuration Files

Example Rack Configuration File: [vts_rack_config.yml](../host/tests/configs/vts_rack_config.yml)

For more details refer [RAFT](https://github.com/rdkcentral/python_raft/blob/1.0.0/README.md) and [example_rack_config.yml](https://github.com/rdkcentral/python_raft/blob/1.0.0/examples/configs/example_rack_config.yml)

In this file, update the configuration to define the console sessions for the `DUT` and the outbound settings:

|Console Session|Description|
|---------------|-----------|
|default|Used by raft to download artifacts and streams|
|ssh_hal_test_0|Executes the `HAL` binary|
|ssh_player|Plays the stream required for test case|

```yaml
rackConfig:
  - dut:
      ip: "XXX.XXX.XXX.XXX"  # IP Address of the device
      description: "device under test"
      platform: "vDevice"
      consoles:
        - default:
            type: "ssh"
            port:
            username: "root"
            ip: "XXX.XXX.XXX" # IP address of the device
            password:
        - ssh_hal_test_0:
            type: "ssh"
            port:
            username: "root"
            ip: "XXX.XXX.XXX" # IP address of the device
            password:
        - ssh_player:
            type: "ssh"
            port:
            username: "root"
            ip: "XXX.XXX.XXX" #IP address of the device
            password:
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
- Specify the device profile path in `profiles/<device profile>.yaml`
- Ensure the `platform` should match with the `DUT` `platform` in vts_rack_config.yml
- Make sure that the `stream_download_URL` is specified correctly to enable downloading of streams for L4 test cases.
- Verify that the `download_path` is set to `assets/streams/input/`, where the streams are copied from the URL and used for L4 test verification.
- Can enable (1) or disable (0) `playback_manual_verification`:
    - When enabled (1) – AV playback verification requires manual (human) intervention.
    - When disabled (0) – AV playback is auto-verified as “Yes” without human intervention.

```yaml
deviceConfig:
    cpe1:
        platform:   "vDevice"
        model:      "UK"
        soc_vendor: "intel"
        target_directory: "/tmp/"
        prompt: "~#" # Prompt string on console
        download_path: "assets/streams/input/" #Download path where streams are saved inside the bin folder which will be used for L4 test
        playback_manual_verification: 1 # flag to enable AV playback verification manually if set to 1, if set to 0 it behaves as auto verification.
        test:
            #TODO: Use the single profile file which contains all details (ds, hdmi, etc)
            profile: "../../../profiles/hfp-vdevice.yaml"
            streams_download_url: "<http stream path>" #URL path from which the streams are downloaded to the device

```

#### Test Setup Configuration File

Example Test Setup configuration File: [vts_l4_setup.yaml](../host/tests/TestCases/vts_l4_setup.yaml)

This `yaml` contains the list of test_suites and test_cases to run.

```yaml
AVModule:
  description: "AVModule L4 setup"
  restart_required: False
  num_of_instances: 1
  test_suites: # List of L4
    #######################################
    # Entries to run individual test cases
    #######################################
    - name: "VTS_L4_AVMODULE"
      test_cases:
        - NormalPlay
        - playBackWithTrickModes
```

Note: By default, all AV L4 test cases are added in the setup file.

#### Test Configuration

Example Test Setup configuration File: [vts_l4_testConfig.yaml](../host/tests/TestCases/vts_l4_testConfig.yaml)

Execute command to run the HAL binary was provided in this file.

The created build/bin tar file name should be mentioned in the artifacts section so that it can be fetched by the RAFT automation.

```yaml
AVModule:
    description: "AVModule testing profile / menu system for UT"
    test:
        artifacts:
        #List of artifacts folders, test class copies the content of folder to the target device workspace
          - "../../../build/<tar name>.tar.gz"
        # exectute command, this will appended with the target device workspace path
        execute: "./run.sh"
        type: UT-C # C (UT-C Cunit) / C++ (UT-G (g++ ut-core gtest backend))
```

### Run on Windows Environment

To run the AVModule L4 tests in a Windows environment, follow these additional steps after checking out the repository and compiling the code:

1. Install the `raft` folder and Python Environment using install/activation scripts in `host` folder and make a tar of `build/bin`.

2. Move the entire project folder (including `host`) to your Windows machine preferably by making a tar.

3. Open the file located at `host/tests/raft/framework/plugins/ut_raft/interactive_shell.py`.

   - Comment out or remove the following import lines to avoid errors on Windows:

     ```python
     import pty
     import fcntl
     ```

4. After these changes, you can run the test cases using Python on your Windows system as usual.

### Run Test Cases

Once the environment is set up, you can execute the test cases with the following command

```bash
python </PATH>/host/tests/TestCases/vts_avmodules_l4_test.py --config </PATH>/host/tests/configs/vts_rack_config.yml --deviceConfig </PATH>/host/tests/configs/vts_deviceConfig.yml
