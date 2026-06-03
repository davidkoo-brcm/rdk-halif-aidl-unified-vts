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

#This python script runs Non-AV L3 VTS test cases

import os
import sys
import time

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, "../"))
sys.path.append(os.path.join(dir_path, "../../../vts_hal_test_components/indicator/host/tests"))

from vts_indicator_L3_SetStates import VTS_INDICATOR_L3_SetStates as vts_indicator_L3_SetStates
from vts_indicator_L3_StressTest import VTS_INDICATOR_L3_StressTest as vts_indicator_L3_StressTest

from raft.framework.core.logModule import logModule

if __name__ == '__main__':
    summaryLogName = "run_non_av_vts_summary"
    summaryLog = logModule(summaryLogName, level=logModule.INFO)

    # Create test instances
    tests = [
        vts_indicator_L3_SetStates(summaryLog, hfpfile=os.path.join(dir_path, "../../../vts_hal_test_components/indicator/profiles/hfp-indicator_vcomponent.yaml"), ledConfig=os.path.join(dir_path, "../../../vts_hal_test_components/indicator/test_configuration/vts_indicator_LED_config_vdevice.yaml"), testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        vts_indicator_L3_StressTest(summaryLog, hfpfile=os.path.join(dir_path, "../../../vts_hal_test_components/indicator/profiles/hfp-indicator_vcomponent.yaml"), ledConfig=os.path.join(dir_path, "../../../vts_hal_test_components/indicator/test_configuration/vts_indicator_LED_config_vdevice.yaml"), testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        # Add more test instances here
    ]

    # Run each test
    for test in tests:
        test.run(False)
        time.sleep(2)  # Short delay between tests