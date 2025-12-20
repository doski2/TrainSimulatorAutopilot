#!/usr/bin/env python3
"""
Script to prepare RailWorks for autopilot integration with EMD SD40 Clinchfield locomotive.
This script copies the autopilot script to the appropriate locations.
"""

import os
import shutil
import sys

def prepare_simulator():
    """Prepare the simulator for autopilot integration."""

    # Paths
    railworks_plugins = r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins"
    sd40_engine_dir = r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks\Assets\DTG\Clinchfield\RailVehicles\Diesel\SD40\Default\Engine"
    workspace_script = r"C:\Users\doski\TrainSimulatorAutopilot\sd40_autopilot.lua"

    # Ensure plugins directory exists
    if not os.path.exists(railworks_plugins):
        print(f"Creating plugins directory: {railworks_plugins}")
        os.makedirs(railworks_plugins)

    # Copy our autopilot script to plugins directory
    if os.path.exists(workspace_script):
        destination = os.path.join(railworks_plugins, "engineScript.lua")
        print(f"Copying autopilot script to plugins: {destination}")
        shutil.copy2(workspace_script, destination)

        # Also copy to SD40 engine directory
        sd40_destination = os.path.join(sd40_engine_dir, "SD40EngineScript.lua")
        print(f"Copying autopilot script to SD40 engine: {sd40_destination}")
        shutil.copy2(workspace_script, sd40_destination)

        print("Scripts copied successfully.")
    else:
        print(f"Error: Source script not found: {workspace_script}")
        return False

    print("Preparation completed for EMD SD40 Clinchfield.")
    print("Make sure to:")
    print("1. Start the Python dashboard (python web_dashboard.py)")
    print("2. Load a scenario with the EMD SD40 Clinchfield locomotive")
    print("3. Turn on the engine")
    print("4. Use the dashboard to activate autopilot")

    return True

if __name__ == "__main__":
    success = prepare_simulator()
    sys.exit(0 if success else 1)