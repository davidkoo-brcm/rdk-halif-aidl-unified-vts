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
UT_CORE_DEFAULT_VERSION="5.1.0"
export UT_CORE_VERSION="${UT_CORE_VERSION:-${UT_CORE_DEFAULT_VERSION}}"
RDK_HALIF_TEST_BASE_URL="https://github.com/rdkcentral/rdk-halif-aidl-test-"
OUT_TAR_FILE=vts_unified.tar.gz.bz

declare -A HALIF_TEST_COMPONENTS=(
  [avbuffer]="RDK_HALIF_AVBUFFER_TEST_VERSION"
  [audiodecoder]="RDK_HALIF_AUDIODECODER_TEST_VERSION"
  [audiosink]="RDK_HALIF_AUDIOSINK_TEST_VERSION"
  [videodecoder]="RDK_HALIF_VIDEODECODER_TEST_VERSION"
  [videosink]="RDK_HALIF_VIDEOSINK_TEST_VERSION"
  [avclock]="RDK_HALIF_AVCLOCK_TEST_VERSION"
  [planecontrol]="RDK_HALIF_PLANECONTROL_TEST_VERSION"
  [hdmicec]="RDK_HALIF_CEC_TEST_VERSION"
  [hdmiinput]="RDK_HALIF_HDMIINPUT_TEST_VERSION"
  [hdmioutput]="RDK_HALIF_HDMIOUTPUT_TEST_VERSION"
  [deepsleep]="RDK_HALIF_DEEPSLEEP_TEST_VERSION"
  [deviceinfo]="RDK_HALIF_DEVICEINFO_TEST_VERSION"
  [boot]="RDK_HALIF_BOOT_TEST_VERSION"
  [flash]="RDK_HALIF_FLASH_TEST_VERSION"
  [indicator]="RDK_HALIF_INDICATOR_TEST_VERSION"
  [audiomixer]="RDK_HALIF_AUDIOMIXER_TEST_VERSION"
  [cdm]="RDK_HALIF_CDM_TEST_VERSION"
  [broadcast]="RDK_HALIF_BROADCAST_TEST_VERSION"
  [panel]="RDK_HALIF_PANEL_TEST_VERSION"
  [farfieldvoice]="RDK_HALIF_FARFIELDVOICE_TEST_VERSION"
)

# Define the directory where the repository will be cloned
declare -r UT_CORE_DIR="${TOP}/ut-core"
declare -r TOP_BUILD_DIR="${TOP}/build"
declare -r COMMON_DIR="${TOP}/common"
declare -r BUILD_INSTALL_PREFIX=${TOP_BUILD_DIR}/usr
declare -r RDK_HAL_DIR=${TOP}/rdk-halif-aidl
declare -r RDK_HAL_TEST_DIR=${TOP}/vts_hal_test_components
declare -r PROFILES_DIR=${TOP}/profiles
declare -r L4_TEST_DIR=${RDK_HAL_TEST_DIR}/l4_tests
declare -r AV_L4_TEST_DIR=${RDK_HAL_TEST_DIR}/l4_tests/src/av/

#TODO: change to server path
DEF_GST_LIB_PATH="`realpath ${TOP}/../`/gstreamer_aidl_package/build/install"
GST_LIB_PATH=${GST_LIB_PATH:-${DEF_GST_LIB_PATH}}

#TODO: change to server path
declare -r DEF_EGL_LIB_PATH="${TOP}/../egl_pkg"
EGL_LIB_PATH=${EGL_LIB_PATH:-${DEF_EGL_LIB_PATH}}

mkdir -p $TOP_BUILD_DIR

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
# Function to validate and set GST_LIB_PATH
###############################################################################
validate_gst_lib_path()
{
    # Resolve GST_LIB_PATH to absolute path before validation
    if [ -n "$GST_LIB_PATH" ]; then
        GST_LIB_PATH=`realpath ${GST_LIB_PATH}` 2>/dev/null || GST_LIB_PATH=""
    fi

    if [ ! -d "$GST_LIB_PATH" ]; then
        echo "GST_LIB_PATH: path does not exists, consider building the GST_LIB_PATH in $DEF_GST_LIB_PATH"
        exit 1
    fi
}

