-- Basic locomotive control script example for Train Simulator Classic
-- This script handles door controls and some basic interactions

function Initialise()
    -- Initialise controls on startup
    SysCall("PlayerEngineSetControlValue", "DoorSwitch", 0, 0)  -- Doors closed
    SysCall("PlayerEngineSetControlValue", "LightSwitch", 0, 0) -- Lights off
end

function Update(time)
    -- Called every frame; handle continuous logic here if needed
    -- For example, automatic door opening based on speed (simplified)
    local speed = SysCall("PlayerEngine:GetControlValue", "SpeedometerMPH", 0)
    if speed > 5 then
        SysCall("PlayerEngineSetControlValue", "DoorSwitch", 0, 1)  -- Open doors if moving
    else
        SysCall("PlayerEngineSetControlValue", "DoorSwitch", 0, 0)  -- Close doors if stopped
    end
end

function OnControlValueChange(name, index, value)
    -- React to control changes
    if name == "DoorSwitch" then
        if value == 1 then
            SysCall("ScenarioManager:ShowMessage", "Doors opened!", 5, 1)
        else
            SysCall("ScenarioManager:ShowMessage", "Doors closed!", 5, 1)
        end
    elseif name == "LightSwitch" then
        SysCall("ScenarioManager:ShowMessage", "Lights toggled!", 5, 1)
    end
end

function OnEvent(event)
    -- Handle events like signals or triggers
    if event == "EmergencyBrake" then
        SysCall("PlayerEngineSetControlValue", "BrakeControl", 0, 1)
        SysCall("ScenarioManager:ShowMessage", "Emergency brake activated!", 10, 3)
    end
end