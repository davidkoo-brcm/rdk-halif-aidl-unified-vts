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

# Put RUN_DIR/lib and RUN_DIR at the front of LD_LIBRARY_PATH so our test binaries use the correct libraries
export LD_LIBRARY_PATH=$RUN_DIR/lib:$RUN_DIR:/usr/lib:/lib:/home/root:./:$LD_LIBRARY_PATH

echo "Executing [vts_hal_test]"
"${RUN_DIR}/vts_hal_test" "$@"
