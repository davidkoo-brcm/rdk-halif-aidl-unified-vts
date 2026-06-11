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


sys.path.append(os.path.join(dir_path, "../../../vts_hal_test_components/hdmicec/host/tests")) # For hdmicec module
sys.path.append(os.path.join(dir_path, "../../../vts_hal_test_components/boot/host/tests")) # For boot module
sys.path.append(os.path.join(dir_path, "../../../vts_hal_test_components/deepsleep/host/tests"))
sys.path.append(os.path.join(dir_path, "../../../vts_hal_test_components/hdmioutput/host/tests"))
sys.path.append(os.path.join(dir_path, "../../../vts_hal_test_components/compositeinput/host/tests"))

from vts_hdmicec_L3_ReceiveMessage import VTS_HDMICEC_L3_ReceiveMessage as vts_hdmicec_L3_receive_message
from vts_hdmicec_L3_SendMessage import VTS_HDMICEC_L3_SendMessage as vts_hdmicec_L3_send_message
from vts_boot_L3_VerifyBootReasonExternalCause import VTS_BOOT_L3_VerifyBootReasonExternalCause as vts_boot_L3_verify_boot_reason_external_cause
from vts_boot_L3_VerifyOverrideBootReason import VTS_BOOT_L3_VerifyOverrideBootReason as vts_boot_L3_verify_override_boot_reason
from vts_boot_L3_VerifyReboot import VTS_BOOT_L3_VerifyReboot as vts_boot_L3_verify_reboot
from vts_deepsleep_L3_WakeFromSupportedTrigger import VTS_DEEPSLEEP_L3_WakeFromSupportedTrigger as vts_deepsleep_L3_wakefromsupportedtrigger
from vts_deepsleep_L3_WakeFromPreconfiguredTrigger import VTS_DEEPSLEEP_L3_WakeFromPreconfiguredTrigger as vts_deepsleep_L3_wakefrompreconfiguredtrigger
from vts_deepsleep_L3_VerifyWakeWithMixedInputTriggerList import VTS_DEEPSLEEP_L3_VerifyWakeWithMixedInputTriggerList as vts_deepsleep_L3_verifywakewithmixedinputtriggerlist
from vts_deepsleep_L3_NoWakeFromUnspecifiedOrUnsupportedTrigger import VTS_DEEPSLEEP_L3_NoWakeFromUnspecifiedOrUnsupportedTrigger as vts_deepsleep_L3_nowakefromunspecifiedorunsupportedtrigger
from vts_hdmioutput_L3_PropertyApplicationVerification import VTS_HDMIOUTPUT_L3_PropertyApplicationVerification as vts_hdmioutput_L3_propertyapplicationverification
from vts_hdmioutput_L3_SPDInfoFrameTransmission import VTS_HDMIOUTPUT_L3_SPDInfoFrameTransmission as vts_hdmioutput_L3_spdinfoframetransmission
from vts_hdmioutput_L3_HotPlugDetectStateBeforeStartCallback import VTS_HDMIOUTPUT_L3_HotPlugDetectStateBeforeStartCallback as vts_hdmioutput_L3_hotplugDetectstatebeforestartcallback
from vts_hdmioutput_L3_HotPlugDetectStateAfterStartCallback import VTS_HDMIOUTPUT_L3_HotPlugDetectStateAfterStartCallback as vts_hdmioutput_L3_hotplugDetectstateafterstartcallback
from vts_compositeinput_L3_VideoModeDetection import VTS_COMPOSITEINPUT_L3_VideoModeDetection as vts_compositeinput_L3_videoModedetection
from vts_compositeinput_L3_ConnectionTestBeforeStart import VTS_COMPOSITEINPUT_L3_ConnectionTestBeforeStart as vts_compositeinput_L3_connectiontestbeforestart
from vts_compositeinput_L3_ConnectionTestAfterStart import VTS_COMPOSITEINPUT_L3_ConnectionTestAfterStart as vts_compositeinput_L3_connectiontestafterstart
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
        lambda: vts_thermalsensor_L3_critical_shutdown_with_suppression(summaryLog, moduleName="VTS"),
        lambda: vts_thermalsensor_L3_thermal_exceed_recovery_lifecycle(summaryLog, moduleName="VTS"),
        lambda: vts_hdmicec_L3_receive_message(summaryLog, testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        lambda: vts_hdmicec_L3_send_message(summaryLog, testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        lambda: vts_boot_L3_verify_boot_reason_external_cause(summaryLog, testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        lambda: vts_boot_L3_verify_override_boot_reason(summaryLog, testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        lambda: vts_boot_L3_verify_reboot(summaryLog, testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        lambda: vts_deepsleep_L3_wakefromsupportedtrigger(summaryLog, hfpfile=os.path.join(dir_path, "../../../vts_hal_test_components/deepsleep/profiles/hfp-deepsleep-vcomponent.yaml"), testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        lambda: vts_deepsleep_L3_wakefrompreconfiguredtrigger(summaryLog, hfpfile=os.path.join(dir_path, "../../../vts_hal_test_components/deepsleep/profiles/hfp-deepsleep-vcomponent.yaml"), testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        lambda: vts_deepsleep_L3_verifywakewithmixedinputtriggerlist(summaryLog, hfpfile=os.path.join(dir_path, "../../../vts_hal_test_components/deepsleep/profiles/hfp-deepsleep-vcomponent.yaml"), testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        lambda: vts_deepsleep_L3_nowakefromunspecifiedorunsupportedtrigger(summaryLog, hfpfile=os.path.join(dir_path, "../../../vts_hal_test_components/deepsleep/profiles/hfp-deepsleep-vcomponent.yaml"), testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        lambda: vts_hdmioutput_L3_propertyapplicationverification(summaryLog, hfpfile=os.path.join(dir_path, "../../../vts_hal_test_components/hdmioutput/profiles/hfp-hdmioutput.yaml"), testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        lambda: vts_hdmioutput_L3_spdinfoframetransmission(summaryLog, hfpfile=os.path.join(dir_path, "../../../vts_hal_test_components/hdmioutput/profiles/hfp-hdmioutput.yaml"), testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        lambda: vts_hdmioutput_L3_hotplugDetectstatebeforestartcallback(summaryLog, hfpfile=os.path.join(dir_path, "../../../vts_hal_test_components/hdmioutput/profiles/hfp-hdmioutput.yaml"), testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        lambda: vts_hdmioutput_L3_hotplugDetectstateafterstartcallback(summaryLog, hfpfile=os.path.join(dir_path, "../../../vts_hal_test_components/hdmioutput/profiles/hfp-hdmioutput.yaml"), testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        lambda: vts_compositeinput_L3_videoModedetection(summaryLog, hfpfile=os.path.join(dir_path, "../../../vts_hal_test_components/compositeinput/profiles/hfp-compositeinput.yaml"), testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        lambda: vts_compositeinput_L3_connectiontestbeforestart(summaryLog, hfpfile=os.path.join(dir_path, "../../../vts_hal_test_components/compositeinput/profiles/hfp-compositeinput.yaml"), testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path),
        lambda: vts_compositeinput_L3_connectiontestafterstart(summaryLog, hfpfile=os.path.join(dir_path, "../../../vts_hal_test_components/compositeinput/profiles/hfp-compositeinput.yaml"), testMenuConfigFile=os.path.join(dir_path, "vts_l3_test_setup.yaml"), moduleName="VTS", artifactDirPath=dir_path)
        # Add more test instances here
        # Need to test after deepsleep integration
        # lambda: vts_motionsensor_L3_deep_sleep_autonomy(summaryLog, moduleName="VTS"),

    ]

    # Run each test
    for test_factory in tests:
        test_factory().run(False)
        time.sleep(2)  # Short delay between tests
