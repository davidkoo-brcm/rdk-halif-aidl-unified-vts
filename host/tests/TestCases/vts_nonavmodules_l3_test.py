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
sys.path.append(os.path.join(dir_path, "../../../vts_hal_test_components/boot/host/tests")) # For boot module

from vts_hdmicec_L3_ReceiveMessage import VTS_HDMICEC_L3_ReceiveMessage as vts_hdmicec_L3_receive_message
from vts_hdmicec_L3_SendMessage import VTS_HDMICEC_L3_SendMessage as vts_hdmicec_L3_send_message
from vts_boot_L3_VerifyBootReasonExternalCause import VTS_BOOT_L3_VerifyBootReasonExternalCause as vts_boot_L3_verify_boot_reason_external_cause
from vts_boot_L3_VerifyOverrideBootReason import VTS_BOOT_L3_VerifyOverrideBootReason as vts_boot_L3_verify_override_boot_reason
from vts_boot_L3_VerifyReboot import VTS_BOOT_L3_VerifyReboot as vts_boot_L3_verify_reboot
from raft.framework.core.logModule import logModule

if __name__ == '__main__':
    summaryLogName = "run_non_av_vts_summary"
    summaryLog = logModule(summaryLogName, level=logModule.INFO)

    # Lambdas defer instantiation so each test opens fresh SSH sessions after the
    # previous test may have rebooted the device (closing any pre-existing connections).
    tests = [
        # lambda: vts_hdmicec_L3_receive_message(summaryLog, testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        # lambda: vts_hdmicec_L3_send_message(summaryLog, testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        lambda: vts_boot_L3_verify_boot_reason_external_cause(summaryLog, testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        lambda: vts_boot_L3_verify_override_boot_reason(summaryLog, testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        lambda: vts_boot_L3_verify_reboot(summaryLog, testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path)
        # Add more test instances here
    ]

    # Run each test
    for test_factory in tests:
        test_factory().run(False)
        time.sleep(2)  # Short delay between tests