###############################################################################
# Function to validate and set EGL_LIB_PATH
###############################################################################
validate_egl_lib_path()
{
    # Resolve EGL_LIB_PATH to absolute path before validation
    if [ -n "$EGL_LIB_PATH" ]; then
        EGL_LIB_PATH=`realpath ${EGL_LIB_PATH}` 2>/dev/null || EGL_LIB_PATH=""
    fi

    if [ ! -d "$EGL_LIB_PATH" ]; then
        echo "EGL_LIB_PATH: path does not exists, consider building the EGL_LIB_PATH in $DEF_EGL_LIB_PATH"
        exit 1
    fi
}

###############################################################################
# Function to clone  unified VTS repo's
###############################################################################
unified_manifest()
{
    if [ -d "${RDK_HAL_TEST_DIR}" ] && [ -n "$(ls -A ${RDK_HAL_TEST_DIR} 2>/dev/null)" ]; then
        echo "Manifest already synced, skipping repo sync"
        return
    fi
    local BRANCH
    BRANCH=$(git rev-parse --abbrev-ref HEAD) || {
        echo "ERROR: Failed to determine current branch. Is the repo in a detached HEAD state?"
        exit 1
    }
    if [ "${BRANCH}" = "HEAD" ]; then
        echo "ERROR: Detached HEAD state detected — cannot determine branch for repo init."
        exit 1
    fi
    echo "repo init unified manifest"
    repo init -b "${BRANCH}" -m aidl_unified_manifest.xml -u https://github.com/rdkcentral/rdk-halif-aidl-unified-vts.git --no-repo-verify -q || {
        echo "ERROR: repo init failed."
        exit 1
    }
    repo sync -cd -j 16 --no-repo-verify -q || {
        echo "ERROR: repo sync failed."
        exit 1
    }
}

###############################################################################
# Install Binder service manager, headers and libraries into build/usr/ from
# the rdk-halif-aidl Binder SDK (built by build_modules.sh -> build_binder.sh).
# Must be called after generate_hal_interfaces().
###############################################################################
install_linux_binder()
{
    local BINDER_SDK="${RDK_HAL_DIR}/out/target"
    local BINDER_INC="${RDK_HAL_DIR}/out/build"

    echo "Install binder 'service manager, headers and libraries'"
    install -d ${BUILD_INSTALL_PREFIX}/bin ${BUILD_INSTALL_PREFIX}/lib ${BUILD_INSTALL_PREFIX}/include

    if [ -d "${BINDER_SDK}/bin" ]; then
        find "${BINDER_SDK}/bin" -maxdepth 1 -type f -executable \
            -exec install -t ${BUILD_INSTALL_PREFIX}/bin {} \; 2>/dev/null || true
    fi

    if [ -d "${BINDER_SDK}/lib/binder" ]; then
        find "${BINDER_SDK}/lib/binder" -maxdepth 1 \( -name "*.so" -o -name "*.so.*" \) \
            -exec install -t ${BUILD_INSTALL_PREFIX}/lib {} \; 2>/dev/null || true
    fi

    if [ -d "${BINDER_INC}/include/binder_sdk" ]; then
        cp -apr ${BINDER_INC}/include/binder_sdk/. ${BUILD_INSTALL_PREFIX}/include/
    fi
}

