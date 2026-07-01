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


#ifdef ENABLE_AV_L4_TEST
#include "vts_av_l4_init.h"
#endif


int main(int argc, char **argv)
{
    UT_status_t result;

    UT_init(argc, argv);

    UT_LOG_INFO("==========================================================================");
    UT_LOG("\t BUILD_TIMESTAMP: \033[0;32m%s\033[0m", BUILD_TIMESTAMP);
    UT_LOG("\t UNIFIED VTS Version: \033[0;32m%s\033[0m", HALIF_TEST_PROJECT_VERSION);

    UT_LOG_INFO("\t VTS UNIFIED HALIF L4 Test Version: \033[0;32m%s\033[0m",L4_TESTS_VERSION);

    UT_LOG_INFO("==========================================================================");


#ifdef ENABLE_AV_L4_TEST
    result = VTS_AV_init();
    if(result != UT_STATUS_OK)
    {
        UT_LOG_ERROR("Failed to initialize AV L4 Tests");
        result = UT_STATUS_FAILURE;
    }
#endif


    UT_status_t ut_result = UT_run_tests();

    if (result != UT_STATUS_OK || ut_result != UT_STATUS_OK)
    {
        result = UT_STATUS_FAILURE;
    }
    else
    {
        result = UT_STATUS_OK;
    }

    
    return result;
}

/** @} */ // End of UNIFIED_VTS_Halif_Test_Main
/** @} */ // End of UNIFIED_VTS_Halif_Test
/** @} */ // End of UNIFIED_VTS
/** @} */ // End of HPK
