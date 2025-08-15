# AVModule L1, L2 and L3 Test Procedure

## Table of Contents
- [Acronyms, Terms and Abbreviations](#acronyms-terms-and-abbreviations)
- [Run L1 L2 and L3 Test directly without python](#run-l1-l2-and-l3-test-directly-without-python)
- [Run L1 L2 and L3 using python](#run-l1-l2-and-l3-using-python)
  - [Setting Up Test Environment](#setting-up-test-environment)
  - [Test setup on VDevice](#test-setup-on-vdevice)
  - [Update Configuration Files](#update-configuration-files)
  - [Run on Windows Environment](#run-on-windows-environment)
  - [Run Test Cases](#run-test-cases)

## Acronyms, Terms and Abbreviations

- `HAL`    - Hardware Abstraction Layer
- `L1`     - Level 1 Testing
- `L2`     - Level 2 Testing
- `L3`     - Level 3 Testing
- `DUT`    - Device Under Test
- `RAFT`   - Rapid Automation Framework for Testing
- `YAML`   - YAML Ain't Markup Language


## Run L1 L2 and L3 Test directly (without python)

Refer [Running L1 L2 and L3 Test suites](https://github.com/rdkcentral/rdk-halif-aidl-unified-vts/blob/develop/README.md#run-test)

## Run L1 L2 and L3 using python

### Setting Up Test Environment

To execute `HAL` `L1` `L2` and `L3` Python test case, need a Python environment. Follow these steps mentioned in [Python Set up](https://github.com/rdkcentral/ut-raft/wiki/Guide-for-Setting-up-the-Python-RAFT-Testing-Suite) and [Raft Setup](https://github.com/rdkcentral/python_raft/?tab=readme-ov-file#installation)

### Test setup on vDevice

To validate automation on vDevice, create a password for the root user using the following command:

```bash
passwd root

```

Then, update the same password in the vts_rack_config.yml file.

Note: Currently, the Python paramiko library does not support empty passwords on vDevice, so setting a password is necessary

### Update Configuration Files

Example Rack Configuration File: [vts_rack_config.yml](../host/tests/configs/vts_rack_config.yml)

For more details refer [RAFT](https://github.com/rdkcentral/python_raft/blob/1.0.0/README.md) and [example_rack_config.yml](https://github.com/rdkcentral/python_raft/blob/1.0.0/examples/configs/example_rack_config.yml)

In this file, update the configuration to define the console sessions for the `DUT` and the outbound settings:

|Console Session|Description|
|---------------|-----------|
|default|Used by raft|
|ssh_hal_test|To run the `HAL` binary|

```yaml
rackConfig:
  - dut:
      ip: "XXX.XXX.XXX.XXX"  # IP Address of the device
      description: "vDevice device under test"
      platform: "vDevice"
      consoles:
        - default:
            type: "ssh"
            port:
            username: "root"
            ip: "XXX.XXX.XXX" # IP address of the device
            password:
        - ssh_hal_test:
            type: "ssh"
            port:
            username: "root"
            ip: "XXX.XXX.XXX" # IP address of the device
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
- Make sure to specify the correct stream download URL to enable downloading streams for L3 test cases.

```yaml
deviceConfig:
    cpe1:
        platform:   "vDevice"
        model:      "UK"
        soc_vendor: "intel"
        target_directory: "/tmp/"
        prompt: "~#" # Prompt string on console
        test:
            #TODO: Use the single profile file which contains all details (ds, hdmi, etc)
            profile: "..\\..\\..\\profiles\\hfp-vdevice.yaml"
            streams_download_url: "<http stream path>" #URL path from which the streams are downloaded to the device

```

#### Test Setup Configuration File

Example Test Setup configuration File: [vts_avmodule_setup.yaml](../host/tests/TestCases/vts_avmodule_setup.yaml)

This `yaml` contains the list of test_suites and test_cases to run

To execute multiple test_suites, update the YAML file as shown in the example below:

```yaml
AVModule:
  description: "AVModule L1 and L2 test setup"
  num_of_instances: 1
  test_suites: # List of L1 and L2 test suites
    ######################################
    # Entry to run all test case
    ######################################
    #  - name: "VTS_L1_AudioDecoder"
    #    test_cases:
    #      - all
    #######################################
    # Entries to run individual test cases
    #######################################
    - name: "VTS_L1_AudioDecoder"
      test_cases:
        - getAudioDecoderIds_pos
        - getAudioDecoder_pos

    - name: "VTS_L2_AudioDecoder"
      test_cases:
        - SetandGetProperties
```

Note : by default, all AV module test cases are added in the setup file

#### Number of Instances

The `number_of_instances` field in the test setup configuration specifies how many parallel instances of the test should run at the same time.

- If set to `1`, the test runs in a single instance.
- If set to `2`, the framework will open two SSH connections to the DUT, run the HAL test binary in both instances, and execute the test cases in parallel.
- Increasing the number of instances can speed up overall execution time by leveraging parallel testing, provided the DUT and test environment support concurrent runs.

#### Test Configuration

Example Test Setup configuration File: [vts_avmodule_testConfig.yaml](../host/tests/TestCases/vts_avmodule_testConfig.yaml)

Execute command to run the HAL binary was provided in this file. The created binary tar file should be placed in the artifacts section so that it can be fetched by the RAFT automation.

```yaml
AVModule:
    description: "AVModule testing profile / menu system for UT"
    test:
        artifacts:
        #List of artifacts folders, test class copies the content of folder to the target device workspace
          - "..\\..\\..\\build\\<tar name>.tar.gz"
        # exectute command, this will appended with the target device workspace path
        execute: "./run.sh"
        type: UT-C # C (UT-C Cunit) / C++ (UT-G (g++ ut-core gtest backend))
```

### Run on Windows Environment

To run the AVModule L1, L2, and L3 tests in a Windows environment, follow these additional steps after checking out the repository and compiling the code:

1. Install the `host` folder and update the rack configuration files as usual in your Linux environment.

2. Move the entire project folder (including `host`) to your Windows machine.

3. Open the file located at `framework/plugins/ut_raft/interactive_shell.py`.

   - Comment out or remove the following import lines to avoid errors on Windows:
     ```python
     import pty
     import fcntl
     ```

4. After these changes, you can run the test cases using Python on your Windows system as usual.


### Run Test Cases

Once the environment is set up, you can execute the test cases with the following command

```bash
python vts_avmodule_tests.py --config </PATH>/host/tests/configs/vts_rack_config.yml --deviceConfig </PATH>/host/tests/configs/vts_deviceConfig.yml
