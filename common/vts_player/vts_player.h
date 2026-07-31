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
 * @defgroup AV_MODULE_HALTEST_PLAYER_H AV Module HAL Tests Player abstract class
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
 * @file vts_player.h
 *
 */

#ifndef __VTS_PLAYER_H__
#define __VTS_PLAYER_H__

#include <string>
#include <memory>
#include <vector>
#include <algorithm>
#include <functional>
#include <map>

class VTSPlayer
{
public:
    virtual ~VTSPlayer() = default;

    /* Initializes the Player */
    virtual bool init() = 0;

    /* Start Playing the given URI */
    virtual bool play(const std::string &streamPath) = 0;

    /* Pause the playback */
    virtual void pause() = 0;

    /* Resume the playback */
    virtual void resume() = 0;

    /* Trick mode with the given speed 0.5, 1.0, 2.0, 4.0 */
    virtual void trickMode(float speed) = 0;

    /* Seek to the given offset in milliseconds */
    virtual void seek(int64_t offset_ms) = 0;

    /* Stop the playback */
    virtual void stop() = 0;

    /* Main loop to handle events and wait for the playback to finish */
    virtual void loop() = 0;

    /* Close the player and free resources */
    virtual void close() = 0;
	
    /* Switch audio track on the fly  */
    virtual bool switchAudioTrack(uint32_t trackIndex) = 0;

    /* Switch video channel on the fly  */
    virtual bool switchVideoTrack(uint32_t trackIndex) = 0;

    /* Factory method to create a player of the given type */
    static std::unique_ptr<VTSPlayer> create(const std::string &type);

    /* Returns the list of supported player types */
    static std::vector<std::string> supportedPlayers();

    /* Global init/deinit for player type */
    static void globalInit(const std::string &type);

    /* Global deinit for player type */
    static void globalDeInit(const std::string &type);
};

/* Type alias for a function that creates a Player */
using PlayerFactoryFn = std::function<std::unique_ptr<VTSPlayer>()>;

/* Init/Deinit function pointer type */
using InitFn = void(*)(void);
using DeinitFn = void(*)(void);

/* Struct to hold all info about a player type */
struct PlayerInfo
{
    PlayerFactoryFn createFn;
    InitFn initFn;
    DeinitFn deinitFn;
};

#endif //__VTS_PLAYER_H__

/** @} */ // End of AV_MODULE_HALTEST_PLAYER_H
/** @} */ // End of AV_MODULE_HALTEST
/** @} */ // End of AV_MODULE
/** @} */ // End of HPK
