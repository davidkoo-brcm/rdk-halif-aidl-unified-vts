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
# *
# * http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.
# *
#** ******************************************************************************

cmake_minimum_required(VERSION 3.10)
project(IAVBufferHelperSkeleton)

# Determine the workspace root (2 levels up from this CMakeLists.txt)
get_filename_component(WORKSPACE_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)

set(AVBUFFER_VERSION "${AVBUFFER_VERSION}" CACHE STRING "AVBuffer interface version")

message(STATUS "AVBUFFER_VERSION=${AVBUFFER_VERSION}")

if(NOT AVBUFFER_VERSION)
    message(FATAL_ERROR "AVBUFFER_VERSION is empty")
endif()
# Use absolute paths
set(HEADER_FILE_CANDIDATE "${WORKSPACE_ROOT}/rdk-halif-aidl/avbuffer/${AVBUFFER_VERSION}/avbufferhelper.h")
set(SKELETON_CPP "${CMAKE_BINARY_DIR}/IAVBufferHelper_skeleton.cpp")
set(SCRIPT_PATH "${CMAKE_CURRENT_SOURCE_DIR}/generate_skeleton.sh")

set(HEADER_FILE "${HEADER_FILE_CANDIDATE}")
get_filename_component(HEADER_INCLUDE_DIR "${HEADER_FILE}" DIRECTORY)
message(STATUS "HEADER_FILE=${HEADER_FILE}")
message(STATUS "HEADER_INCLUDE_DIR=${HEADER_INCLUDE_DIR}")

# Generate the skeleton .cpp file using full path to the script
add_custom_command(
    OUTPUT ${SKELETON_CPP}
    COMMAND ${CMAKE_COMMAND} -E echo "Running script: ${SCRIPT_PATH}"
    COMMAND ${CMAKE_COMMAND} -E env bash ${SCRIPT_PATH} ${HEADER_FILE} ${SKELETON_CPP}
    DEPENDS ${HEADER_FILE} ${SCRIPT_PATH}
    COMMENT "Generating skeleton implementation"
)

# Custom target to generate the file
add_custom_target(generate_skeleton DEPENDS ${SKELETON_CPP})

# Build the .so
add_library(avbufferhelper SHARED ${SKELETON_CPP})
add_dependencies(avbufferhelper generate_skeleton)
target_include_directories(avbufferhelper PUBLIC
    ${HEADER_INCLUDE_DIR}
)
