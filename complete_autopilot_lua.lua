-- Advanced Train Simulator Autopilot - Complete Lua Implementation
-- SendCommand system ELIMINATED - Direct control only
-- GetData maintained for telemetry output

-- Global variables
gData = ""
autopilotActive = false
predictiveActive = false
doorsAutoMode = true
lastSpeed = 0
lastAcceleration = 0
speedHistory = {}
accelerationHistory = {}
alertThresholds = {
    speed = 80,  -- km/h
    acceleration = 2.0,  -- m/s²
    brakePressure = 3.0,  -- bar (converted from PSI)
    wheelslip = 0.1,  -- wheelslip threshold
    fuel = 0.15,  -- 15% fuel remaining
    rpm = 2000,  -- high RPM threshold
    current = 1000,  -- high current threshold (amps)
    speedLimitBuffer = 5  -- km/h over limit before alert
}

-- Control mappings (same as Python system)
controlMappings = {
    ["acelerador"] = "Regulator",
    ["freno_tren"] = "TrainBrakeControl",
    ["freno_motor"] = "EngineBrakeControl",
    ["freno_dinamico"] = "VirtualEngineBrakeControl",
    ["reverser"] = "Reverser",
    ["puertas"] = "DoorSwitch",  -- May not be available in diesel locos
    ["luces"] = "Headlights",  -- Changed to Headlights
    ["freno_emergencia"] = "EmergencyBrake"
}

-- Initialize system
function Initialise()
    -- Initialize all controls to safe state
    SysCall("PlayerEngineSetControlValue", "DoorSwitch", 0, 0)  -- Doors closed
    SysCall("PlayerEngineSetControlValue", "Headlights", 0, 0) -- Lights off
    SysCall("PlayerEngineSetControlValue", "Regulator", 0, 0) -- Throttle off
    SysCall("PlayerEngineSetControlValue", "TrainBrakeControl", 0, 0) -- Brakes off

    -- Initialize history tables
    for i = 1, 10 do
        speedHistory[i] = 0
        accelerationHistory[i] = 0
    end

    SysCall("ScenarioManager:ShowMessage", "Train Simulator Autopilot Initialized", 5, 1)
end

-- Main update loop (called every frame)
function Update(time)
    if Call("GetIsEngineWithKey") == 1 then
        -- Read commands from Python system
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

        -- Handle automatic doors
        if doorsAutoMode then
            handleAutomaticDoors()
        end

        -- Check for alerts
        checkAlerts()
    end
end

-- Update telemetry data
function updateTelemetry()
    local currentSpeed = Call("GetSpeed") * 3.6  -- Convert to km/h
    local currentAcceleration = Call("GetAcceleration")

    -- Update history (rolling buffer)
    table.remove(speedHistory, 1)
    table.insert(speedHistory, currentSpeed)

    table.remove(accelerationHistory, 1)
    table.insert(accelerationHistory, currentAcceleration)

    -- Store for next frame
    lastSpeed = currentSpeed
    lastAcceleration = currentAcceleration
end

