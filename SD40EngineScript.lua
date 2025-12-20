-- Universal RailWorks Autopilot Script
-- Works with any locomotive by auto-detecting available controls

-- Global variables
gData = ""
autopilotActive = false
predictiveActive = false
doorsAutoMode = false
lastSpeed = 0
lastAcceleration = 0
speedHistory = {}
accelerationHistory = {}
alertThresholds = {
    speed = 80,
    acceleration = 2.0,
    brakePressure = 3.0,
    wheelslip = 0.1,
    fuel = 0.15,
    rpm = 2000,
    current = 1000,
    speedLimitBuffer = 5
}

-- Auto-detect control mappings
controlMappings = {}

-- Probe: write a file immediately when the script is loaded
pcall(function()
    local f = io.open("plugins/universal_autopilot_loaded.txt", "w")
    if f then
        f:write(os.date("%Y-%m-%d %H:%M:%S") .. " - Universal autopilot script loaded\n")
        f:close()
    end
end)

-- Initialize system
function Initialise()
    -- Auto-detect available controls
    detectControls()

    -- Initialize all detected controls to safe state
    if controlMappings["luces"] then
        SysCall("PlayerEngineSetControlValue", controlMappings["luces"], 0, 0)
    end
    if controlMappings["acelerador"] then
        SysCall("PlayerEngineSetControlValue", controlMappings["acelerador"], 0, 0)
    end
    if controlMappings["freno_tren"] then
        SysCall("PlayerEngineSetControlValue", controlMappings["freno_tren"], 0, 0)
    end

    -- Initialize history tables
    for i = 1, 10 do
        speedHistory[i] = 0
        accelerationHistory[i] = 0
    end

    SysCall("ScenarioManager:ShowMessage", "Universal Autopilot Initialized", 5, 1)

    -- Create a file to indicate the plugin is loaded
    local loaded_file = io.open("plugins/autopilot_plugin_loaded.txt", "w")
    if loaded_file then
        loaded_file:write("loaded")
        loaded_file:close()
    end

    -- Initialize debug log
    pcall(function()
        local f = io.open("plugins/universal_autopilot_debug.log", "a")
        if f then
            f:write(os.date("%Y-%m-%d %H:%M:%S") .. " - Initialise: Universal autopilot loaded\n")
            f:write("Detected controls: " .. tableToString(controlMappings) .. "\n")
            f:close()
        end
    end)
end

-- Detect available controls
function detectControls()
    -- Common control names to try
    local possibleControls = {
        acelerador = {"Regulator", "Throttle", "EngineThrottle"},
        freno_tren = {"TrainBrakeControl", "TrainBrake", "Brake"},
        freno_motor = {"EngineBrakeControl", "EngineBrake", "IndependentBrake"},
        freno_dinamico = {"DynamicBrake", "DynamicBrakeControl", "BlendedBrake"},
        reverser = {"Reverser", "Direction"},
        luces = {"Headlights", "Lights", "Headlight"},
        freno_emergencia = {"EmergencyBrake", "EmergencyBrakeControl"}
    }

    for controlType, possibleNames in pairs(possibleControls) do
        for _, controlName in ipairs(possibleNames) do
            -- Try to get the control value to see if it exists
            local success, value = pcall(function()
                return Call("GetControlValue", controlName, 0)
            end)
            if success and value ~= nil then
                controlMappings[controlType] = controlName
                pcall(function()
                    local f = io.open("plugins/universal_autopilot_debug.log", "a")
                    if f then
                        f:write("Detected control: " .. controlType .. " -> " .. controlName .. "\n")
                        f:close()
                    end
                end)
                break
            end
        end
    end
end

