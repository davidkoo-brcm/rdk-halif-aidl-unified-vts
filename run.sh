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

DEV_BINDER='/dev/binder'
RUN_DIR=$(realpath "$(dirname "$0")")

# Check permission to access binder
if [ ! -w "$DEV_BINDER" ]; then
    echo "Error: No permission to access $DEV_BINDER. Please run as root."
    exit 1
fi

export LD_LIBRARY_PATH=/usr/lib:/lib:/home/root:./:$RUN_DIR:$LD_LIBRARY_PATH

# Function to check if a process is running
check_process() {
    local name="$1"
    pgrep -f "$name" > /dev/null
    return $?
}

# Function to prompt the user
prompt_yes_no() {
    local prompt="$1"
    while true; do
        read -p "$prompt (y/n): " response
        case "$response" in
            [Yy]*) return 0 ;;
            [Nn]*) return 1 ;;
            *) echo "Please answer y or n." ;;
        esac
    done
}

# Function to check and start a service with verification
check_and_start_service() {
    local name="$1"
    local binary_path="${RUN_DIR}/${name}"
    local max_attempts=3
    local attempt=1

    if check_process "$name"; then
        echo "$name is already running."
        return 0
    fi

    if prompt_yes_no "$name is not running. Do you want to start it?"; then
        if [ -x "$binary_path" ]; then
            echo "Starting [$name]"
            "$binary_path" &
            local pid=$!
            # Wait up to 3 attempts (3 seconds each) for service to start
            while [ $attempt -le $max_attempts ]; do
                sleep 3
                if check_process "$name"; then
                    echo "$name started successfully (PID: $(pgrep -f "$name"))."
                    return 0
                fi
                echo "Attempt $attempt: $name not yet running."
                attempt=$((attempt + 1))
            done
            echo "Error: Failed to start $name after $max_attempts attempts."
            return 1
        else
            echo "Error: Executable $binary_path not found or not executable!"
            return 1
        fi
    else
        echo "Error: Skipped starting $name. This may cause vts_hal_test to fail."
        return 1
    fi
}

# Always check/start servicemanager first
if ! check_and_start_service "servicemanager"; then
    echo "Error: servicemanager is required but not running. Exiting."
    exit 1
fi

# List of required services to check
services=(
    "RDKAVBufferService"
    "AudioDecoderService"
    "RDKAVClockService"
    "RDKVideoDecoderService"
    "RDKVideoSinkAndPCService"
    "AudioSinkService"
)

# Check all services and track failures
failed_services=()
for service in "${services[@]}"; do
    if ! check_and_start_service "$service"; then
        failed_services+=("$service")
    fi
done

# Exit if any required services failed to start
if [ ${#failed_services[@]} -ne 0 ]; then
    echo "Error: The following services failed to start: ${failed_services[*]}"
    echo "vts_hal_test requires all services to be running. Exiting."
    exit 1
fi

echo "Executing [vts_hal_test]"
"${RUN_DIR}/vts_hal_test" "$@"