-- Handle autopilot logic
function handleAutopilot()
    local currentSpeed = lastSpeed
    local targetSpeed = 60  -- km/h (configurable)
    local speedLimit = Call("GetCurrentSpeedLimit") * 3.6

    -- Señal procesada: priorizar KVB si existe
    local signalAspect = Call("GetControlValue", "SignalAspect", 0) or -1
    local kvbAspect = Call("GetControlValue", "KVB_SignalAspect", 0) or -1
    local senal_procesada = kvbAspect ~= -1 and kvbAspect or signalAspect

    -- Log para debugging rápido en consola si está habilitado
    if senal_procesada == 0 then
        SysCall("ScenarioManager:ShowMessage", "Señal ROJA detectada por autopilot", 1, 1)
    elseif senal_procesada == 1 then
        SysCall("ScenarioManager:ShowMessage", "Señal AMARILLA detectada por autopilot", 0.5, 1)
    end

    -- Seguridad: si la señal es roja o desconocida (y se quiere ser conservador), aplicar freno
    if senal_procesada == 0 then
        -- Freno completo y cortar acelerador
        SysCall("PlayerEngineSetControlValue", "TrainBrakeControl", 0, 1.0)
        SysCall("PlayerEngineSetControlValue", "Regulator", 0, 0)
        return
    elseif senal_procesada == 1 then
        -- Señal ámbar: reducir velocidad con freno leve si estamos por encima del límite
        local currentLimit = Call("GetCurrentSpeedLimit") * 3.6
        if currentSpeed > currentLimit + 5 then
            local amberBrake = math.min((currentSpeed - currentLimit) / 40, 0.4)
            SysCall("PlayerEngineSetControlValue", "TrainBrakeControl", 0, amberBrake)
            SysCall("PlayerEngineSetControlValue", "Regulator", 0, 0)
        end
    end

    -- Basic speed control logic
    if currentSpeed < targetSpeed - 2 then
        -- Speed up
        local throttleValue = math.min((targetSpeed - currentSpeed) / 20, 1.0)
        SysCall("PlayerEngineSetControlValue", "Regulator", 0, throttleValue)
        SysCall("PlayerEngineSetControlValue", "TrainBrakeControl", 0, 0)
    elseif currentSpeed > targetSpeed + 2 then
        -- Slow down
        local brakeValue = math.min((currentSpeed - targetSpeed) / 30, 1.0)
        SysCall("PlayerEngineSetControlValue", "Regulator", 0, 0)
        SysCall("PlayerEngineSetControlValue", "TrainBrakeControl", 0, brakeValue)
    else
        -- Maintain speed
        SysCall("PlayerEngineSetControlValue", "Regulator", 0, 0.1)
        SysCall("PlayerEngineSetControlValue", "TrainBrakeControl", 0, 0)
    end

    -- Gradient compensation
    local gradient = Call("GetGradient")
    if gradient > 0.01 then  -- Uphill
        local compensation = gradient * 0.5
        local currentThrottle = Call("GetControlValue", "Regulator", 0)
        SysCall("PlayerEngineSetControlValue", "Regulator", 0, math.min(currentThrottle + compensation, 1.0))
    elseif gradient < -0.01 then  -- Downhill
        local compensation = math.abs(gradient) * 0.3
        local currentBrake = Call("GetControlValue", "TrainBrakeControl", 0)
        SysCall("PlayerEngineSetControlValue", "TrainBrakeControl", 0, math.min(currentBrake + compensation, 1.0))
    end
end

-- Handle predictive analysis
function handlePredictiveAnalysis()
    -- Simple predictive braking based on speed and distance to next signal/limit
    local currentSpeed = lastSpeed
    local nextLimit, nextDistance = Call("GetNextSpeedLimit", 0)

    if nextLimit and nextDistance then
        nextLimit = nextLimit * 3.6  -- Convert to km/h
        nextDistance = nextDistance  -- Distance in meters

        -- Calculate required deceleration
        local speedDiff = currentSpeed - nextLimit
        local stoppingDistance = (currentSpeed * currentSpeed) / (2 * 1.5)  -- v²/2a, a=1.5 m/s²

        if nextDistance < stoppingDistance and speedDiff > 5 then
            -- Apply predictive braking
            local brakeIntensity = math.min(speedDiff / 20, 1.0)
            SysCall("PlayerEngineSetControlValue", "TrainBrakeControl", 0, brakeIntensity)
            SysCall("PlayerEngineSetControlValue", "Regulator", 0, 0)

            if brakeIntensity > 0.3 then
                SysCall("ScenarioManager:ShowMessage", "Predictive braking activated", 3, 2)
            end
        end
    end
end

-- Handle automatic doors
function handleAutomaticDoors()
    local currentSpeed = lastSpeed

    if currentSpeed > 8 then  -- Moving
        SysCall("PlayerEngineSetControlValue", "DoorSwitch", 0, 1)  -- Open doors
    elseif currentSpeed < 2 then  -- Stopped
        SysCall("PlayerEngineSetControlValue", "DoorSwitch", 0, 0)  -- Close doors
    end
end