###############################################################################
# Function to install gstreamer headers, and libraries
###############################################################################
install_gstreamer_package()
{
    cp -r ${GST_LIB_PATH}/usr/lib/* ${TOP_BUILD_DIR}/usr/lib/
    cp -r ${GST_LIB_PATH}/usr/include/* ${TOP_BUILD_DIR}/usr/include/
}

###############################################################################
# Function to install egl headers, and libraries
###############################################################################
install_egl_package()
{
    cp -r ${EGL_LIB_PATH}/usr/lib/* ${TOP_BUILD_DIR}/usr/lib/
    cp -r ${EGL_LIB_PATH}/usr/include/* ${TOP_BUILD_DIR}/usr/include/
}

###############################################################################
# Cross-compile ARM binder runtime (libbinder.so, libutils.so, etc.) from
# the linux_binder_idl sources using the ARM cross-compiler.
#
# build_modules.sh intentionally does not build binder for ARM — it expects
# the linux-binder Yocto recipe to pre-stage it. For standalone ARM builds
# outside Yocto, we cross-compile it here with BUILD_HOST_AIDL=OFF so only
# the runtime libs are built (skipping the AIDL host tools that require a
# host/x86 compiler).
###############################################################################
build_arm_binder()
{
    local BINDER_REPO_DIR="${RDK_HAL_DIR}/build-tools/linux_binder_idl"
    local ARM_BINDER_BUILD="${RDK_HAL_DIR}/build/binder-arm"
    local ARM_BINDER_SDK="${RDK_HAL_DIR}/out/target"

    if [ -f "${ARM_BINDER_SDK}/.sdk_ready" ]; then
        echo "ARM Binder SDK already built at ${ARM_BINDER_SDK}"
        return 0
    fi

    # Clone linux_binder_idl directly — not via build_binder.sh.
    # build_binder.sh would try to build the full host AIDL compiler, but OE
    # prepends its own native tools (including an older m4) to PATH even when
    # CC/CXX are unset — that m4 rejects the --gnu flag bison passes and
    # breaks the AIDL parser build.  A plain git clone avoids PATH entirely.
    if [ ! -d "${BINDER_REPO_DIR}/.git" ]; then
        echo "Cloning linux_binder_idl for ARM build..."
        local _binder_version
        _binder_version=$(grep -vE '^[[:space:]]*(#|$)' \
            "${RDK_HAL_DIR}/binder_sdk.version" 2>/dev/null \
            | head -1 | tr -d '[:space:]')
        _binder_version="${_binder_version:-2.0.0}"

        [ -d "${BINDER_REPO_DIR}" ] && rm -rf "${BINDER_REPO_DIR}"
        mkdir -p "${RDK_HAL_DIR}/build-tools"
        git clone "https://github.com/rdkcentral/linux_binder_idl" \
            "${BINDER_REPO_DIR}" || {
            echo "ERROR: Failed to clone linux_binder_idl."
            exit 1
        }
        ( cd "${BINDER_REPO_DIR}" && \
          git checkout "${_binder_version}" 2>/dev/null || \
          echo "Note: version ${_binder_version} not found, using default branch" )

        # Clone Android binder sources required by the cmake build
        ( cd "${BINDER_REPO_DIR}" && bash ./clone-android-binder-repo.sh ) || {
            echo "ERROR: Failed to clone Android binder sources."
            exit 1
        }
    fi

    # The OE toolchain sets CC/CXX to "compiler-path <flags>" (flags embedded).
    # cmake requires CMAKE_C_COMPILER to be just the binary path; flags go into
    # CMAKE_C_FLAGS_INIT inside a toolchain file.
    #
    # cmake 3.22+ auto-loads OEToolchainConfig.cmake even when CMAKE_TOOLCHAIN_FILE
    # is cleared. Writing our own toolchain file takes precedence over that.
    local cc_bin cxx_bin cc_flags
    cc_bin=$(echo "${CC}" | awk '{print $1}')
    cxx_bin=$(echo "${CXX}" | awk '{print $1}')
    cc_flags=$(echo "${CC}" | cut -d' ' -f2-)   # flags embedded in CC by OE

    mkdir -p "${ARM_BINDER_BUILD}"
    local TOOLCHAIN_FILE="${ARM_BINDER_BUILD}/arm-cross.cmake"
    cat > "${TOOLCHAIN_FILE}" <<TOOLCHAIN_EOF
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR arm)
set(CMAKE_C_COMPILER   "${cc_bin}")
set(CMAKE_CXX_COMPILER "${cxx_bin}")
set(CMAKE_C_FLAGS_INIT   "${cc_flags} ${CFLAGS:-}")
set(CMAKE_CXX_FLAGS_INIT "${cc_flags} ${CXXFLAGS:-}")
set(CMAKE_EXE_LINKER_FLAGS_INIT    "${LDFLAGS:-}")
set(CMAKE_SHARED_LINKER_FLAGS_INIT "${LDFLAGS:-}")
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
TOOLCHAIN_EOF

    # linux_binder_idl cmake auto-enables BUILD_ENV_YOCTO when OECORE_* env
    # vars are set (line 174 of its CMakeLists.txt), which skips ALL install()
    # rules so cmake never installs libs or headers.  Temporarily clear these
    # vars during cmake configure so BUILD_ENV_YOCTO stays OFF.  The sysroot
    # path is baked into our toolchain file's CMAKE_C_FLAGS_INIT, so clearing
    # the OE detection vars does not affect cross-compilation.
    local _OECORE_NATIVE="${OECORE_NATIVE_SYSROOT:-}"
    local _OECORE_TARGET="${OECORE_TARGET_SYSROOT:-}"
    unset OECORE_NATIVE_SYSROOT OECORE_TARGET_SYSROOT

    echo "Cross-compiling ARM binder runtime (BUILD_HOST_AIDL=OFF)..."
    echo "  Compiler: ${cc_bin}"
    echo "  Flags:    ${cc_flags} ${CFLAGS:-}"
    cmake -S "${BINDER_REPO_DIR}" \
          -B "${ARM_BINDER_BUILD}" \
          -DCMAKE_INSTALL_PREFIX="${ARM_BINDER_SDK}" \
          -DCMAKE_BUILD_TYPE=Release \
          -DBUILD_HOST_AIDL=OFF \
          -DBUILD_ENV_YOCTO=OFF \
          -DCMAKE_TOOLCHAIN_FILE="${TOOLCHAIN_FILE}"
    local cmake_cfg_rc=$?

    # Restore OE env vars before any further steps
    [ -n "${_OECORE_NATIVE}" ] && export OECORE_NATIVE_SYSROOT="${_OECORE_NATIVE}"
    [ -n "${_OECORE_TARGET}" ] && export OECORE_TARGET_SYSROOT="${_OECORE_TARGET}"

    if [ $cmake_cfg_rc -ne 0 ]; then
        echo "ERROR: ARM binder cmake configuration failed."
        exit 1
    fi
    cmake --build "${ARM_BINDER_BUILD}" -j"$(nproc)" || {
        echo "ERROR: ARM binder build failed."
        exit 1
    }
    cmake --install "${ARM_BINDER_BUILD}" || {
        echo "ERROR: ARM binder install failed."
        exit 1
    }

    # Reorganise the install tree to match what build_binder.sh produces for
    # the linux target, so that build_modules.sh finds the SDK at the expected
    # paths (out/target/lib/binder/, out/build/include/binder_sdk/).
    # Always wipe lib/binder/ — Step 1 (x86 build) may have put x86_64 libs here.
    local ARM_BINDER_INCLUDE="${RDK_HAL_DIR}/out/build"
    if [ -d "${ARM_BINDER_SDK}/lib" ]; then
        rm -rf "${ARM_BINDER_SDK}/lib/binder"
        mkdir -p "${ARM_BINDER_SDK}/lib/binder"
        mv "${ARM_BINDER_SDK}"/lib/*.so* "${ARM_BINDER_SDK}/lib/binder/" 2>/dev/null || true
    fi
    if [ -d "${ARM_BINDER_SDK}/include" ]; then
        mkdir -p "${ARM_BINDER_INCLUDE}/include/binder_sdk"
        find "${ARM_BINDER_SDK}/include" -mindepth 1 -maxdepth 1 -type d \
            -exec mv {} "${ARM_BINDER_INCLUDE}/include/binder_sdk/" \; 2>/dev/null || true
        find "${ARM_BINDER_SDK}/include" -maxdepth 1 -type f -name "*.h" \
            -exec mv {} "${ARM_BINDER_INCLUDE}/include/binder_sdk/" \; 2>/dev/null || true
        rmdir "${ARM_BINDER_SDK}/include" 2>/dev/null || true
    fi
    mkdir -p "${ARM_BINDER_SDK}/lib/halif"
    touch "${ARM_BINDER_SDK}/.sdk_ready"
    touch "${ARM_BINDER_INCLUDE}/.sdk_ready"
    echo "ARM Binder SDK built and installed to ${ARM_BINDER_SDK}"
}

###############################################################################
# Create convenience softlinks so the Makefile can link with -l<module>-cpp
# without embedding the version number:
#   lib<module>-cpp.so  ->  lib<module>-v<version>-cpp.so
# Versions are read from rdk-halif-aidl/versions_released.yaml.
###############################################################################
create_halif_softlinks()
{
    local YAML="${RDK_HAL_DIR}/versions_released.yaml"
    local LIB_DIR="${RDK_HAL_DIR}/out/target/lib/halif"
    local in_components=0

    if [ ! -f "$YAML" ]; then
        echo "Warning: versions_released.yaml not found, skipping softlink creation"
        return
    fi

    echo "Creating halif library softlinks..."
    while IFS= read -r line; do
        if [[ "$line" =~ ^components: ]]; then
            in_components=1
            continue
        fi
        if [[ $in_components -eq 1 ]]; then
            if [[ "$line" =~ ^[[:space:]]+([A-Za-z0-9_]+):[[:space:]]*([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+) ]]; then
                local module="${BASH_REMATCH[1]}"
                local version="${BASH_REMATCH[2]}"
                local versioned="lib${module}-v${version}-cpp.so"
                local link="lib${module}-cpp.so"
                if [ -f "${LIB_DIR}/${versioned}" ]; then
                    ln -sf "${versioned}" "${LIB_DIR}/${link}"
                    echo "  ${link} -> ${versioned}"
                fi
            elif [[ "$line" =~ ^[^[:space:]] && ! "$line" =~ ^# ]]; then
                in_components=0
            fi
        fi
    done < "$YAML"
}

###############################################################################
# Clone rdk-halif-aidl and build HAL interfaces using its own build system.
#
# build_modules.sh manifest:
#   - Auto-invokes build_binder.sh (Stage 1) if the Binder SDK is not yet built
#   - Reads versions_released.yaml and compiles each component's pre-committed
#     C++ from the pinned versioned snapshot into lib<module>-v<version>-cpp.so
#   - Outputs libraries to rdk-halif-aidl/out/target/lib/halif/
#   - Outputs headers  to rdk-halif-aidl/out/build/include/<module>/<version>/include/
#
# For ARM cross-compilation set CC/CXX/CFLAGS/CXXFLAGS/LDFLAGS in the
# environment and BINDER_SDK_DIR to the ARM-compiled Binder SDK location.
###############################################################################
generate_hal_interfaces()
{
    # rdk-halif-aidl is not in the repo manifest — clone it if not present.
    if [ ! -d "$RDK_HAL_DIR" ]; then
        echo "Cloning rdk-halif-aidl..."
        git clone https://github.com/rdkcentral/rdk-halif-aidl.git "$RDK_HAL_DIR"
        if [ $? -ne 0 ]; then
            echo "ERROR: Failed to clone rdk-halif-aidl."
            exit 1
        fi
    fi

    # build_modules.sh preflight check requires out/target/lib/binder to exist before
    # it can run, so build_binder.sh must be called explicitly first.
    # TODO: build_modules.sh to skip the preflight binder check in manifest mode.
    local binder_toolchain_dir="${RDK_HAL_DIR}/build-tools/linux_binder_idl"
    if [ "${TARGET}" = "arm" ]; then
        # For ARM: if BINDER_SDK_DIR is already set (e.g. Yocto sysroot), use it.
        # Otherwise two steps are needed:
        #   Step 1 — clear ARM env and call build_binder.sh with x86 gcc to build
        #            the AIDL host compiler tools.
        #   Step 2 — restore ARM env and call build_arm_binder() with BUILD_HOST_AIDL=OFF
        #            to cross-compile the ARM binder runtime.
        if [ -z "${BINDER_SDK_DIR:-}" ]; then
            if [ -n "${OECORE_TARGET_SYSROOT:-}" ] && [ -d "${OECORE_TARGET_SYSROOT}/usr/lib/binder" ]; then
                export BINDER_SDK_DIR="${OECORE_TARGET_SYSROOT}/usr"
                echo "ARM build: using OE sysroot binder SDK at ${BINDER_SDK_DIR}"
            else
                # Step 1: build AIDL host tools using x86 compiler.
                # Clear ARM cross-compile env AND OECORE vars — linux_binder_idl
                # CMakeLists.txt auto-sets BUILD_ENV_YOCTO=ON when OECORE_* vars
                # are present, which skips all cmake install() rules.
                echo "ARM build: building AIDL host tools with x86 compiler..."
                local _CC="${CC:-}" _CXX="${CXX:-}" _CFLAGS="${CFLAGS:-}"
                local _CXXFLAGS="${CXXFLAGS:-}" _LDFLAGS="${LDFLAGS:-}"
                local _ARCH="${ARCH:-}" _CMAKE_TOOLCHAIN_FILE="${CMAKE_TOOLCHAIN_FILE:-}"
                local _OECORE_NATIVE="${OECORE_NATIVE_SYSROOT:-}"
                local _OECORE_TARGET="${OECORE_TARGET_SYSROOT:-}"
                unset CC CXX CFLAGS CXXFLAGS LDFLAGS ARCH CMAKE_TOOLCHAIN_FILE
                unset OECORE_NATIVE_SYSROOT OECORE_TARGET_SYSROOT
                export M4=/usr/bin/m4
                (
                    cd "${RDK_HAL_DIR}"
                    ./build_binder.sh
                ) || {
                    echo "ERROR: build_binder.sh (host tools) failed."
                    exit 1
                }
                # Restore ARM cross-compile environment.
                [ -n "${_CC}" ]                   && export CC="${_CC}"
                [ -n "${_CXX}" ]                  && export CXX="${_CXX}"
                [ -n "${_CFLAGS}" ]               && export CFLAGS="${_CFLAGS}"
                [ -n "${_CXXFLAGS}" ]             && export CXXFLAGS="${_CXXFLAGS}"
                [ -n "${_LDFLAGS}" ]              && export LDFLAGS="${_LDFLAGS}"
                [ -n "${_ARCH}" ]                 && export ARCH="${_ARCH}"
                [ -n "${_CMAKE_TOOLCHAIN_FILE}" ] && export CMAKE_TOOLCHAIN_FILE="${_CMAKE_TOOLCHAIN_FILE}"
                [ -n "${_OECORE_NATIVE}" ]        && export OECORE_NATIVE_SYSROOT="${_OECORE_NATIVE}"
                [ -n "${_OECORE_TARGET}" ]        && export OECORE_TARGET_SYSROOT="${_OECORE_TARGET}"

                # Step 2: cross-compile ARM binder runtime.
                # Remove .sdk_ready written by Step 1 — build_arm_binder() skips
                # itself if this file exists, leaving x86_64 libs in place.
                # TODO: build_binder.sh to use a separate sentinel for ARM runtime.
                rm -f "${RDK_HAL_DIR}/out/target/.sdk_ready"
                echo "ARM build: cross-compiling ARM binder runtime..."
                build_arm_binder
                export BINDER_SDK_DIR="${RDK_HAL_DIR}/out/target"
            fi
        fi
    else
        # Linux native build: always call build_binder.sh so linux_binder_idl
        # is cloned and host/aidl_ops.py exists before build_modules.sh preflight
        # runs.  build_binder.sh exits immediately if .sdk_ready is already
        # present, so there is no cost when the SDK is up to date.
        if [ -d "${binder_toolchain_dir}" ] && [ ! -d "${binder_toolchain_dir}/.git" ]; then
            echo "Removing incomplete toolchain stub before fresh clone..."
            rm -rf "${binder_toolchain_dir}"
        fi
        (
            cd "${RDK_HAL_DIR}"
            ./build_binder.sh
        ) || {
            echo "ERROR: build_binder.sh failed. Cannot continue."
            exit 1
        }
    fi

    # Build HAL modules from versioned snapshots listed in versions_released.yaml.
    # WORKAROUND: Several snapshot CMakeLists.txt files still reference common/0.1.0.0
    # and videodecoder/0.1.0.0 but versions_released.yaml builds 0.2.0.0 only.
    # Stage old headers and create lib symlinks BEFORE build_modules.sh manifest runs.
    # TODO: Fix snapshot CMakeLists.txt files in rdk-halif-aidl to match versions_released.yaml.

    # Workaround part 1: stage 0.1.0.0 headers so stale include paths in CMakeLists.txt resolve.
    local HALIF_INC_STAGE="${RDK_HAL_DIR}/out/build/include"
    mkdir -p "${HALIF_INC_STAGE}"
    for component in common videodecoder; do
        local old_ver="0.1.0.0"
        local src="${RDK_HAL_DIR}/${component}/${old_ver}/include"
        local dst="${HALIF_INC_STAGE}/${component}/${old_ver}/include"
        if [ -d "${src}" ] && [ ! -d "${dst}" ]; then
            echo "Staging legacy headers: ${component}/${old_ver}"
            mkdir -p "${dst}"
            cp -r "${src}/." "${dst}/"
        fi
    done

    # Workaround part 2: create 0.1.0.0 lib symlinks pointing to 0.2.0.0 so stale
    # target_link_libraries in CMakeLists.txt resolve at link time.
    # TODO: Fix snapshot CMakeLists.txt in rdk-halif-aidl to link against 0.2.0.0 directly.
    local HALIF_LIB_STAGE="${RDK_HAL_DIR}/out/target/lib/halif"
    mkdir -p "${HALIF_LIB_STAGE}"
    for component in common videodecoder; do
        local old_lib="lib${component}-v0.1.0.0-cpp.so"
        local new_lib="lib${component}-v0.2.0.0-cpp.so"
        if [ ! -e "${HALIF_LIB_STAGE}/${old_lib}" ]; then
            echo "Creating legacy lib symlink: ${old_lib} -> ${new_lib}"
            ln -sf "${new_lib}" "${HALIF_LIB_STAGE}/${old_lib}"
        fi
    done

    local HALIF_LIB_DIR="${RDK_HAL_DIR}/out/target/lib/halif"
    local HALIF_READY="${HALIF_LIB_DIR}/.halif_modules_ready"

    if [ -f "${HALIF_READY}" ]; then
        echo "HAL module .so files already present, skipping build_modules.sh..."
    else
        echo "Building HAL modules from versions_released.yaml..."
        local manifest_file="${RDK_HAL_DIR}/versions_released.yaml"
        local sdk_dir_arg=""
        if [ "${TARGET}" = "arm" ] && [ -n "${BINDER_SDK_DIR:-}" ]; then
            sdk_dir_arg="--sdk-dir ${BINDER_SDK_DIR}"
        fi
        (
            cd "${RDK_HAL_DIR}"
            ./build_modules.sh manifest --file "${manifest_file}" ${sdk_dir_arg}
        ) || {
            echo -e "${BOLD}╔══════════════════════════════════════════════════════════════════════╗${RESET}"
            echo -e "${BOLD}* ${RED}Failed to build HAL modules. Exiting.${RESET}"
            echo -e "${BOLD}╚══════════════════════════════════════════════════════════════════════╝${RESET}"
            exit 1
        }
        touch "${HALIF_READY}"
        create_halif_softlinks
    fi
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
    install -m 644 "${RDK_HAL_DIR}/avbuffer/current/avbufferhelper.h" "${BUILD_INSTALL_PREFIX}/include/"
    cd -
    rm -rf $AVBUFFER_HELPER_DIR/build
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

    # Remove gstreamer and egl libraries from the install path (not needed in final tar)
    rm -rf ${INSTALL_PATH}/libgst*  ${INSTALL_PATH}/libEGL* ${INSTALL_PATH}/libGL* ${INSTALL_PATH}/libMali* ${INSTALL_PATH}/libwayland* ${INSTALL_PATH}/libgbm* ${INSTALL_PATH}/libgio*

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

    # Install versioned halif libs and their softlinks from the snapshot build
    local HALIF_LIB_DIR="${RDK_HAL_DIR}/out/target/lib/halif"
    if [ -d "${HALIF_LIB_DIR}" ]; then
        find "${HALIF_LIB_DIR}" -maxdepth 1 -name "*.so" \
            -exec cp -a {} "${INSTALL_PATH}/" \; 2>/dev/null || true
    fi

    mkdir -p ${INSTALL_PATH}/assets/streams/input
    mkdir -p ${INSTALL_PATH}/assets/streams/reference
    rm -rf ${INSTALL_PATH}/libavbufferhelper.so

    cd ${TOP_BUILD_DIR}
    tar -zcf ${OUT_TAR_FILE} bin
    cd -
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

    find "$TOP_BUILD_DIR" -type f -name "*.o" -delete

    # Remove build output directories (binaries, libs including libbinder.so copies).
    rm -rf "${TOP_BUILD_DIR}/linux"
    rm -rf "${TOP_BUILD_DIR}/arm"
    rm -rf "${TOP_BUILD_DIR}/bin"
    rm -rf "${TOP_BUILD_DIR}/usr"

    # Remove HAL snapshot cmake build dirs, binder SDK build, and installed out/.
    rm -rf "${RDK_HAL_DIR}/build"
    rm -rf "${RDK_HAL_DIR}/out"
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
echo -e "${BOLD}${GREEN}RDK_HAL_DIR            : ${RESET}${YELLOW}$RDK_HAL_DIR${RESET}"
if [ "${ENABLE_AV_L4_TEST}" = "1" ]; then
echo -e "${BOLD}${GREEN}GST_LIB_PATH           : ${RESET}${YELLOW}$GST_LIB_PATH${RESET}"
fi
if [ "${ENABLE_PLANE_CONTROL_TEST}" = "1" ]; then
echo -e "${BOLD}${GREEN}EGL_LIB_PATH           : ${RESET}${YELLOW}$EGL_LIB_PATH${RESET}"
fi
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
    if [ "${ENABLE_AV_L4_TEST}" = "1" ]; then
        validate_gst_lib_path
    fi
    if [ "${ENABLE_PLANE_CONTROL_TEST}" = "1" ]; then
        validate_egl_lib_path
    fi
    unified_manifest
    generate_hal_interfaces
    install_linux_binder
    if [ "${ENABLE_AV_L4_TEST}" = "1" ]; then
        install_gstreamer_package
    fi
    if [ "${ENABLE_PLANE_CONTROL_TEST}" = "1" ]; then
        install_egl_package
    fi
    build_ut_core
    generate_avbufferhelper_skeleton
    build_halif_test
    install_test
else
    echo -e "${BOLD}${RED}Invalid Arguments${RESET}"
    help
fi
