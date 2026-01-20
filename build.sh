#!/bin/bash
#* ******************************************************************************
#*  If not stated otherwise in this file or this component's LICENSE
#*  file the following copyright and licenses apply:
#*
#*  Copyright 2025 RDK Management
#*
#*  Licensed under the Apache License, Version 2.0 (the License);
#*  you may not use this file except in compliance with the License.
#*  You may obtain a copy of the License at
#*
#*  http://www.apache.org/licenses/LICENSE-2.0
#*
#*  Unless required by applicable law or agreed to in writing, software
#*  distributed under the License is distributed on an AS IS BASIS,
#*  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#*  See the License for the specific language governing permissions and
#*  limitations under the License.
#*
#* ******************************************************************************

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

declare -r TOP=`dirname $(realpath $0)`
declare -r HALIF_VERSION=current
RDK_HALIF_AIDL_VERSION="${RDK_HALIF_AIDL_VERSION="main"}"
RDK_HALIF_TEST_BASE_URL="https://github.com/rdkcentral/rdk-halif-aidl-test-"
VCOMPONENT_BASE_URL="ssh://git@github.code.rdkcentral.com/rdkcentral"
OUT_TAR_FILE=vts_unified.tar.gz.bz

declare -A HALIF_COMPONENTS=(
  [avbuffer]="current"
  [audiodecoder]="current"
  [audiosink]="current"
  [videodecoder]="current"
  [videosink]="current"
  [avclock]="current"
  [planecontrol]="current"
  [indicator]="current"
)

declare -A HALIF_TEST_COMPONENTS=(
  [avbuffer]="RDK_HALIF_AVBUFFER_TEST_VERSION"
  [audiodecoder]="RDK_HALIF_AUDIODECODER_TEST_VERSION"
  [audiosink]="RDK_HALIF_AUDIOSINK_TEST_VERSION"
  [videodecoder]="RDK_HALIF_VIDEODECODER_TEST_VERSION"
  [videosink]="RDK_HALIF_VIDEOSINK_TEST_VERSION"
  [avclock]="RDK_HALIF_AVCLOCK_TEST_VERSION"
  [planecontrol]="RDK_HALIF_PLANECONTROL_TEST_VERSION"
  [indicator]="RDK_HALIF_INDICATOR_TEST_VERSION"
)

: "${RDK_VCOMPONENT_DEFAULT_BRANCH:=main}"

declare -A VCOMPONENT_MODULES=(
    [indicator]="RDK_HALIF_INDICATOR_VCOMP_VERSION"
)

resolve_branch() {
    local component="$1"
    local var="RDK_VCOMPONENT_${component^^}"
    echo "${!var:-$RDK_VCOMPONENT_DEFAULT_BRANCH}"
}

# Define the directory where the repository will be cloned
declare -r UT_CORE_DIR="${TOP}/ut-core"
declare -r TOP_BUILD_DIR="${TOP}/build"
declare -r COMMON_DIR="${TOP}/common"
declare -r BUILD_INSTALL_PREFIX=${TOP_BUILD_DIR}/usr
declare -r AIDL_LIB_DIR=${TOP}/aidl_lib
declare -r RDK_HAL_DIR=${TOP}/rdk-halif-aidl
declare -r RDK_HAL_TEST_DIR=${TOP}/vts_hal_test_components
declare -r PROFILES_DIR=${TOP}/profiles
declare -r L4_TEST_DIR=${RDK_HAL_TEST_DIR}/l4_tests
declare -r AV_L4_TEST_DIR=${RDK_HAL_TEST_DIR}/l4_tests/src/av/
declare -r VCOMPONENT_DIR=${TOP}/vcomponents

#TODO: change to server path
declare -r DEF_GST_PATH="${TOP}/../gstreamer_pkg"
GST_PATH=${GST_PATH:-${DEF_GST_PATH}}

DEF_LINUX_BINDER="`realpath ${TOP}/../`/linux_binder_idl"
# AIDL_BIN: path of aidl compiler
AIDL_BIN=${AIDL_BIN:-${DEF_LINUX_BINDER}/out/aidl}
# LINUX_BINDER_OUT_DIR: output installed after building linux_binder_idl
# contains bin/servicemanager, lib/libbinder etc
LINUX_BINDER_OUT_DIR=${LINUX_BINDER_OUT_DIR:-${DEF_LINUX_BINDER}/local}

