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
sys.path.append(os.path.join(dir_path, "../../../vts_hal_test_components/hdmicec/host/tests")) # For hdmicec module

from vts_hdmicec_L3_ReceiveMessage import VTS_HDMICEC_L3_ReceiveMessage as vts_hdmicec_L3_receive_message
from vts_hdmicec_L3_SendMessage import VTS_HDMICEC_L3_SendMessage as vts_hdmicec_L3_send_message
from raft.framework.core.logModule import logModule

if __name__ == '__main__':
    summaryLogName = "run_non_av_vts_summary"
    summaryLog = logModule(summaryLogName, level=logModule.INFO)

    # Create test instances
    tests = [
        vts_hdmicec_L3_receive_message(summaryLog, testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        vts_hdmicec_L3_send_message(summaryLog, testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path)
        # Add more test instances here
    ]

    # Run each test
    for test in tests:
        test.run(False)
        time.sleep(2)  # Short delay between tests
