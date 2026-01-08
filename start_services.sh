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

# -----------------------------
# Service definitions
# -----------------------------

SERVICE_NAMES=(
  "Vendor-Indicator"
)

SERVICE_BINARIES=(
  "./Vendor-Indicator"
)

SERVICE_CONFIGS=(
  "./vcomponent_configurations/indicator_vcomponent_configuration.yaml"
)

SERVICE_PORTS=(
  "8080"
)

LOG_DIR="/tmp/vendor_services_logs"
mkdir -p "${LOG_DIR}"

# -----------------------------
# Helper functions
# -----------------------------

is_service_running() {
  local binary="$1"
  local port="$2"

  # Match process by binary name and port
  pgrep -f "${binary}" > /dev/null 2>&1
}

# -----------------------------
# Start services if not running
# -----------------------------

SERVICE_COUNT=${#SERVICE_NAMES[@]}

for (( i=0; i<SERVICE_COUNT; i++ )); do
  NAME="${SERVICE_NAMES[$i]}"
  BIN="${SERVICE_BINARIES[$i]}"
  CFG="${SERVICE_CONFIGS[$i]}"
  PORT="${SERVICE_PORTS[$i]}"

  if is_service_running "${BIN}" "${PORT}"; then
    echo "[SKIP] ${NAME} already running on port ${PORT}"
  else
    echo "[START] ${NAME} (port ${PORT})"

    ${BIN} \
      -c "${CFG}" \
      -p "${PORT}" \
      > "${LOG_DIR}/${NAME}.log" 2>&1 &

    PID=$!
    echo "[OK] ${NAME} started with PID ${PID}"
  fi
done

echo "Service startup check completed."