-- Check for alerts and safety conditions
function checkAlerts()
    local currentSpeed = lastSpeed
    local currentAcceleration = lastAcceleration

    -- Speed alert
    if currentSpeed > alertThresholds.speed then
        SysCall("ScenarioManager:ShowMessage", string.format("SPEED ALERT: %.1f km/h", currentSpeed), 5, 3)
    end

    -- Acceleration alert (sudden changes)
    if math.abs(currentAcceleration) > alertThresholds.acceleration then
        SysCall("ScenarioManager:ShowMessage", string.format("ACCELERATION ALERT: %.2f m/s²", currentAcceleration), 5, 3)
    end

    -- Brake pressure alerts
    local brakePipePressure = Call("GetControlValue", "AirBrakePipePressurePSI", 0) or 0
    local locoBrakePressure = Call("GetControlValue", "LocoBrakeCylinderPressurePSI", 0) or 0
    local trainBrakePressure = Call("GetControlValue", "TrainBrakeCylinderPressurePSI", 0) or 0

    if brakePipePressure < alertThresholds.brakePressure then
        SysCall("ScenarioManager:ShowMessage", string.format("LOW BRAKE PIPE PRESSURE: %.1f PSI", brakePipePressure), 5, 3)
    end

    if locoBrakePressure < 10 then  -- Low loco brake pressure
        SysCall("ScenarioManager:ShowMessage", string.format("LOCO BRAKE LOW: %.1f PSI", locoBrakePressure), 5, 3)
    end

    -- Wheelslip alert (adaptive threshold based on asset scale)
    local wheelslip = Call("GetControlValue", "Wheelslip", 0) or 0
    local slip_detected = false
    -- If asset reports values in 0..1, use threshold from config; else, treat base~1 assets
    if wheelslip <= 1.0 then
        if wheelslip > alertThresholds.wheelslip then
            slip_detected = true
        end
    else
        -- Most assets that use base=1 report 1 as normal, >1 indicates slip
        -- use a small margin over 1.0 to detect slip
        if wheelslip > 1.05 then
            slip_detected = true
        end
    end
    if slip_detected then
        SysCall("ScenarioManager:ShowMessage", string.format("WHEELSLIP DETECTED: %.2f", wheelslip), 3, 2)
        -- Reduce throttle to recover from slip (basic mitigation)
        local current_throttle = Call("GetControlValue", "Regulator", 0) or 0
        local reduced_throttle = current_throttle * 0.5
        SysCall("PlayerEngineSetControlValue", "Regulator", reduced_throttle, 0)
    end

    -- Fuel level alert
    local fuelLevel = Call("GetFuelLevel") or 1.0
    if fuelLevel < 0.15 then  -- Low fuel
        SysCall("ScenarioManager:ShowMessage", string.format("LOW FUEL: %.1f%%", fuelLevel * 100), 5, 3)
    end

    -- Speed limit monitoring
    local currentLimit = Call("GetCurrentSpeedLimit") or 0
    currentLimit = currentLimit * 3.6  -- Convert to km/h
    if currentSpeed > currentLimit + 5 and currentLimit > 0 then
        SysCall("ScenarioManager:ShowMessage", string.format("EXCEEDING SPEED LIMIT: %.1f/%.1f km/h", currentSpeed, currentLimit), 5, 3)
    end

    -- Signal aspect monitoring
    local signalAspect = Call("GetControlValue", "SignalAspect", 0) or 0
    if signalAspect == 0 then  -- Red signal
        SysCall("ScenarioManager:ShowMessage", "RED SIGNAL AHEAD", 5, 3)
    end

    -- RPM monitoring (engine stress)
    local rpm = Call("GetControlValue", "RPM", 0) or 0
    if rpm > 2000 then  -- High RPM
        SysCall("ScenarioManager:ShowMessage", string.format("HIGH ENGINE RPM: %.0f", rpm), 3, 2)
    end

    -- Ammeter monitoring (electrical load)
    local ammeter = Call("GetControlValue", "Ammeter", 0) or 0
    if math.abs(ammeter) > 1000 then  -- High current draw
        SysCall("ScenarioManager:ShowMessage", string.format("HIGH CURRENT DRAW: %.0f A", ammeter), 3, 2)
    end
