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
#* *****************************************************************************

import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, "../"))

from vts_avmodules_helper import AVModuleTestHelperClass
from raft.framework.core.logModule import logModule


class L3TestClass(AVModuleTestHelperClass):
    """Runs all L3 AVModule test suites (with streams) in a single entrypoint."""

    def __init__(self, log: logModule = None):
        super().__init__(
            module_name="AVModule",
            test_name="L3_AVModule",
            qc_id="L3_001",
            setup_file_name="vts_avmodule_setup.yaml",
            test_config_file_name="vts_avmodule_setup.yaml",
            log=log,
        )

    def testFunction(self) -> bool:
        """Main executor filtering only L3 suites from setup and running them."""
        if not self.test_prepare_function():
            self.log.error("Test preparation failed")
            return False

        final_result = True

        # Start UT menu once when restart is not required
        if not self.restart_required:
            for i, ut_menu in enumerate(self.ut_menu):
                self.log.info(f"[Instance {i}] Starting test case...")
                ut_menu.start()

        test_suites = self.test_setup.fields.get("test", {}).get("suites", {})

        for suite_key, suite in test_suites.items():
            suite_name = suite.get("name", "")
            # Filter only L3 suites
            if not suite_name.startswith("VTS_L3_"):
                continue

            test_cases = suite.get("tests")
            # If no test_cases listed in setup, default to run ALL from catalog
            if not test_cases:
                self.log.info(f"No test_cases in setup for {suite_name}; defaulting to ALL from catalog")
                test_cases = ["all"]

            # Download streams for this suite using helper (reads list directly)
            streams = suite.get("streams", [])
            if not self.download_streams_from_list(streams):
                final_result = False

            # Optional service restart handling
            if self.restart_required:
                self.restart_services(suite_name)

            if len(test_cases) == 1 and test_cases[0] == "all":
                self.log.stepStart(f"Test Suite: {suite_name} Run all Test cases")
                result = self.run_all(suite_name, use_all_wait_time=True)
                final_result = final_result and bool(result)
                self.log.stepResult(result, f"Test Suite: {suite_name} Run all Test cases")
            else:
                for tc in test_cases:
                    self.log.testStart(suite_name, tc)
                    self.log.stepStart(f"Test Suite: {suite_name} Test Case: {tc}")
                    result = self.runTest(suite_name, tc, use_all_wait_time=True)
                    final_result = final_result and bool(result)
                    self.log.stepResult(result, f"Test Suite: {suite_name} Test Case: {tc}")
                    self.log.testResult(f'{suite_name} Finished')

            # Clean downloaded assets for this suite
            self.test_clean_all_assets()

            # Optional post-suite restart
            if self.restart_required:
                self.restart_services(suite_name)

        # Stop UT menu if we started it once
        if not self.restart_required:
            for i, ut_menu in enumerate(self.ut_menu):
                self.log.info(f"[Instance {i}] Stopping test case...")
                ut_menu.stop()

        self.test_cleanup()
        return final_result


if __name__ == "__main__":
    summaryLogName = os.path.splitext(os.path.basename(__file__))[0] + "_summary"
    summaryLog = logModule("L3Test", level=logModule.INFO)
    test = L3TestClass(summaryLog)
    test.run(False)
