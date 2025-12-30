#!/usr/bin/env python3

#vts_non_av_tests.py

import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, "../../"))
sys.path.append(os.path.join(dir_path, "../../../vts_hal_test_components/cec/host/tests")) # For hdmicec module

from vts_hdmicec_L3_ReceiveMessage import VTS_HDMICEC_L3_ReceiveMessage as vts_hdmicec_L3_receive_message
from vts_hdmicec_L3_SendMessage import VTS_HDMICEC_L3_SendMessage as vts_hdmicec_L3_send_message
from raft.framework.core.logModule import logModule

if __name__ == '__main__':
    summaryLogName = "run_non_av_vts_summary"
    summaryLog = logModule(summaryLogName, level=logModule.INFO)

    # Create test instances
    tests = [
        #vts_hdmicec_L3_receive_message(summaryLog),
        vts_hdmicec_L3_send_message(summaryLog)
        # Add more test instances here
    ]

    # Run each test
    for test in tests:
        test.run(False)