-- Autopilot Update function
function Update_autopilot(time)
    if Call("GetIsEngineWithKey") == 1 then
        -- Read commands from Python system
        pcall(function()
            local f = io.open("plugins/universal_autopilot_debug.log", "a")
            if f then
                f:write(os.date("%Y-%m-%d %H:%M:%S") .. " - Update_autopilot: engine key ON - reading commands\n")
                f:close()
            end
        end)
        readPythonCommands()

        -- Update telemetry
        updateTelemetry()

        -- Write data to file for external monitoring
        getdata()

        -- Handle automatic systems
        if autopilotActive then
            handleAutopilot()
        end

        if predictiveActive then
            handlePredictiveAnalysis()
        end

        -- Check for alerts
        checkAlerts()
    else
        pcall(function()
            local f = io.open("plugins/universal_autopilot_debug.log", "a")
            if f then
                f:write(os.date("%Y-%m-%d %H:%M:%S") .. " - Update_autopilot: engine key OFF - skipping\n")
                f:close()
            end
        end)
    end
end

-- Main Update function
function MainUpdate_autopilot(time)
    Update_autopilot(time)
end

-- Legacy Update function for compatibility
function Update(time)
    Update_autopilot(time)
end

-- Read Python commands
function readPythonCommands()
    local file = io.open("plugins/autopilot_commands.txt", "r")
    if file then
        local command = file:read("*all")
        file:close()

        if command and command ~= "" then
            pcall(function()
                local f = io.open("plugins/universal_autopilot_debug.log", "a")
                if f then
                    f:write(os.date("%Y-%m-%d %H:%M:%S") .. " - Command received: " .. command .. "\n")
                    f:close()
                end
            end)

            if command == "start_autopilot" then
                autopilotActive = true
                SysCall("ScenarioManager:ShowMessage", "Autopilot ACTIVATED", 3, 1)
            elseif command == "stop_autopilot" then
                autopilotActive = false
                SysCall("ScenarioManager:ShowMessage", "Autopilot DEACTIVATED", 3, 1)
                -- Reset controls to neutral
                if controlMappings["acelerador"] then
                    SysCall("PlayerEngineSetControlValue", controlMappings["acelerador"], 0, 0)
                end
                if controlMappings["freno_tren"] then
                    SysCall("PlayerEngineSetControlValue", controlMappings["freno_tren"], 0, 0)
                end
            end

            -- Clear the command file
            local clear_file = io.open("plugins/autopilot_commands.txt", "w")
            if clear_file then
                clear_file:close()
            end
        end
    end
end

-- Handle autopilot logic
function handleAutopilot()
    -- Get current speed
    local currentSpeed = Call("GetSpeed") * 3.6  -- Convert m/s to km/h

    -- Simple autopilot: maintain speed around 50 km/h
    local targetSpeed = 50.0
    local speedError = targetSpeed - currentSpeed

    if math.abs(speedError) > 2.0 then  -- Deadband
        if speedError > 0 then
            -- Need to accelerate
            if controlMappings["acelerador"] then
                local throttle = math.min(speedError / 20.0, 1.0)  -- Proportional control
                SysCall("PlayerEngineSetControlValue", controlMappings["acelerador"], throttle, 0)
            end
            if controlMappings["freno_tren"] then
                SysCall("PlayerEngineSetControlValue", controlMappings["freno_tren"], 0, 0)
            end
        else
            -- Need to brake
            if controlMappings["acelerador"] then
                SysCall("PlayerEngineSetControlValue", controlMappings["acelerador"], 0, 0)
            end
            if controlMappings["freno_tren"] then
                local brake = math.min(-speedError / 30.0, 1.0)  -- Proportional control
                SysCall("PlayerEngineSetControlValue", controlMappings["freno_tren"], brake, 0)
            end
        end
    else
        -- Maintain current speed
        if controlMappings["acelerador"] then
            SysCall("PlayerEngineSetControlValue", controlMappings["acelerador"], 0.3, 0)  -- Idle throttle
        end
        if controlMappings["freno_tren"] then
            SysCall("PlayerEngineSetControlValue", controlMappings["freno_tren"], 0, 0)
        end
    end
end

