#!/usr/bin/env bash

# -----------------------------
# Service definitions (arrays)
# -----------------------------

SERVICE_NAMES=(
  "Vendor-HdmiCec"
  "Vendor-DeviceInfo"
  "Vendor-DeepSleep"
)

SERVICE_BINARIES=(
  "./Vendor-HdmiCec"
  "./Vendor-DeviceInfo"
  "./Vendor-DeepSleep"
)

SERVICE_CONFIGS=(
  "./vcomponent_configurations/hdmicec_vcomponent_configuration.yaml"
  "./vcomponent_configurations/deviceinfo_vcomponent_configuration.yaml"
  "./vcomponent_configurations/deepsleep_vcomponent_configuration.yaml"
)

SERVICE_PORTS=(
  "8080"
  "8075"
  "8085"
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
