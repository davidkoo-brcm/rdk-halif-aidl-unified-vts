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
sys.path.append(os.path.join(dir_path, "../../../vts_hal_test_components/flash/host/tests")) # For flash module
sys.path.append(os.path.join(dir_path, "../../../vts_hal_test_components/motionsensor/host/tests")) # For motionsensor module
sys.path.append(os.path.join(dir_path, "../../../vts_hal_test_components/thermalsensor/host/tests")) # For thermalsensor module

from vts_flash_L3_ConcurrentImage import VTS_FLASH_L3_ConcurrentImage as vts_flash_L3_concurrent_image
from vts_flash_L3_TestAllImages import VTS_FLASH_L3_TestAllImages as vts_flash_L3_test_all_images
from vts_flash_L3_validateAllErrorcodes import VTS_FLASH_L3_ValidateAllErrorCodes as vts_flash_L3_validate_all_errorcodes
from vts_motionsensor_L3_ActiveWindowBehavior import VTS_MOTIONSENSOR_L3_ActiveWindowBehavior as vts_motionsensor_L3_active_window_behavior
from vts_motionsensor_L3_DeepSleepAutonomy import VTS_MOTIONSENSOR_L3_DeepSleepAutonomy as vts_motionsensor_L3_deep_sleep_autonomy
from vts_motionsensor_L3_MotionEventDetection import VTS_MOTIONSENSOR_L3_MotionEventDetection as vts_motionsensor_L3_motion_event_detection
from vts_motionsensor_L3_NoMotionEventDetection import VTS_MOTIONSENSOR_L3_NoMotionEventDetection as vts_motionsensor_L3_no_motion_event_detection
from vts_thermalsensor_L3_CriticalShutdownWithSuppression import VTS_THERMALSENSOR_L3_CriticalShutdownWithSuppression as vts_thermalsensor_L3_critical_shutdown_with_suppression
from vts_thermalsensor_L3_ThermalExceedRecoveryLifecycle import VTS_THERMALSENSOR_L3_ThermalExceedRecoveryLifecycle as vts_thermalsensor_L3_thermal_exceed_recovery_lifecycle
from raft.framework.core.logModule import logModule


if __name__ == '__main__':
    summaryLogName = "run_non_av_vts_summary"
    summaryLog = logModule(summaryLogName, level=logModule.INFO)

    # Lambdas defer instantiation so each test opens fresh SSH sessions after the
    # previous test may have rebooted the device (closing any pre-existing connections).
    tests = [
        lambda: vts_flash_L3_concurrent_image(summaryLog, moduleName="VTS"),
        lambda: vts_flash_L3_test_all_images(summaryLog, moduleName="VTS"),
        lambda: vts_flash_L3_validate_all_errorcodes(summaryLog, moduleName="VTS"),
        lambda: vts_motionsensor_L3_motion_event_detection(summaryLog, moduleName="VTS"),
        lambda: vts_motionsensor_L3_no_motion_event_detection(summaryLog, moduleName="VTS"),
        lambda: vts_motionsensor_L3_active_window_behavior(summaryLog, moduleName="VTS"),
        # Need to test after deepsleep integration
        #lambda: vts_motionsensor_L3_deep_sleep_autonomy(summaryLog, moduleName="VTS"),
        lambda: vts_thermalsensor_L3_critical_shutdown_with_suppression(summaryLog, moduleName="VTS"),
        lambda: vts_thermalsensor_L3_thermal_exceed_recovery_lifecycle(summaryLog, moduleName="VTS")
        # Add more test instances here
    ]

    # Run each test
    for test_factory in tests:
        test_factory().run(False)
        time.sleep(2)  # Short delay between tests
