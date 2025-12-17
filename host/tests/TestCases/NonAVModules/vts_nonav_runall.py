import os
import sys
import importlib
from pathlib import Path
import inspect

dir_path = os.path.dirname(os.path.realpath(__file__))

sys.path.append(dir_path)
sys.path.append(os.path.join(dir_path, "../../"))
sys.path.append(os.path.join(dir_path, "../../raft"))

from raft.framework.core.logModule import logModule


# Base path for all Non-AV HAL components
NONAV_BASE_PATH = os.path.abspath(os.path.join(dir_path, "../../../../vts_hal_test_components"))

# Non-AV modules to execute
NONAV_MODULES = [
    "indicator"
]

# Add module test paths
for module in NONAV_MODULES:
    module_test_path = os.path.join(NONAV_BASE_PATH, module, "host", "tests")
    if module_test_path not in sys.path:
        sys.path.append(module_test_path)


# Helper: Find VTS test class inside module
def get_vts_test_class(module_obj):
    """
    Returns the first class that starts with 'VTS_' and has a run() method
    """
    for name, obj in inspect.getmembers(module_obj, inspect.isclass):
        if name.startswith("VTS_") and hasattr(obj, "run"):
            return obj
    return None

# Master Runner
def RunAll_NonAV_L3():
    """
    Dynamically discovers and runs all Non-AV tests
    File pattern: vts_<module_name>_L*.py
    """

    nonavSummaryLog = logModule("NonAV_L3_Summary", level=logModule.INFO)

    nonavSummaryLog.info("Starting Non-AV Test Execution")

    for module in NONAV_MODULES:
        test_dir = Path(os.path.join(NONAV_BASE_PATH, module, "host", "tests"))

        nonavSummaryLog.info(f"Module: {module.upper()}")

        # Discover test files
        test_modules = sorted(test_dir.glob(f"vts_{module}_L3*.py"))

        if not test_modules:
            continue

        for test_module_path in test_modules:
            module_name = test_module_path.stem

            try:
                nonavSummaryLog.info(f"Running Test Module: {module_name}")

                # Import module
                module_obj = importlib.import_module(module_name)

                # Find correct VTS test class
                test_class = get_vts_test_class(module_obj)

                if not test_class:
                    nonavSummaryLog.error(f"No test class found in {module_name}")
                    continue

                # Instantiate and run
                test_instance = test_class(nonavSummaryLog)
                result = test_instance.run(False)

                nonavSummaryLog.stepResult(result,f"{module.upper()} :: {test_class.__name__}")

            except Exception as e:
                nonavSummaryLog.error(f"Failed to run {module_name}: {e}")

    nonavSummaryLog.info("Completed Non-AV Tests Execution")


# Main
if __name__ == "__main__":
    RunAll_NonAV_L3()