-- Update telemetry
function updateTelemetry()
    local speed = Call("GetSpeed") * 3.6
    local acceleration = Call("GetAcceleration")
    local rpm = 318  -- Default value
    local fuel = 1.0  -- Default value

    -- Try to get actual values if controls exist
    if controlMappings["rpm"] then
        rpm = Call("GetControlValue", controlMappings["rpm"], 0) or 318
    end
    if controlMappings["fuel"] then
        fuel = Call("GetControlValue", controlMappings["fuel"], 0) or 1.0
    end

    -- Update history
    table.insert(speedHistory, 1, speed)
    table.remove(speedHistory)
    table.insert(accelerationHistory, 1, acceleration)
    table.remove(accelerationHistory)

    lastSpeed = speed
    lastAcceleration = acceleration
end

-- Get data for external monitoring
function getdata()
    local speed = Call("GetSpeed") * 3.6
    local acceleration = Call("GetAcceleration")
    local rpm = 318
    local fuel = 1.0
    local wheelslip = 0

    -- Try to get actual values
    if controlMappings["rpm"] then
        rpm = Call("GetControlValue", controlMappings["rpm"], 0) or 318
    end
    if controlMappings["fuel"] then
        fuel = Call("GetControlValue", controlMappings["fuel"], 0) or 1.0
    end
    if controlMappings["wheelslip"] then
        wheelslip = Call("GetControlValue", controlMappings["wheelslip"], 0) or 0
    end

    gData = string.format("%.2f,%.4f,%.0f,%.2f,%.3f,%s,%s",
        speed, acceleration, rpm, fuel, wheelslip,
        tostring(autopilotActive), tostring(predictiveActive))

    -- Write to file in RailDriver format for compatibility
    pcall(function()
        local file = io.open("plugins/GetData.txt", "w")
        if file then
            -- Write in RailDriver format that the Python system expects
            file:write(string.format(
                "ControlName:CurrentSpeed\nControlValue:%.2f\n" ..
                "ControlName:Acceleration\nControlValue:%.4f\n" ..
                "ControlName:RPM\nControlValue:%.0f\n" ..
                "ControlName:AutopilotActive\nControlValue:%d\n" ..
                "ControlName:PredictiveActive\nControlValue:%d\n" ..
                "ControlName:Wheelslip\nControlValue:%.3f\n",
                speed, acceleration, rpm, 
                autopilotActive and 1 or 0, 
                predictiveActive and 1 or 0,
                wheelslip))
            file:close()
        end
    end)
end

-- Handle predictive analysis (placeholder)
function handlePredictiveAnalysis()
    -- Placeholder for future predictive features
end

-- Check for alerts
function checkAlerts()
    local speed = Call("GetSpeed") * 3.6
    local acceleration = math.abs(Call("GetAcceleration"))
    local rpm = 318
    local fuel = 1.0

    if controlMappings["rpm"] then
        rpm = Call("GetControlValue", controlMappings["rpm"], 0) or 318
    end
    if controlMappings["fuel"] then
        fuel = Call("GetControlValue", controlMappings["fuel"], 0) or 1.0
    end

    if speed > alertThresholds.speed then
        SysCall("ScenarioManager:ShowMessage", "ALERT: High Speed!", 2, 2)
    end

    if acceleration > alertThresholds.acceleration then
        SysCall("ScenarioManager:ShowMessage", "ALERT: High Acceleration!", 2, 2)
    end

    if rpm > alertThresholds.rpm then
        SysCall("ScenarioManager:ShowMessage", "ALERT: High RPM!", 2, 2)
    end

    if fuel < alertThresholds.fuel then
        SysCall("ScenarioManager:ShowMessage", "ALERT: Low Fuel!", 2, 2)
    end
end

-- Utility function to convert table to string for debugging
function tableToString(tbl)
    local result = "{"
    for k, v in pairs(tbl) do
        result = result .. k .. "=" .. tostring(v) .. ", "
    end
    result = result .. "}"
    return result
end