end

-- Handle control value changes
function OnControlValueChange(name, index, value)
    -- Provide feedback for control changes
    if name == "DoorSwitch" then
        if value == 1 then
            SysCall("ScenarioManager:ShowMessage", "Doors opened", 3, 1)
        else
            SysCall("ScenarioManager:ShowMessage", "Doors closed", 3, 1)
        end
    elseif name == "Headlights" then
        if value == 1 then
            SysCall("ScenarioManager:ShowMessage", "Lights ON", 3, 1)
        else
            SysCall("ScenarioManager:ShowMessage", "Lights OFF", 3, 1)
        end
    elseif name == "Regulator" then
        if autopilotActive then
            SysCall("ScenarioManager:ShowMessage", string.format("Autopilot throttle: %.1f", value), 2, 1)
        end
    elseif name == "TrainBrakeControl" then
        if value > 0.5 then
            SysCall("ScenarioManager:ShowMessage", string.format("Braking: %.1f", value), 2, 2)
        end
    end
end

-- Handle events
function OnEvent(event)
    if event == "EmergencyBrake" or event == "EmergencyStop" then
        -- Emergency brake activation
        SysCall("PlayerEngineSetControlValue", "BrakeControl", 0, 1)
        SysCall("PlayerEngineSetControlValue", "Regulator", 0, 0)
        autopilotActive = false
        SysCall("ScenarioManager:ShowMessage", "EMERGENCY BRAKE ACTIVATED!", 10, 3)

    elseif event == "SignalPassed" then
        -- Signal passed - could trigger speed limit changes
        SysCall("ScenarioManager:ShowMessage", "Signal passed", 3, 1)

    elseif event == "StationStop" then
        -- Station stop - prepare for passenger exchange
        SysCall("PlayerEngineSetControlValue", "Regulator", 0, 0)
        SysCall("PlayerEngineSetControlValue", "TrainBrakeControl", 0, 0.8)
        SysCall("ScenarioManager:ShowMessage", "Approaching station - braking", 5, 2)
    end
end

-- Custom functions for external control (called from Python if needed)
function SetAutopilotState(state)
    autopilotActive = state
    if state then
        SysCall("ScenarioManager:ShowMessage", "Autopilot ENGAGED", 5, 1)
    else
        SysCall("PlayerEngineSetControlValue", "Regulator", 0, 0)
        SysCall("PlayerEngineSetControlValue", "TrainBrakeControl", 0, 0)
        SysCall("ScenarioManager:ShowMessage", "Autopilot DISENGAGED", 5, 2)
    end
end

function SetPredictiveState(state)
    predictiveActive = state
    if state then
        SysCall("ScenarioManager:ShowMessage", "Predictive analysis ACTIVE", 5, 1)
    else
        SysCall("ScenarioManager:ShowMessage", "Predictive analysis INACTIVE", 5, 1)
    end
end

function SetDoorsState(state)
    doorsAutoMode = state
    SysCall("PlayerEngineSetControlValue", "DoorSwitch", 0, state and 1 or 0)
    if state then
        SysCall("ScenarioManager:ShowMessage", "Automatic doors ENABLED", 3, 1)
    else
        SysCall("ScenarioManager:ShowMessage", "Automatic doors DISABLED", 3, 1)
    end
end

function SetLightsState(state)
    SysCall("PlayerEngineSetControlValue", "Headlights", 0, state and 1 or 0)
    if state then
        SysCall("ScenarioManager:ShowMessage", "Lights ON", 3, 1)
    else
        SysCall("ScenarioManager:ShowMessage", "Lights OFF", 3, 1)
    end
end

function EmergencyBrake()
    SysCall("PlayerEngineSetControlValue", "BrakeControl", 0, 1)
    SysCall("PlayerEngineSetControlValue", "Regulator", 0, 0)
    autopilotActive = false
    predictiveActive = false
    SysCall("ScenarioManager:ShowMessage", "EMERGENCY BRAKE!", 10, 3)
