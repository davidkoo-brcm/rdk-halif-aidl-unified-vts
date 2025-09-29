#!/usr/bin/env python3
#** *****************************************************************************
# *
# * If not stated otherwise in this file or this component's LICENSE file the
# * following copyright and licenses apply:
# *
# * Copyright 2025 RDK Management
# *
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# * http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.
# *
#* ******************************************************************************

import os
import yaml
import sys
from pathlib import Path

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, "../"))

from vts_avmodules_helper import AVModuleTestHelperClass
from raft.framework.core.logModule import logModule
from raft.framework.plugins.ut_raft import utHelperClass
from raft.framework.plugins.ut_raft.utPlayer import utPlayer
from raft.framework.plugins.ut_raft.utBaseUtils import utBaseUtils
from raft.framework.plugins.ut_raft.utSuiteNavigator import UTSuiteNavigatorClass
from raft.framework.plugins.ut_raft.configRead import ConfigRead


class L4TestClass(AVModuleTestHelperClass):
    """
    Test class for running L4 tests for the AV module (e.g., playback, trickmode tests).
    """

    def __init__(self, log: logModule = None):
        """
        Initializes the L4 test class.

        Args:
            log (logModule, optional): Parent log class. Defaults to None.
        """
        super().__init__(
            module_name="AVModule",
            test_name="L4_AVModule",
            qc_id="L4_001",
            test_suites=["VTS_L4_AVMODULE"],
            l4_yaml_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), "vts_l4_test_info.yaml"),
            log=log
        )

    def testFunction(self):
        """
        The main test function to run L4 tests, looping through each test case.

        Returns:
            bool: Final result of the test.
        """
        if not self.test_prepare_function():
            self.log.error("Test preparation failed")
            return False

        final_result = True
        outputs = []
        results = []
        test_suite_name = "VTS_L4_AVMODULE"
        self.waitTime = self.cpe.get("wait_time")
        self.module_name = "AVModule"
        socVendor = self.cpe.get("soc_vendor")

        self.player_session = self.dut.getConsoleSession("ssh_player")

        self.testSession =  utPlayer(self.player_session, socVendor)

        # extra command required for av modules , todo remove once it fixed
        cmd = """
        systemctl restart hal-av_buffer.service
        sleep 3
        """
        self.writeCommands(cmd, self.player_session)

        self.utilities = utBaseUtils()
        self.ut_menu = []
        ut_menu = UTSuiteNavigatorClass(self.test_config, None, self.player_session)
        self.ut_menu.append(ut_menu)

        self.utilities.change_directory(self.player_session, self.run_path)

        # Read L4 test info YAML to get test cases
        if not os.path.exists(self.l4_yaml_path):
            self.log.error(f"L4 input YAML file {self.l4_yaml_path} does not exist")
            return False

        with open(self.l4_yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        l4_tests = data.get("AVModule", {}).get("L4", [])
        manual_verification = False

        if not self.restart_required:
            for i, ut_menu in enumerate(self.ut_menu):
                self.log.info(f"[Instance {i}] Starting test case...")
                ut_menu.start()

        for test_case in l4_tests:
            tcid = test_case.get("tcid")
            action = test_case.get("action")
            stream_name = test_case.get("stream_name")
            target_stream_name = stream_name
            self.log.testStart(test_suite_name, tcid)

            if self.restart_required:
                cmd = """
                systemctl restart hal-av_buffer.service
                sleep 3
                """
                self.writeCommands(cmd, self.player_session)
                for i, ut_menu in enumerate(self.ut_menu):
                    self.log.info(f"[Instance {i}] Starting test case...")
                    ut_menu.start()

            # Map action to test case name
            action_to_test_case = {
                "normal_play": "NoramlPlay",
                "trick_play": "playBackWithTrickModes"
            }
            test_case_name = action_to_test_case.get(action, action)

            self.log.stepStart(f"Test Suite: {test_suite_name} TCID: {tcid} Action: {test_case_name} Stream: {target_stream_name}")

            # Generate YAML files for this test case
            test_config_path = os.path.join(dir_path, "vts_l4_av_test_config.yaml")
            stream_config_path = os.path.join(dir_path, "vts_l4_av_stream_config.yaml")
            if not self.generate_l4_yaml_files_for_test_case(test_case, test_config_path, stream_config_path):
                self.log.error(f"Failed to generate YAML files for TCID: {tcid}")
                final_result = False
                continue

            # Copy YAML files and stream to DUT
            if not self.copy_yaml_and_stream(test_config_path, stream_config_path, stream_name, tcid):
                self.log.error(f"Failed to copy YAML files or stream for TCID: {tcid}")
                final_result = False
                continue

            self.stream_info = ConfigRead(stream_config_path, "AVStreams")

            duration = self.stream_info.get(f"{tcid}_mp4.duration")
            if duration is None:
                self.log.info(f"No stream duration found for {tcid}_mp4 in stream config")
                wait_time = self.wait_time  # fallback
            else:
                wait_time = duration #

            output = ut_menu.select(test_suite_name, test_case_name, None, wait_time, False)
            outputs.append(output)

            # Check if the playback verification prompt exists in the output
            if "Is the stream playback good (Y/N)?" in output:
                # Call manual verification (will ask user Y/N)
                result1 = not self.testVerifyAVPlayback(True)
                self.restart_required = False

                # You can handle the result here
                if result1:
                    self.log.info("Playback verification failed.")
                else:
                    self.log.info("Playback verification passed.")
            else:
                self.restart_required = True

            if not self.restart_required:
                for i, ut_menu in enumerate(self.ut_menu):
                    self.log.info(f"[Instance {i}] Stopping test case...")
                    ut_menu.stop()

            result = ut_menu.collect_results(output, True)
            if result is None:
                final_result = False
            results.append(result)
            self.log.stepResult(result, f"Test Suite: {test_suite_name} TCID: {tcid} Action: {test_case_name}")

            # Clean up streams after each test case
            self.test_clean_all_assets()

            self.log.testResult(f'{test_suite_name} Finished')

        if self.restart_required:
            for i, ut_menu in enumerate(self.ut_menu):
                self.log.info(f"[Instance {i}] Stopping test case...")
                ut_menu.stop()

        self.test_cleanup()
        return final_result

if __name__ == "__main__":
    summerLogName = os.path.splitext(os.path.basename(__file__))[0] + "_summery"
    summeryLog = logModule("L4Test", level=logModule.INFO)
    test = L4TestClass(summeryLog)
    test.run(False)