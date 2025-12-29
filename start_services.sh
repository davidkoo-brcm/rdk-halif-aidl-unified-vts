#!/usr/bin/env bash

# -----------------------------
# Service definitions (arrays)
# -----------------------------

SERVICE_NAMES=(
  "Vendor-HdmiCec"
  "Vendor-DeviceInfo"
)

SERVICE_BINARIES=(
  "./Vendor-HdmiCec"
  "./Vendor-DeviceInfo"
)

SERVICE_CONFIGS=(
  "./vcomponent_configurations/hdmicec_vcomponent_configuration.yaml"
  "./vcomponent_configurations/deviceinfo_vcomponent_configuration.yaml"
)

SERVICE_PORTS=(
  "8080"
  "8075"
)

# Optional: log directory
LOG_DIR="/tmp/vendor_services_logs"
mkdir -p "${LOG_DIR}"

# -----------------------------
# Start services
# -----------------------------

SERVICE_COUNT=${#SERVICE_NAMES[@]}

for (( i=0; i<SERVICE_COUNT; i++ )); do
  echo "Starting ${SERVICE_NAMES[$i]}..."

  ${SERVICE_BINARIES[$i]} \
    -c "${SERVICE_CONFIGS[$i]}" \
    -p "${SERVICE_PORTS[$i]}" \
    > "${LOG_DIR}/${SERVICE_NAMES[$i]}.log" 2>&1 &

  PID=$!
  echo "${SERVICE_NAMES[$i]} started with PID ${PID}"
done

echo "All services started in background."
