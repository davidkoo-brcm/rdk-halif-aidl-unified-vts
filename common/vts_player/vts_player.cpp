/**
 *  If not stated otherwise in this file or this component's LICENSE
 *  file the following copyright and licenses apply:
 *
 *  Copyright 2024 RDK Management
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
 * @addtogroup HPK Hardware Porting Kit
 * @{
 *
 */

/**
 * @addtogroup AV_MODULE AV pipeline Module
 * @{
 *
 */

/**
 * @defgroup AV_MODULE_HALTEST AV Module HAL Tests
 * @{
 *
 */

/**
 * @defgroup AV_MODULE_HALTEST_PLAYER AV Module HAL Tests Player abstract class
 * @{
 * @parblock
 *
 * ### Player Interface (Abstract Class) :
 *
 * This file contains Player Interface (Abstract Class).
 *
 * **Pre-Conditions:** @n
 * **Dependencies:** None@n
 *
 * @endparblock
 *
 */

/**
 * @file vts_player.cpp
 *
 */

#include "vts_player.h"
#include "vts_gstreamer_player.h"

// Table of available players
static const std::map<std::string, PlayerInfo> playerTable = {
    { "gstreamer", {
        []() { return std::make_unique<VTSGStreamerPlayer>(); },
        gstGlobalInitWrapper,
        gstGlobalDeinitWrapper
    } }
};

void VTSPlayer::globalInit(const std::string &type)
{
    auto it = playerTable.find(type);
    if (it != playerTable.end() && it->second.initFn)
    {
        if(it->second.initFn)
            it->second.initFn();
    }
}

void VTSPlayer::globalDeInit(const std::string &type)
{
    auto it = playerTable.find(type);
    if (it != playerTable.end() && it->second.deinitFn)
    {
        if(it->second.deinitFn)
            it->second.deinitFn();
    }
}

std::unique_ptr<VTSPlayer> VTSPlayer::create(const std::string &type)
{
    std::string lower = type;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);

    auto it = playerTable.find(lower);
    if (it != playerTable.end())
    {
        return it->second.createFn();
    }
    return nullptr;
}

std::vector<std::string> VTSPlayer::supportedPlayers()
{
    std::vector<std::string> names;
    for (const auto &entry : playerTable)
    {
        names.push_back(entry.first);
    }
    return names;
}

/** @} */ // End of AV_MODULE_HALTEST_PLAYER
/** @} */ // End of AV_MODULE_HALTEST
/** @} */ // End of AV_MODULE
/** @} */ // End of HPK