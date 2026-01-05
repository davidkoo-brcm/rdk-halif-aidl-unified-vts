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
# file: run_non_av.sh

#set -euo pipefail

DEV_BINDER='/dev/binder'
RUN_DIR=$(realpath "$(dirname "$0")")

# Check permission to access binder
if [ ! -w "$DEV_BINDER" ]; then
    echo "Error: No permission to access $DEV_BINDER. Please run as root."
    exit 1
fi

export LD_LIBRARY_PATH=/usr/lib:/lib:/home/root:./:$RUN_DIR:$LD_LIBRARY_PATH

# ---- Configuration (ARRAYS) -----------------------------------------------

VCOMPONENT_SERVICE_NAMES=(
    "Vendor-DeviceInfo",
    "Vendor-HdmiCec"
    "Vendor-DeepSleep"
    # add more services here
)

VCOMPONENT_CONFIG_PATHS=(
    "${RUN_DIR}/vcomponent_configurations/deviceinfo_vcomponent_configuration.yaml",
    "${RUN_DIR}/vcomponent_configurations/hdmicec_vcomponent_configuration.yaml"
    "${RUN_DIR}/vcomponent_configurations/deepsleep_vcomponent_configuration.yaml"
    # matching config paths
)

VCOMPONENT_PORTS=(
    8075,
    8080,
    8080
    # matching ports
)

# ---- Validation ------------------------------------------------------------

if [[ ${#VCOMPONENT_SERVICE_NAMES[@]} -ne ${#VCOMPONENT_CONFIG_PATHS[@]} ]] || \
   [[ ${#VCOMPONENT_SERVICE_NAMES[@]} -ne ${#VCOMPONENT_PORTS[@]} ]]; then
    echo "ERROR: Array lengths must match (service, config, port)"
    exit 1
fi

# ---- Helpers ---------------------------------------------------------------

check_process() {
    local process_name=$1
    pgrep -f "$process_name" > /dev/null
}

prompt_string() {
    local prompt=$1
    local response
    read -p "$prompt : " response
    echo "$response"
}

# ---- Service Runner --------------------------------------------------------

start_vcomponent_service() {
    local name=$1
    local default_config=$2
    local port=$3

    echo "Starting ${name} (port=${port})"

    local user_config
    user_config=$(prompt_string "Config path for ${name} (Default: ${default_config})")
    [[ -z "$user_config" ]] && user_config="$default_config"

    "${RUN_DIR}/${name}" -c "$user_config" -p "$port" &
    local pid=$!

    sleep 1
    echo "${name} started with PID: ${pid}"
}

# ---- Main Loop -------------------------------------------------------------

for i in "${!VCOMPONENT_SERVICE_NAMES[@]}"; do
    name="${VCOMPONENT_SERVICE_NAMES[$i]}"
    config="${VCOMPONENT_CONFIG_PATHS[$i]}"
    port="${VCOMPONENT_PORTS[$i]}"

    if check_process "$name"; then
        echo "${name} is already running"
    else
        start_vcomponent_service "$name" "$config" "$port"
    fi
done

echo "Executing [vts_hal_test]"
"${RUN_DIR}/vts_hal_test" "$@"