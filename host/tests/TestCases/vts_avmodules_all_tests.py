#!/usr/bin/env python3
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
# * http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.
# *
#* *****************************************************************************

import os
import sys
import argparse

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, "../"))

from vts_l1l2_test import L1L2TestClass
from vts_avmodules_l3_test import L3TestClass
from raft.framework.core.logModule import logModule


def run_l1l2(logger: logModule) -> bool:
    test = L1L2TestClass(logger)
    return bool(test.run(False))


def run_l3(logger: logModule) -> bool:
    test = L3TestClass(logger)
    return bool(test.run(False))


def main():
    parser = argparse.ArgumentParser(description="Run VTS L1/L2/L3 test suites", add_help=True)
    parser.add_argument(
        "--levels",
        nargs="+",
        choices=["L1", "L2", "L3", "ALL"],
        default=["ALL"],
        help="Which levels to run (default: ALL)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARN", "ERROR"],
        help="Logger level (default: INFO)"
    )
    # Accept and ignore unknown args (e.g., --config, --deviceConfig) so RAFT helpers can still see them in sys.argv
    args, unknown = parser.parse_known_args()
    if unknown:
        # Optionally log ignored args for visibility
        pass

    summaryLogName = os.path.splitext(os.path.basename(__file__))[0] + "_summary"
    logger = logModule(summaryLogName)
    level_map = {
        "DEBUG": getattr(logModule, "DEBUG", None) or logModule.INFO,
        "INFO": getattr(logModule, "INFO", None) or logModule.INFO,
        "WARN": getattr(logModule, "WARN", None) or getattr(logModule, "WARNING", None) or logModule.INFO,
        "WARNING": getattr(logModule, "WARNING", None) or getattr(logModule, "WARN", None) or logModule.INFO,
        "ERROR": getattr(logModule, "ERROR", None) or logModule.INFO,
    }
    logger.setLevel(level_map.get(args.log_level, level_map["INFO"]))

    levels = args.levels
    if "ALL" in levels:
        levels = ["L1", "L2", "L3"]

    overall = True

    # L1/L2 are combined in one runner
    if "L1" in levels or "L2" in levels:
        logger.testStart("VTS", "L1L2")
        result = run_l1l2(logger)
        overall = overall and result
        # testResult in logModule accepts a single argument; record summary label only
        logger.testResult("L1/L2 Finished")

    if "L3" in levels:
        logger.testStart("AVModule", "L3")
        result = run_l3(logger)
        overall = overall and result
        logger.testResult("L3 Finished")

    # Exit status based on overall result
    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