end

function GetTelemetryData()
    -- Return comprehensive current telemetry as a table (for Python integration)
    return {
        -- Basic operational data
        speed = lastSpeed,
        acceleration = lastAcceleration,
        throttle = Call("GetControlValue", "Regulator", 0),
        brake = Call("GetControlValue", "TrainBrakeControl", 0),
        gradient = Call("GetGradient"),

        -- System states
        autopilot = autopilotActive,
        predictive = predictiveActive,
        doors = Call("GetControlValue", "DoorSwitch", 0),
        lights = Call("GetControlValue", "Headlights", 0),

        -- Engine and electrical data
        rpm = Call("GetControlValue", "RPM", 0) or 0,
        ammeter = Call("GetControlValue", "Ammeter", 0) or 0,
        tractiveEffort = Call("GetControlValue", "TractiveEffort", 0) or 0,
        fuelLevel = Call("GetFuelLevel") or 1.0,

        -- Brake system data
        brakePipePressure = Call("GetControlValue", "AirBrakePipePressurePSI", 0) or 0,
        locoBrakeCylinderPressure = Call("GetControlValue", "LocoBrakeCylinderPressurePSI", 0) or 0,
        trainBrakeCylinderPressure = Call("GetControlValue", "TrainBrakeCylinderPressurePSI", 0) or 0,
        equalizingReservoirPressure = Call("GetControlValue", "EqReservoirPressurePSIAdvanced", 0) or 0,
        mainReservoirPressure = Call("GetControlValue", "MainReservoirPressurePSIDisplayed", 0) or 0,
        auxReservoirPressure = Call("GetControlValue", "AuxReservoirPressure", 0) or 0,
        brakePipeTailPressure = Call("GetControlValue", "BrakePipePressureTailEnd", 0) or 0,

        -- Safety and navigation data
        wheelslip = Call("GetControlValue", "Wheelslip", 0) or 0,
        currentSpeedLimit = Call("GetCurrentSpeedLimit") or 0,
        nextSpeedLimit = Call("GetNextSpeedLimit") or 0,
        nextSpeedLimitDistance = Call("GetNextSpeedLimitDistance") or 0,
        signalAspect = Call("GetControlValue", "SignalAspect", 0) or 0,
        kvbSignalAspect = Call("GetControlValue", "KVB_SignalAspect", 0) or -1,

        -- Distance and time data
        distanceTravelled = Call("GetControlValue", "DistanceTravelled", 0) or 0,
        simulationTime = Call("GetSimulationTime") or 0,

        -- System health indicators
        systemHealthy = true,  -- Could be expanded with more checks
        timestamp = os.time()
    }
end