mkdir -p $TOP_BUILD_DIR

if [ ! -x $AIDL_BIN ]; then
    echo "AIDL_BIN: path does not exists, consider building the linux_binder_idl in $AIDL_BIN"
    exit 1
fi
if [ ! -d $LINUX_BINDER_OUT_DIR ]; then
    echo "LINUX_BINDER_OUT_DIR: path does not exists, consider building the linux_binder_idl in $DEF_LINUX_BINDER"
    exit 1
fi

declare -r AIDL_BIN=`realpath ${AIDL_BIN}`
declare -r LINUX_BINDER_OUT_DIR=`realpath ${LINUX_BINDER_OUT_DIR}`

# Parse Target argument (e.g., Target=arm or target=linux)
# Default to 'linux' if not provided
TARGET="linux"

###############################################################################
# Function to validate TARGET option
###############################################################################
for arg in "$@"; do
    if [[ $arg == [Tt]arget=* ]]; then
        TARGET="${arg#*=}"
    fi
done

# Validate TARGET
valid_targets=("linux" "arm")
if [[ ! " ${valid_targets[@]} " =~ " ${TARGET} " ]]; then
    echo -e "${BOLD}${RED}Invalid Target: $TARGET. Valid targets are: ${valid_targets[@]}${RESET}"
    help
    exit 1
fi

###############################################################################
# Function to clone  unified VTS repo's
###############################################################################
unified_manifest()
{
    echo "repo init unified manifest"
    repo init -b $(git rev-parse --abbrev-ref HEAD) -m aidl_unified_manifest.xml -u git@github.code.rdkcentral.com:rdkcentral/rdk-halif-aidl-unified-vts.git --no-repo-verify -q
    repo sync -cd -j 16 --no-repo-verify -q
}


