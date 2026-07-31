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
 */

/**
 * @defgroup AV_MODULE_HALTEST_GST_PLAYER_H AV Module HAL Tests Gstreamer Player class
 * @{
 * @parblock
 *
 * ### Gstreamer Player Interface:
 *
 * This file contains Gstreamer Player Interface.
 *
 * **Pre-Conditions:** @n
 * **Dependencies:** None@n
 *
 * @endparblock
 *
 */

/**
 * @file vts_gstreamer_player.h
 *
 */

#ifndef __VTS_GST_PLAYER_H__
#define __VTS_GST_PLAYER_H__

#include "vts_player.h"
#include <gst/gst.h>
#include <string>

class VTSGStreamerPlayer : public VTSPlayer
{
public:
    VTSGStreamerPlayer();
    ~VTSGStreamerPlayer() override;

    bool init() override;
    bool play(const std::string &streamPath) override;
    void pause() override;
    void resume() override;
    void trickMode(float speed) override;
    void seek(int64_t offset_ms) override;
    void stop() override;
    void loop() override;
    void close() override;
	
	// Switch audio track on the fly
    bool switchAudioTrack(uint32_t trackIndex) override;

	// Switch video channel on the fly
    bool switchVideoTrack(uint32_t trackIndex) override;

private:
    // Helper methods for dynamic replugging
    void configAudioPipe(GstCaps *newAudioCaps);
    void reconfigAudioPipe(GstCaps *newAudioCaps);

    // GStreamer signal callbacks kept for old SDK RDKE impementation
    // static void deepElementAddedCallback(GstBin *bin, GstBin *sub_bin, GstElement *element, gpointer user_data);
    // static void typeFoundCallback(GstElement *typefind, guint probability, const GstCaps *caps, gpointer user_data);
	
private:
    GstElement *playbin;
    GstBus *bus;
    bool terminate;
	
	// Track audio decoders, parsers, and sinks for OTF switching
    GstElement *curAudioDecodeBin;
    GstElement *curAudioTypefind;
    GstElement *curAudioParse;
    GstElement *curAudioDecoder;
    GstElement *curAudioPlaysinkBin;
    GstElement *mCurAudioSink;
    bool isAudioAAC_current;
    bool linkTypefindParser;
    guint mNumAudioTracks = 0;
    guint mCurrentAudioTrack = 0;
};

void gstGlobalInitWrapper();
void gstGlobalDeinitWrapper();

#endif //__VTS_GST_PLAYER_H__

/** @} */ // End of AV_MODULE_HALTEST_GST_PLAYER_H
/** @} */ // End of AV_MODULE_HALTEST_PLAYER_H
/** @} */ // End of AV_MODULE_HALTEST
/** @} */ // End of AV_MODULE
/** @} */ // End of HPK
