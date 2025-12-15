#!/usr/bin/env python3
#** *****************************************************************************
# *
# * If not stated otherwise in this file or this component's LICENSE file the
# * following copyright and licenses apply:
# *
# * Copyright 2024 RDK Management
# *
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# *
# http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.
# *
#* ******************************************************************************

import os
import sys
import time

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, "../"))

from raft.framework.plugins.ut_raft.configRead import ConfigRead
from raft.framework.core.logModule import logModule
from raft.framework.plugins.ut_raft import utHelperClass
from raft.framework.plugins.ut_raft.utSuiteNavigator import UTSuiteNavigatorClass
from raft.framework.plugins.ut_raft.utBaseUtils import utBaseUtils

class  AVModule_Tests(utHelperClass):
    """
    Runs automated L1, L2, and L3 AV module tests on the target device.
    Handles setup, service restarts, asset management, and multi-instance execution.
    Collects and aggregates test results for pass/fail reporting.
    """
    def __init__(self, log:logModule=None):
        """
        Initializes the test class
        """
        testName = "AVModule"
        qcId = "1"
        super().__init__(testName, qcId, log)

        self.log = log
        if log is None:
            self.log = logModule(self.__class__.__name__)
            self.log.setLevel( self.log.INFO )

        self.moduleName = testName
        deviceTestSetup = self.cpe.get("test")
        targetWorkspace = self.cpe.get("target_directory")
        prompt = self.cpe.get("prompt")
        self.allWaitTime = self.cpe.get("all_wait_time")
        self.waitTime = self.cpe.get("wait_time")

        # kept for the process restart between test cases if required
        self.vSinkprocessName = self.cpe.get("vsink_process_name")
        self.vDecoderprocessName = self.cpe.get("vdecoder_process_name")
        self.aSinkprocessName = self.cpe.get("asink_process_name")
        self.aDecoderprocessName = self.cpe.get("adecoder_process_name")
        self.processPath = self.cpe.get("process_path")
        self.IsAVBufferRestart = self.cpe.get("AVBuffer_Restart")
        self.avClockProcessName = self.cpe.get("avClock_process_name")
        self.planeCtrlProcessName = self.cpe.get("planeCtrl_process_name")

        #stream url path
        self.streamDownloadURL = deviceTestSetup.get("streams_download_url")
        self.rackDevice = "dut"

        self.downloadPath = self.cpe.get("download_path")

        # Get the target workspace
        self.targetWorkspace = targetWorkspace

        # Load test setup configuration
        testSetupPath = os.path.join(dir_path, "vts_avmodule_setup.yaml" )
        self.testConfigFile = os.path.join(dir_path, "vts_avmodule_testConfig.yaml")
        self.testSetup = ConfigRead(testSetupPath, self.moduleName)
        self.restartRequired = self.testSetup.fields.get('restart_required')
        self.hal_session_0 = self.dut.getConsoleSession("ssh_hal_test_0")
        self.hal_session_1 = self.dut.getConsoleSession("ssh_hal_test_1")
        self.hal_session_2 = self.dut.getConsoleSession("ssh_hal_test_2")
        self.hal_session_0.prompt = prompt
        self.hal_session_1.prompt = prompt
        self.hal_session_2.prompt = prompt

        self.binPath = "bin/" #bin path which is coming from the build
        self.profilePath = "profiles/"

        # Forming the run.sh exe path and tar copy path /tmp/<modulename>/bin/run.sh and /tmp/<modulename>
        targetWorkspace = os.path.join(targetWorkspace,self.moduleName)
        targetWorkspace = targetWorkspace.replace("\\", "/")
        runPath = os.path.join(targetWorkspace,self.binPath)
        runPath = runPath.replace("\\", "/")

        #stream download path
        self.downloadPath = os.path.join(runPath, self.downloadPath)

        self.instanceList = self.testSetup.fields.get('num_of_instances')

        #Forming profile paths for many instances...
        profile_path = deviceTestSetup.get("profile")
        directory_path, filename = os.path.split(profile_path)
        name, extension = os.path.splitext(filename)

        self.moduleConfigProfileFiles = []
        self.utMenu = []

        for i in range(self.instanceList):
            instanceNum = i + 1  # For naming like _1, _2...

            # instanceList is a single integer, like 1 or 2
            if self.instanceList == 1:
                # Single instance, use original file path
                finalProfile = os.path.join(directory_path, filename)
            else:
                # Multiple instances: create filenames like ...instance_1.yaml, instance_2.yaml, etc.
                finalProfile = os.path.join(directory_path, f"{name}_instance_{instanceNum}{extension}")
            self.moduleConfigProfileFiles.append(finalProfile)

            # Forming the profile path /tmp/<modulename>/bin/profiles/hfp-profile.yaml
            moduleConfigProfileFilePath = os.path.join(self.profilePath, os.path.basename(self.moduleConfigProfileFiles[i]))
            moduleConfigProfileFilePath = moduleConfigProfileFilePath.replace("\\", "/")
           # Load configurations for device profile and menu
            self.testConfig    = ConfigRead(self.testConfigFile, self.moduleName)
            #Forming exe command
            self.testConfig.test.execute = self.testConfig.test.execute + f" -p {moduleConfigProfileFilePath}"

            session_index = instanceNum - 1  # map 1 → 0, 2 → 1, etc.
            hal_session = getattr(self, f'hal_session_{session_index}', None)
            utMenu = UTSuiteNavigatorClass(self.testConfig, None, hal_session)
            self.utMenu.append(utMenu)
            self.testSession   = hal_session
            self.utilities     = utBaseUtils()

            tarFilesPath = os.path.normpath(os.path.join(dir_path, *self.testConfig.test.artifacts))
            self.utilities.sftpCopy(self.testSession, tarFilesPath, targetWorkspace)

            self.utilities.change_directory(self.testSession, targetWorkspace)
            self.utilities.untar(self.testSession, os.path.basename(tarFilesPath), targetWorkspace)
            self.utilities.change_directory(self.testSession, runPath)

    def runTest(self, testSuite:str="L3 AVModule", test_case:str=None):
        """
        Runs the test case passed to this funtion
        Args:
            test_case (str, optional): test case name to run
        Returns:
            bool: True - test pass, False - test fails
        """
        outputs = []
        results = []

        # Step 1: Start all instances
        if self.restartRequired:
            for i, utMenu in enumerate(self.utMenu):
                self.log.info(f"[Instance {i}] Starting test case...")
                utMenu.start()

        # Step 2: Run select() for each instance
        for i, utMenu in enumerate(self.utMenu):
            self.log.info(f"[Instance {i}] Selecting test case {test_case}...")
            output = utMenu.select(testSuite, test_case, None, self.waitTime, False)
            outputs.append(output)

        # Step 3: Stop all instances
        if self.restartRequired:
            for i, utMenu in enumerate(self.utMenu):
                self.log.info(f"[Instance {i}] Stopping test case...")
                utMenu.stop()

        # Step 4: Collect results
        for i, (utMenu, output) in enumerate(zip(self.utMenu, outputs)):
            result = utMenu.collect_results(output, True)
            if result is None:
                result = False
            results.append(result)
            self.log.info(f"[Instance {i}] Result: {result}")

        # Final result
        return all(results)

    def runAll(self, testSuite: str = "L3 AVModule", test_case: str = None):
        """
        Runs the test case (or all tests if test_case is None) on all instances
        without stopping them afterward.

        Args:
            test_case (str, optional): Test case name to run.
                                    If None, all tests in the suite are run.

        Returns:
            bool: True if all instances pass, False otherwise.
        """
        outputs = []
        results = []

        # Step 1: Start all instances
        if self.restartRequired:
            for i, utMenu in enumerate(self.utMenu):
                self.log.info(f"[Instance {i}] Starting test case(s)...")
                utMenu.start()

        # Step 2: Run tests for each instance
        for i, utMenu in enumerate(self.utMenu):
            self.log.info(f"[Instance {i}] Running test suite '{testSuite}', "
                        f"test_case='{test_case if test_case else 'ALL'}'...")
            output = utMenu.select(testSuite, test_case, None, self.allWaitTime, False)
            outputs.append(output)

        # Step 3: Stop all instances
        if self.restartRequired:
            for i, utMenu in enumerate(self.utMenu):
                self.log.info(f"[Instance {i}] Stopping test case(s)...")
                utMenu.stop()

        # Step 3: Collect results from all instances (no stop)
        for i, (utMenu, output) in enumerate(zip(self.utMenu, outputs)):
            result = utMenu.collect_results(output, True)
            if result is None:
                result = False
            results.append(result)
            self.log.info(f"[Instance {i}] Result: {result}")

        # Final result
        return all(results)

    def restart_services(self, testsuite_name):
        """
        Restarts only the AV-related process based on module name in testsuite_name.
        """
        # Extract module name from testsuite_name
        try:
            module = testsuite_name.strip().split("_")[-1].lower()  # e.g., 'videodecoder'
        except Exception:
            self.log.error("Invalid testsuite_name format: %s", testsuite_name)
            return

        for instanceNum in range(self.instanceList):
            session_index = instanceNum
            hal_session = getattr(self, f'hal_session_{session_index}', None)

            if not hal_session:
                self.log.info(f"HAL session for instance {instanceNum} not found — skipping.")
                continue

            #TODO : hardcoded the restart for now as the AVClock service is not started in vDevice. Need to remove.
            #self.utilities.restart_process_by_name(hal_session, "RDKAVClockService", "/usr/bin/")

            if self.IsAVBufferRestart == 1 and module == "avbuffer":
                self.log.info("Restarting AVBufferService...")
                self.utilities.restart_process_by_name(hal_session, "RDKAVBufferService", "/usr/bin/")
                continue

            services = {
                "videosink": (self.vSinkprocessName, self.processPath, "VideoSink"),
                "videodecoder": (self.vDecoderprocessName, self.processPath, "VideoDecoder"),
                "audiosink": (self.aSinkprocessName, self.processPath, "AudioSink"),
                "audiodecoder": (self.aDecoderprocessName, self.processPath, "AudioDecoder"),
                "avclock": (self.avClockProcessName, self.processPath, "AVClock"),
                "planecontrol": (self.planeCtrlProcessName, self.processPath, "PlaneControl"),
            }

            if module in services:
                proc_name, proc_path, label = services[module]
                if proc_name and proc_path:
                    self.log.info(f"Restarting {label} process: {proc_name} for instance {instanceNum}")
                    self.utilities.restart_process_by_name(hal_session, proc_name, proc_path)
                else:
                    self.log.info(f"{label} process name or path is None — skipping restart.")
            else:
                self.log.info(f"Module '{module}' not recognized — no process restarted.")

    def testDownloadAllAssets(self, testsuite_name):
        self.testStreams = []
        url = []

        test_suites = self.testSetup.fields.get('test_suites')

        streams = []
        for suite in test_suites:
            if suite.get("name") == testsuite_name:
                streams = suite.get("streams", [])
                break

        if streams and self.streamDownloadURL:
            for streamPath in streams:
                full_url = os.path.join(self.streamDownloadURL, streamPath.lstrip("/"))
                url.append(full_url)
                self.testStreams.append(os.path.join(self.downloadPath, os.path.basename(streamPath)))

            self.downloadToDevice(url, self.downloadPath, self.rackDevice, True)


    def testCleanAllAssets(self):
        """
        Removes the downloaded assets and test streams from the DUT after test execution.
        """
        if self.testStreams:
            self.log.info("Removing Downloaded Assets...")
            self.deleteFromDevice(self.testStreams, self.rackDevice, False)
            self.testStreams = []
        else:
            self.log.info("No test streams to clean.")

    def testFunction(self):
        """
        The main test function to run the L1 and L2 tests.

        Returns:
            bool: Final result of the test.
        """
        testsuites = self.testSetup.fields.get('test_suites')

        finalresult = True

        if not self.restartRequired:
            for i, utMenu in enumerate(self.utMenu):
                self.log.info(f"[Instance {i}] Starting test case...")
                utMenu.start()

        for testsuite in testsuites:
            testsuite_name = testsuite.get("name")

            test_cases = testsuite.get("test_cases")

            self.testDownloadAllAssets(testsuite_name)

            if len(test_cases) == 1 and test_cases[0] == "all":
                self.log.stepStart(f'Test Suit: {testsuite_name} Run all Tests cases')

                #restarting before starting the test cases
                if self.restartRequired:
                    self.restart_services(testsuite_name)

                # If 'all' test case mentioned in list, run all tests with 'r' option
                result = self.runAll(testsuite_name)
                if not result:
                    finalresult = False
                self.log.stepResult(result, f'Test Suit: {testsuite_name} Run all Tests cases')

                #restarting after completing the test cases.
                if self.restartRequired:
                    self.restart_services(testsuite_name)

            else:
                for test_case in testsuite.get("test_cases"):
                    self.log.stepStart(f'Test Suit: {testsuite_name} Test Case: {test_case}')

                    #restarting before starting the test cases
                    if self.restartRequired:
                        self.restart_services(testsuite_name)

                    result = self.runTest(testsuite_name, test_case)
                    if not result:
                        finalresult = False
                    self.log.stepResult(result, f'Test Suit: {testsuite_name} Test Case: {test_case}')

            self.testCleanAllAssets()

        return finalresult

if __name__ == '__main__':
    summerLogName = os.path.splitext(os.path.basename(__file__))[0] + "_summery"
    summeryLog = logModule(summerLogName, level=logModule.INFO)
    test = AVModule_Tests(summeryLog)
    test.run(False)