###############################################################################
# Function to install linux-binder service manager, headers, and libraries
###############################################################################
install_linux_binder()
{
    echo "Install linux-binder 'service manager, headers and libraries'"
    install -d ${BUILD_INSTALL_PREFIX}/bin ${BUILD_INSTALL_PREFIX}/lib ${BUILD_INSTALL_PREFIX}/include
    install -t ${BUILD_INSTALL_PREFIX}/bin ${LINUX_BINDER_OUT_DIR}/bin/*
    install -t ${BUILD_INSTALL_PREFIX}/lib ${LINUX_BINDER_OUT_DIR}/lib/*
    cp -apr ${LINUX_BINDER_OUT_DIR}/include/* ${BUILD_INSTALL_PREFIX}/include/
}

###############################################################################
# Function to install gstreamer headers, and libraries
###############################################################################
install_gstreamer_pacakge()
{
    cp -r ${GST_PATH}/usr/lib/* ${TOP_BUILD_DIR}/usr/lib/
    cp -r ${GST_PATH}/usr/include/* ${TOP_BUILD_DIR}/usr/include/
}

###############################################################################
# Function to checkout the halif aidl repository and convert the aidl files
# to C++ headers
###############################################################################
generate_hal_interfaces()
{
    # Clone the repository if not already present
    if [ ! -d "$RDK_HAL_DIR" ]; then
        echo "Checking out version: " $RDK_HALIF_AIDL_VERSION
        git clone -b $RDK_HALIF_AIDL_VERSION 'http://git@github.com/rdkcentral/rdk-halif-aidl.git' $RDK_HAL_DIR
    fi

    # Iterate through the HALIF components
    for component in "${!HALIF_COMPONENTS[@]}"; do
        version=${HALIF_COMPONENTS[$component]}
        echo "Component: $component, Version: $version"

        HAL_TOP_BUILD_DIR=${TOP_BUILD_DIR}/${component}_aidl
        AIDL_GEN_DIR="${TOP_BUILD_DIR}/$HALIF_VERSION"

        cmake \
        -DAIDL_BIN=$AIDL_BIN \
        -DAIDL_GEN_DIR=$AIDL_GEN_DIR \
        -DAIDL_SRC_VERSION=$version \
        -DAIDL_TARGET=$component  \
        -B ${HAL_TOP_BUILD_DIR} \
        $RDK_HAL_DIR

        if [ $? -ne 0 ]; then
            echo -e "${BOLD}╔══════════════════════════════════════════════════════════════════════╗${RESET}"
            echo -e "${BOLD}* ${RED}Failed to Convert AIDL files for ${component}. Exiting.${RESET}"
            echo -e "${BOLD}╚══════════════════════════════════════════════════════════════════════╝${RESET}"
            exit 1
        fi
    done
}

###############################################################################
# Function to build AIDL libraries
###############################################################################
build_aidl_libs()
{
    pushd ${AIDL_LIB_DIR}
    make -j`nproc` TARGET=$TARGET VARIANT=CPP
    if [ $? -ne 0 ]; then
        echo -e "${BOLD}╔══════════════════════════════════════════════╗${RESET}"
        echo -e "${BOLD}* ${RED}Failed to build the AIDL Lib. Exiting.${RESET}       ${BOLD}*${RESET}"
        echo -e "${BOLD}╚══════════════════════════════════════════════╝${RESET}"
        exit 1
    fi
    popd
}

###############################################################################
# Function to clone and build the ut-core repository
###############################################################################
build_ut_core()
{
    if [ ! -d ${UT_CORE_DIR} ]; then
        git clone https://github.com/rdkcentral/ut-core.git ${UT_CORE_DIR}
        if [ $? -ne 0 ]; then
            echo "Failed to clone the repository. Exiting."
            exit 1
        fi
    fi

    pushd ${UT_CORE_DIR}

    git fetch -q -t origin
    # get the latest version of ut-core
    if [ -z "$UT_CORE_VERSION" ]; then
        UT_CORE_VERSION=`git tag | sort -Vr | head -n1`
    fi

    git checkout $UT_CORE_VERSION

    # Use the user-provided TARGET or default to 'linux'
    ./build.sh TARGET=$TARGET VARIANT=CPP
    if [ $? -ne 0 ]; then
        echo -e "${BOLD}╔══════════════════════════════════════════════╗${RESET}"
        echo -e "${BOLD}* ${RED}Failed to build the UT Core. Exiting.${RESET}        ${BOLD}*${RESET}"
        echo -e "${BOLD}╚══════════════════════════════════════════════╝${RESET}"
        exit 1
    fi

    popd
}

###############################################################################
# Function to generate the avbufferhelper skeleton
###############################################################################
generate_avbufferhelper_skeleton()
{
    declare -r AVBUFFER_HELPER_DIR=${COMMON_DIR}/avbufferhelper_skeleton
    mkdir -p $AVBUFFER_HELPER_DIR/build
    cd $AVBUFFER_HELPER_DIR/build

    cmake ..
    if [ $? -ne 0 ]; then
        echo -e "${BOLD}╔═══════════════════════════════════════════════════╗${RESET}"
        echo -e "${BOLD}* ${RED}Failed to generate av buffer skeleton. Exiting.${RESET}"
        echo -e "${BOLD}╚═══════════════════════════════════════════════════╝${RESET}"
        exit 1
    fi

    make
    if [ $? -ne 0 ]; then
        echo -e "${BOLD}╔══════════════════════════════════════════════════════╗${RESET}"
        echo -e "${BOLD}* ${RED}Failed to generate av buffer skeleton Lib. Exiting.${RESET}"
        echo -e "${BOLD}╚══════════════════════════════════════════════════════╝${RESET}"
        exit 1
    fi

    cp libavbufferhelper.so ${TOP_BUILD_DIR}/usr/lib/
    cd -
    rm -rf $AVBUFFER_HELPER_DIR/build
}

###############################################################################
# Function to Build mock services
###############################################################################
build_mock_services()
{
    for component in "${!HALIF_TEST_COMPONENTS[@]}"; do
        # Build the mock component
        make -j"$(nproc)" -C "${RDK_HAL_TEST_DIR}/${component}/mockservice" BUILD_DIR="${TOP_BUILD_DIR}"
        if [ $? -ne 0 ]; then
            echo -e "${BOLD}╔══════════════════════════════════════════════════════╗${RESET}"
            echo -e "${BOLD}* ${RED}Failed to build the mock ${component}. Exiting.${RESET}"
            echo -e "${BOLD}╚══════════════════════════════════════════════════════╝${RESET}"
            exit 1
        fi
    done
}

###############################################################################
# Function to Build HALIF test
###############################################################################
build_halif_test()
{
    # Build the tests
    make -j`nproc` -C ${TOP} TARGET=$TARGET VARIANT=CPP
    if [ $? -ne 0 ]; then
        echo -e "${BOLD}╔════════════════════════════════════════════╗${RESET}"
        echo -e "${BOLD}* ${RED}Failed to build the main tests. Exiting.${RESET}"
        echo -e "${BOLD}╚════════════════════════════════════════════╝${RESET}"
        exit 1
    fi
}

###############################################################################
# Function to install test binaries and scripts to the build directory
###############################################################################
install_test()
{
    declare -r INSTALL_PATH=${TOP_BUILD_DIR}/bin

    install -t ${INSTALL_PATH} ${TOP_BUILD_DIR}/usr/bin/*
    install -t ${INSTALL_PATH} ${TOP_BUILD_DIR}/usr/lib/*
    install -t ${INSTALL_PATH} run.sh
    install -t ${INSTALL_PATH} start_services.sh

    cp -r ${PROFILES_DIR} ${INSTALL_PATH}

    for component in "${!HALIF_TEST_COMPONENTS[@]}"; do
        if [ -d "${RDK_HAL_TEST_DIR}/${component}/${component}_test_configuration" ]; then
            cp -rf ${RDK_HAL_TEST_DIR}/${component}/${component}_test_configuration ${INSTALL_PATH}/
        fi
        if [ -d "${RDK_HAL_TEST_DIR}/${component}/stream_configuration" ]; then
            cp -rf ${RDK_HAL_TEST_DIR}/${component}/stream_configuration ${INSTALL_PATH}/
        fi
        if [ -d "${RDK_HAL_TEST_DIR}/${component}/${component}_stream_configuration" ]; then
            cp -rf ${RDK_HAL_TEST_DIR}/${component}/${component}_stream_configuration ${INSTALL_PATH}/
        fi
        if [ -d "${RDK_HAL_TEST_DIR}/${component}/profiles" ]; then
            cp -rf ${RDK_HAL_TEST_DIR}/${component}/profiles ${INSTALL_PATH}/
        fi
    done
    cp -rf ${L4_TEST_DIR}/av_test_configurations ${INSTALL_PATH}/

    for component in "${!VCOMPONENT_MODULES[@]}"; do
        if [ -d "${VCOMPONENT_DIR}/rdk-aidl-vcomponent-${component}" ]; then
            cp -rf ${VCOMPONENT_DIR}/rdk-aidl-vcomponent-${component}/vcomponent_configurations ${INSTALL_PATH}/
        fi
    done

    mkdir -p ${INSTALL_PATH}/assets/streams/input
    mkdir -p ${INSTALL_PATH}/assets/streams/reference
    rm -rf ${INSTALL_PATH}/libavbufferhelper.so

    cd ${TOP_BUILD_DIR}
    tar cfz ${OUT_TAR_FILE} bin/
    cd -
}

#TODO: This function needs to be removed, once the vcomponent is available in vDevice
###############################################################################
# Function to install and build vcomponent services
###############################################################################

build_vcomponent_services()
{
    mkdir -p "${VCOMPONENT_DIR}" || return 1

    for component in "${!VCOMPONENT_MODULES[@]}"; do
        local repo="rdk-aidl-vcomponent-${component}"
        local repo_dir="${VCOMPONENT_DIR}/${repo}"
        local branch
        branch="$(resolve_branch "$component")"

        echo -e "${BOLD}Building ${repo} [branch: ${branch}]${RESET}"

        # Clone if missing
        if [[ ! -d "${repo_dir}/.git" ]]; then
            git clone "${VCOMPONENT_BASE_URL}/${repo}.git" "${repo_dir}"
            if [ $? -ne 0 ]; then
                echo -e "${BOLD}╔══════════════════════════════════════════════════════╗${RESET}"
                echo -e "${BOLD}* ${RED}Failed to clone ${repo}. Exiting.${RESET}"
                echo -e "${BOLD}╚══════════════════════════════════════════════════════╝${RESET}"
                return 1
            fi
        fi

        pushd "${repo_dir}" >/dev/null

        git fetch origin || exit 1

        git checkout "${branch}" 2>/dev/null \
            || git checkout -b "${branch}" "origin/${branch}" || {
                echo -e "${BOLD}${RED}Branch '${branch}' not found in ${repo}${RESET}"
                exit 1
            }

        git pull origin "${branch}" || exit 1

        make -j"$(nproc)" \
            BUILD_DIR="${TOP_BUILD_DIR}" \
            UT_CORE_DIR="${UT_CORE_DIR}" || {
                echo -e "${BOLD}╔════════════════════════════════════════════════╗${RESET}"
                echo -e "${BOLD}* ${RED}Failed to build the vcomponent Service. Exiting.${RESET}"
                echo -e "${BOLD}╚════════════════════════════════════════════════╝${RESET}"
                exit 1
            }

        popd >/dev/null
    done
}
###############################################################################
# Function to clean the test build directory
###############################################################################
clean_test()
{
    rm -rf ${TOP}/test/*.o
    for component in "${!HALIF_TEST_COMPONENTS[@]}"; do
        rm -rf ${RDK_HAL_TEST_DIR}/${component}/mockservice/src/*.o
        rm -rf ${RDK_HAL_TEST_DIR}/${component}/src/*.o
    done

    rm -rf ${AV_L4_TEST_DIR}/*.o
    rm -rf ${COMMON_DIR}/helper_functions/*.o
    rm -rf ${COMMON_DIR}/vts_player/*.o

    find "$VCOMPONENT_DIR" -type f -name "*.o" -delete
    find "$RDK_HAL_TEST_DIR" -type f -name "*.o" -delete
    find "$TOP_BUILD_DIR" -type f -name "*.o" -delete
}

###############################################################################
# Function to clean the test build directory
###############################################################################
dist_clean_test()
{
    clean_test
    rm -rf $TOP_BUILD_DIR
    rm -rf $RDK_HAL_DIR
    rm -rf ${UT_CORE_DIR}
    rm -rf $RDK_HAL_TEST_DIR
    rm -rf $VCOMPONENT_DIR #TODO: Remove this when vDevice is completely done
    rm -rf .repo
}

###############################################################################
# help function to display usage information
###############################################################################
help()
{
    echo -e "${BOLD}${CYAN}Usage:${RESET}"

    echo -e "${BOLD}╔════════════════════════════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${BOLD}* ${GREEN}$0 Target=<target>${RESET} ${YELLOW}- Builds the test for specified target (arm, linux)${RESET} ${BOLD}*${RESET}"
    echo -e "${BOLD}* ${GREEN}$0 clean${RESET}           ${YELLOW}- Cleans the build folder${RESET}                           ${BOLD}*${RESET}"
    echo -e "${BOLD}* ${GREEN}$0 dist_clean${RESET}      ${YELLOW}- Deletes all build and checkout folders${RESET}            ${BOLD}*${RESET}"
    echo -e "${BOLD}* ${GREEN}$0 help/-h/--help${RESET}  ${YELLOW}- Prints this message${RESET}                               ${BOLD}*${RESET}"
    echo -e "${BOLD}╚════════════════════════════════════════════════════════════════════════════════╝${RESET}"
}

echo -e "${BOLD}${GREEN}VTS Unified Version    : ${RESET}${YELLOW}$(git rev-parse --abbrev-ref HEAD)${RESET}"
echo -e "${BOLD}${GREEN}UT_CORE_VERSION        : ${RESET}${YELLOW}$UT_CORE_VERSION${RESET}"
echo -e "${BOLD}${GREEN}RDK_HALIF_AIDL_VERSION : ${RESET}${YELLOW}$RDK_HALIF_AIDL_VERSION${RESET}"
echo -e "${BOLD}${GREEN}AIDL_BIN               : ${RESET}${YELLOW}$AIDL_BIN${RESET}"
echo -e "${BOLD}${GREEN}LINUX_BINDER_OUT_DIR   : ${RESET}${YELLOW}$LINUX_BINDER_OUT_DIR${RESET}"
echo -e "${BOLD}${GREEN}TARGET                 : ${RESET}${YELLOW}$TARGET${RESET}"

###############################################################################
# Main script execution starts here
###############################################################################
if [ "$1" == "clean" ]; then
    clean_test
elif [ "$1" == "dist_clean" ]; then
    dist_clean_test
elif [ "$1" == "help" ] || [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    help
elif [[ "$1" == [Tt]arget=* ]]; then
    unified_manifest
    install_linux_binder
    install_gstreamer_pacakge
    generate_hal_interfaces
    build_aidl_libs
    build_ut_core
    generate_avbufferhelper_skeleton
    build_halif_test
    build_vcomponent_services
    install_test
else
    echo -e "${BOLD}${RED}Invalid Arguments${RESET}"
    help
fi