-- Legacy compatibility - GetData only (SendCommand replaced by direct control)
function getdata()
    -- Write comprehensive telemetry data for external monitoring in RailDriver format
    gData = string.format(
        "ControlName:CurrentSpeed\nControlValue:%.2f\n" ..
        "ControlName:Acceleration\nControlValue:%.2f\n" ..
        "ControlName:Regulator\nControlValue:%.2f\n" ..
        "ControlName:TrainBrakeControl\nControlValue:%.2f\n" ..
        "ControlName:Gradient\nControlValue:%.2f\n" ..
        "ControlName:AutopilotActive\nControlValue:%d\n" ..
        "ControlName:PredictiveActive\nControlValue:%d\n" ..
        "ControlName:DistanceTravelled\nControlValue:%.2f\n" ..
        "ControlName:SimulationTime\nControlValue:%.2f\n" ..
        "ControlName:TractiveEffort\nControlValue:%.2f\n" ..
        "ControlName:RPM\nControlValue:%.2f\n" ..
        "ControlName:Ammeter\nControlValue:%.2f\n" ..
        "ControlName:Wheelslip\nControlValue:%.2f\n" ..
        "ControlName:AirBrakePipePressurePSI\nControlValue:%.2f\n" ..
        "ControlName:LocoBrakeCylinderPressurePSI\nControlValue:%.2f\n" ..
        "ControlName:TrainBrakeCylinderPressurePSI\nControlValue:%.2f\n" ..
        "ControlName:EqReservoirPressurePSIAdvanced\nControlValue:%.2f\n" ..
        "ControlName:MainReservoirPressurePSIDisplayed\nControlValue:%.2f\n" ..
        "ControlName:AuxReservoirPressure\nControlValue:%.2f\n" ..
        "ControlName:BrakePipePressureTailEnd\nControlValue:%.2f\n" ..
        "ControlName:LocoBrakeCylinderPressurePSIDisplayed\nControlValue:%.2f\n" ..
        "ControlName:FuelLevel\nControlValue:%.2f\n" ..
        "ControlName:CurrentSpeedLimit\nControlValue:%.2f\n" ..
        "ControlName:NextSpeedLimitSpeed\nControlValue:%.2f\n" ..
        "ControlName:NextSpeedLimitDistance\nControlValue:%.2f\n" ..
        "ControlName:SignalAspect\nControlValue:%.2f\n" ..
        "ControlName:KVB_SignalAspect\nControlValue:%.2f\n",
        lastSpeed / 3.6,  -- Convert back to m/s for RailDriver format
        lastAcceleration,
        Call("GetControlValue", "Regulator", 0),
        Call("GetControlValue", "TrainBrakeControl", 0),
        Call("GetGradient"),
        autopilotActive and 1 or 0,
        predictiveActive and 1 or 0,
        Call("GetControlValue", "DistanceTravelled", 0) or 0,
        Call("GetSimulationTime") or 0,
        Call("GetControlValue", "TractiveEffort", 0) or 0,
        Call("GetControlValue", "RPM", 0) or 0,
        Call("GetControlValue", "Ammeter", 0) or 0,
        Call("GetControlValue", "Wheelslip", 0) or 0,
        Call("GetControlValue", "AirBrakePipePressurePSI", 0) or 0,
        Call("GetControlValue", "LocoBrakeCylinderPressurePSI", 0) or 0,
        Call("GetControlValue", "TrainBrakeCylinderPressurePSI", 0) or 0,
        Call("GetControlValue", "EqReservoirPressurePSIAdvanced", 0) or 0,
        Call("GetControlValue", "MainReservoirPressurePSIDisplayed", 0) or 0,
        Call("GetControlValue", "AuxReservoirPressure", 0) or 0,
        Call("GetControlValue", "BrakePipePressureTailEnd", 0) or 0,
        Call("GetControlValue", "LocoBrakeCylinderPressurePSIDisplayed", 0) or 0,
        Call("GetFuelLevel") or 0,
        Call("GetCurrentSpeedLimit") or 0,
        Call("GetNextSpeedLimit") or 0,
        Call("GetNextSpeedLimitDistance") or 0,
        Call("GetControlValue", "SignalAspect", 0) or 0,
        Call("GetControlValue", "KVB_SignalAspect", 0) or -1
    )

    local file = io.open("plugins/GetData.txt", "w")
    if file then
        file:write(gData)
        file:close()
    end
end

-- SendCommand functionality REMOVED - now using direct Lua API calls
-- All control is handled internally or through direct function calls

-- Read commands from Python system
function readPythonCommands()
    local commandFile = io.open("plugins/autopilot_commands.txt", "r")
    if commandFile then
        for line in commandFile:lines() do
            line = line:match("^%s*(.-)%s*$")
            if line == "start_autopilot" then
                SetAutopilotState(true)
            elseif line == "stop_autopilot" then
                SetAutopilotState(false)
            elseif line == "start_predictive" then
                SetPredictiveState(true)
            elseif line == "stop_predictive" then
                SetPredictiveState(false)
            elseif line == "emergency_brake" then
                EmergencyBrake()
            elseif line == "doors_open" then
                SetDoorsState(true)
            elseif line == "doors_close" then
                SetDoorsState(false)
            elseif line == "lights_on" then
                SetLightsState(true)
            elseif line == "lights_off" then
                SetLightsState(false)
            end
        end
        commandFile:close()
        -- Delete the file after processing
        os.remove("plugins/autopilot_commands.txt")
    end
end