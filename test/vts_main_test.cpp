/**
 *  If not stated otherwise in this file or this component's LICENSE
 *  file the following copyright and licenses apply:
 *
 *  Copyright 2025 RDK Management
 *
 *  Licensed under the Apache License, Version 2.0 (the License);
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an AS IS BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */

/**
 * @addtogroup HPK Hardware Porting Kit
 * @{
 * @par The Hardware Porting Kit
 * HPK is the next evolution of the well-defined Hardware Abstraction Layer
 * (HAL), but augmented with more comprehensive documentation and test suites
 * that OEM or SOC vendors can use to self-certify their ports before taking
 * them to RDKM for validation or to an operator for final integration and
 * deployment. The Hardware Porting Kit effectively enables an OEM and/or SOC
 * vendor to self-certify their own Video Accelerator devices, with minimal RDKM
 * assistance.
 *
 */

/**
 * @addtogroup UNIFIED_VTS Unified VTS
 * @{
 */

/**
 * @addtogroup UNIFIED_VTS_Halif_Test Unified VTS HALIF Tests
 * @{
 */

/**
 * @defgroup UNIFIED_VTS_Halif_Test_Main Unified VTS HALIF Tests Main File
 * @{
 * @parblock
 *
 * ### main functions for Unified VTS VTS HALIF AIDL tests :
 *
 *
 *
 * **Pre-Conditions:**  None@n
 * **Dependencies:** None@n
 *
 * Ref to API Definition specification documentation :
 *
 * @endparblock
 */

/**
 * @file vts_main_test.cpp
 *
 */

#include <ut.h>
#include <ut_log.h>

#include "vts_avbuffer_init.h"
#include "vts_audiodecoder_init.h"
#include "vts_audiosink_init.h"
#include "vts_videosink_init.h"
#include "vts_videodecoder_init.h"
#include "vts_avclock_init.h"
#include "vts_planecontrol_init.h"

int main(int argc, char **argv)
{
    UT_status_t result;

    UT_init(argc, argv);

    UT_LOG_INFO("==========================================================================");
    UT_LOG_INFO("\t BUILD_TIMESTAMP: \033[0;32m%s\033[0m", BUILD_TIMESTAMP);
    UT_LOG_INFO("\t UNIFIED VTS Version: \033[0;32m%s\033[0m", HALIF_TEST_PROJECT_VERSION);
    UT_LOG_INFO("\t AIDL HALIF Version: \033[0;32m%s\033[0m",RDK_HALIF_AIDL_VERSION);
    UT_LOG_INFO("\t VTS UNIFIED Audio Decoder HALIF Test Version: \033[0;32m%s\033[0m",AUDIODECODER_VERSION);
    UT_LOG_INFO("\t VTS UNIFIED Audio Sink HALIF Test Version: \033[0;32m%s\033[0m",AUDIOSINK_VERSION);
    UT_LOG_INFO("\t VTS UNIFIED Video Decoder HALIF Test Version: \033[0;32m%s\033[0m",VIDEODECODER_VERSION);
    UT_LOG_INFO("\t VTS UNIFIED Video Sink HALIF Test Version: \033[0;32m%s\033[0m",VIDEOSINK_VERSION);
    UT_LOG_INFO("\t VTS UNIFIED AVBuffer HALIF Test Version: \033[0;32m%s\033[0m",AVBUFFER_VERSION);
    UT_LOG_INFO("\t VTS UNIFIED AV Clock HALIF Test Version: \033[0;32m%s\033[0m",AVCLOCK_VERSION);
    UT_LOG_INFO("\t VTS UNIFIED Plane Control HALIF Test Version: \033[0;32m%s\033[0m",PLANECONTROL_VERSION);
    UT_LOG_INFO("==========================================================================");

    result = VTS_AVBuffer_init();
    if(result != UT_STATUS_OK)
    {
        UT_LOG_ERROR("Failed to initialize AVBuffer");
        result = UT_STATUS_FAILURE;
    }

    result = VTS_AudioDecoder_init();
    if(result != UT_STATUS_OK)
    {
        UT_LOG_ERROR("Failed to initialize AudioDecoder");
        result = UT_STATUS_FAILURE;
    }

    result = VTS_VideoDecoder_init();
    if(result != UT_STATUS_OK)
    {
        UT_LOG_ERROR("Failed to initialize VideoDecoder");
        result = UT_STATUS_FAILURE;
    }

    result = VTS_AudioSink_init();
    if(result != UT_STATUS_OK)
    {
        UT_LOG_ERROR("Failed to initialize AudioSink");
        result = UT_STATUS_FAILURE;
    }

    result = VTS_VideoSink_init();
    if(result != UT_STATUS_OK)
    {
        UT_LOG_ERROR("Failed to initialize VideoSink");
        result = UT_STATUS_FAILURE;
    }

    result = VTS_AVClock_init();
    if(result != UT_STATUS_OK)
    {
        UT_LOG_ERROR("Failed to initialize AV Clock");
        result = UT_STATUS_FAILURE;
    }

    result = VTS_PlaneControl_init();
    if(result != UT_STATUS_OK)
    {
        UT_LOG_ERROR("Failed to initialize AV Clock");
        result = UT_STATUS_FAILURE;
    }

    UT_status_t ut_result = UT_run_tests();

    if (result != UT_STATUS_OK || ut_result != UT_STATUS_OK)
    {
        result = UT_STATUS_FAILURE;
    }
    else
    {
        result = UT_STATUS_OK;
    }

    VTS_AudioDecoder_destroy();
    VTS_VideoDecoder_destroy();
    VTS_AudioSink_destroy();
    VTS_VideoSink_destroy();

    return result;
}

/** @} */ // End of UNIFIED_VTS_Halif_Test_Main
/** @} */ // End of UNIFIED_VTS_Halif_Test
/** @} */ // End of UNIFIED_VTS
/** @} */ // End of HPK
