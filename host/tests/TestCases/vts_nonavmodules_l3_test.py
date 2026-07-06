#!/usr/bin/env python3
#** *****************************************************************************
# *
# * If not stated otherwise in this file or this component's LICENSE file the
# * following copyright and licenses apply:
# *
# * Copyright 2026 RDK Management
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
import time
import yaml
import inspect
import importlib.util
from pathlib import Path

dir_path = os.path.dirname(os.path.realpath(__file__))
module_path = Path(dir_path) / "../../../vts_hal_test_components"
DEFAULT_CONFIG_FILE = "vts_l3_test_nonav_setup.yaml"

sys.path.append(os.path.join(dir_path, "../"))
sys.path.append(os.path.join(dir_path, "../raft"))
from raft.framework.core.logModule import logModule


def _loadPythonModule(pyFile: Path):
    """Load a Python module from the given file path.

    Args:
        pyFile (Path): Path to the Python source file to load.

    Returns:
        module: The loaded module, or None if loading failed.
    """
    fileDir = str(pyFile.parent)
    if fileDir not in sys.path:
        sys.path.append(fileDir)

    moduleName = f"vts_nonav_l3_{pyFile.stem}"
    spec = importlib.util.spec_from_file_location(moduleName, str(pyFile))
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception:
        return None
    return module


def _resolveKwargsForClass(testClass, component):
    """Inspect the test class constructor and return only the kwargs it accepts.

    Supports the well-known optional params used across Non-AV L3 tests:
    - ``moduleName``         - always injected as ``"VTS"``
    - ``testMenuConfigFile`` - resolved to ``<dir_path>/vts_l3_test_setup.yaml``
    - ``artifactDirPath``    - resolved to ``<dir_path>``
    - ``hfpfile``            - auto-discovered as the first
                               ``<components_root>/<module>/profiles/hfp-*.yaml``
    - ``ledConfig``          - auto-discovered from indicator test configuration
                               files (``*LED*config*.yaml``)

    Args:
        testClass: The L3 test class whose ``__init__`` will be inspected.
        component (str): Module name, used for hfpfile path resolution.

    Returns:
        dict: Only the kwargs accepted by the constructor, pre-filled.
    """
    try:
        sig = inspect.signature(testClass.__init__)
    except (ValueError, TypeError):
        return {}

    known = {
        "moduleName": "VTS",
        "testMenuConfigFile": os.path.join(dir_path, "vts_l3_test_setup.yaml"),
        "artifactDirPath": dir_path,
        "hfpfile": None,  # resolved lazily below only if the constructor wants it
        "ledConfig": None,  # resolved lazily below only if the constructor wants it
    }

    kwargs = {}
    for param_name in sig.parameters:
        if param_name in ("self", "log", "summaryLog", "summary_log", "args", "kwargs"):
            continue
        if param_name not in known:
            continue
        value = known[param_name]
        if param_name == "hfpfile" and value is None:
            profiles_dir = module_path / component / "profiles"
            hfp_files = sorted(profiles_dir.glob("hfp-*.yaml")) if profiles_dir.is_dir() else []
            value = str(hfp_files[0]) if hfp_files else None
        if param_name == "ledConfig" and value is None:
            cfg_dir = module_path / component / "test_configuration"
            led_cfgs = sorted(cfg_dir.glob("*LED*config*.yaml")) if cfg_dir.is_dir() else []
            if not led_cfgs and cfg_dir.is_dir():
                led_cfgs = sorted(cfg_dir.glob("*led*config*.yaml"))
            value = str(led_cfgs[0]) if led_cfgs else None
        if value is not None:
            kwargs[param_name] = value
    return kwargs


def runTestInstance(testClass, summary_log, component):
    """Instantiate and run a single L3 test class.

    Injects common class-level attributes then auto-detects which constructor
    kwargs (``moduleName``, ``testMenuConfigFile``, ``artifactDirPath``,
    ``hfpfile``, ``ledConfig``) the test accepts and passes only those — no per-test or
    per-module config required.

    Args:
        testClass: The L3 test class to instantiate and run.
        summary_log (logModule): Logger for test output.
        component (str): Component name (e.g. ``"flash"``), used to resolve
            the component directory under ``vts_hal_test_components``.
    """
    testClass._menuConfigFile = os.path.join(dir_path, "vts_l3_test_setup.yaml")
    testClass._moduleName = "VTS"
    testClass._dirPath = dir_path
    testClass._profilePath = module_path / component
    kwargs = _resolveKwargsForClass(testClass, component)
    testInstance = testClass(summary_log, **kwargs)
    testInstance.run(False)
    time.sleep(2)  # Short delay between tests

def runNonAvL3TestInstances(summary_log):
    """Load and run all Non-AV L3 tests defined in the YAML suite config.

    Reads the test suite config (default: ``vts_l3_test_nonav_setup.yaml``)
    and discovers L3 test classes for each enabled module, then runs them sequentially.

    Args:
        summary_log (logModule): Logger for test output.

    Returns:
        bool: True if all tests were processed, False on config error.
    """
    configPath = Path(dir_path) / DEFAULT_CONFIG_FILE
    if not configPath.exists():
        summary_log.error(f"Config file not found: {configPath}")
        return False

    try:
        with open(configPath, "r", encoding="utf-8") as cfg_file:
            data = yaml.safe_load(cfg_file) or {}
    except Exception as e:
        summary_log.error(f"Failed to read config file {configPath}: {e}")
        return False

    testEntries = data.get("nonAvL3Tests", {}).get("tests", [])
    if not isinstance(testEntries, list):
        summary_log.error("Invalid config format: nonAvL3Tests.tests must be a list")
        return False

    for entry in testEntries:
        if not isinstance(entry, dict):
            continue
        if not entry.get("enabled", True):
            continue

        component = entry.get("module")
        requestedClasses = entry.get("tests", [])
        if not component or not isinstance(requestedClasses, list):
            summary_log.warn(f"Skipping invalid test entry (module/tests missing): {entry}")
            continue

        testsDir = (module_path / component / "host/tests").resolve()
        if not testsDir.is_dir():
            summary_log.warn(f"Host tests directory not found for module '{component}': {testsDir}")
            continue

        classMap = {}
        for pyFile in sorted(testsDir.glob("*L3*.py")):
            module = _loadPythonModule(pyFile)
            if module is None:
                continue
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if "_L3_" in name and obj.__module__ == module.__name__:
                    classMap[name] = (obj, pyFile)

        for className in requestedClasses:
            if className not in classMap:
                summary_log.warn(
                    f"Class {className} not found under module '{component}' L3 host tests"
                )
                continue
            testClass, moduleFile = classMap[className]
            summary_log.info(f"Loading L3 test class {className} from {moduleFile}")
            runTestInstance(testClass, summary_log, component)

    return True

if __name__ == "__main__":
    summaryLog = logModule("L3NonAvTests", level=logModule.INFO)
    runNonAvL3TestInstances(summaryLog)