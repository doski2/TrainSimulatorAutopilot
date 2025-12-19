-- Enhanced locomotive control script for Train Simulator Autopilot
-- Combines data reading/writing with advanced locomotive controls

gData = ""
delay = 5
counter = 3 --Loop counter to only update every number of iterations set by delay variable
dataread = 0
previousValues = {}
speedoType = 0 -- 0 = none, 1 = MPH, 2 = KPH
MPH = 2.23693629 -- Convert meters per second to MPH
KPH = 3.60	-- Convert meters per second to KPH
delete_Files = 1 -- Delete Getdata.txt and sendcommand.txt files on first run

-- Enhanced locomotive control variables
autoDoorsEnabled = false  -- Disabled: doors managed by AI in future
lastSpeed = 0
doorsState = 0 -- 0 = closed, 1 = open
lightsState = 0 -- 0 = off, 1 = on

function Initialise()
    -- Initialize locomotive controls on startup
    -- Door control initialization removed; AI will manage doors in future
    if Call("ControlExists", "LightSwitch", 0) == 1 then
        Call("SetControlValue", "LightSwitch", 0, 0) -- Lights off
        lightsState = 0
    end
end

function Update(time)
    -- Enhanced locomotive logic
    if Call("GetIsEngineWithKey") == 1 then
        local currentSpeed = Call("GetSpeed")

        -- Door automation disabled; doors will be handled by AI when implemented

        lastSpeed = currentSpeed
    end
end

function OnControlValueChange(name, index, value)
    -- Handle control changes with feedback
    -- Door control events removed; handled by AI in future
    elseif name == "LightSwitch" then
        lightsState = value
        if value == 1 then
            Call("ScenarioManager:ShowMessage", "Lights ON", 3, 1)
        else
            Call("ScenarioManager:ShowMessage", "Lights OFF", 3, 1)
        end
    elseif name == "BrakeControl" and value == 1 then
        Call("ScenarioManager:ShowMessage", "EMERGENCY BRAKE!", 5, 3)
    end
end

function OnEvent(event)
    -- Handle emergency events
    if event == "EmergencyBrake" or event == "EmergencyStop" then
        if Call("ControlExists", "BrakeControl", 0) == 1 then
            Call("SetControlValue", "BrakeControl", 0, 1)
            Call("ScenarioManager:ShowMessage", "EMERGENCY BRAKE ACTIVATED!", 10, 3)
        end
    end
end

-- Original data collection functions (simplified)
function getdata()
    if delete_Files == 1 then
        deleteFiles()
    end
    counter = counter + 1
    if counter >= delay then
        if Call("GetIsEngineWithKey") == 1 then
            GetSpeedInfo()
            GetControlData()
            GetSpeedLimits()
            WriteData()
        end
        counter = 0
    end
end

function GetSpeedInfo()
    local data = ""
    local ControlType = "Speed"
    local ControlName = ""
    local ControlMin = 0
    local ControlMax = 0
    local ControlValue = 0

    if Call("ControlExists", "SpeedometerKPH", 0) == 1 then
        speedoType = 2
        ControlName = "SpeedometerKPH"
        ControlMin = 0
        ControlMax = 300
        ControlValue = Call("GetControlValue", "SpeedometerKPH", 0)
        data = data.."ControlType:"..ControlType.."\n"
        data = data .."ControlName:"..ControlName.."\n"
        data = data .."ControlMin:"..ControlMin.."\n"
        data = data .."ControlMax:"..ControlMax.."\n"
        data = data .."ControlValue:"..ControlValue.."\n"
    elseif Call("ControlExists", "SpeedometerMPH", 0) == 1 then
        speedoType = 1
        ControlName = "SpeedometerMPH"
        ControlMin = 0
        ControlMax = 200
        ControlValue = Call("GetControlValue", "SpeedometerMPH", 0)
        data = data.."ControlType:"..ControlType.."\n"
        data = data .."ControlName:"..ControlName.."\n"
        data = data .."ControlMin:"..ControlMin.."\n"
        data = data .."ControlMax:"..ControlMax.."\n"
        data = data .."ControlValue:"..ControlValue.."\n"
    else
        speedoType = 0
        ControlName = "CurrentSpeed"
        ControlMin = 0
        ControlMax = 3000
        ControlValue = Call("GetSpeed")
        data = data.."ControlType:"..ControlType.."\n"
        data = data .."ControlName:"..ControlName.."\n"
        data = data .."ControlMin:"..ControlMin.."\n"
        data = data .."ControlMax:"..ControlMax.."\n"
        data = data .."ControlValue:"..ControlValue.."\n"
    end
    gData = gData ..data
end

function GetControlData()
    local data = ""
    local ControlType = "Speed"
    local ControlName = ""
    local ControlMin = 0
    local ControlMax = 0
    local ControlValue = 0

    ControlType = "TimeOfDay"
    ControlName = "TimeOfDay"
    ControlMin = 0
    ControlMax = 0
    ControlValue = SysCall("ScenarioManager:GetTimeOfDay")
    data = data.."ControlType:"..ControlType.."\n"
    data = data .."ControlName:"..ControlName.."\n"
    data = data .."ControlMin:"..ControlMin.."\n"
    data = data .."ControlMax:"..ControlMax.."\n"
    data = data .."ControlValue:"..ControlValue.."\n"

    ControlType = "_Acceleration"
    ControlName = "Acceleration"
    ControlMin = 0
    ControlMax = 0
    ControlValue = Call("GetAcceleration")
    data = data.."ControlType:"..ControlType.."\n"
    data = data .."ControlName:"..ControlName.."\n"
    data = data .."ControlMin:"..ControlMin.."\n"
    data = data .."ControlMax:"..ControlMax.."\n"
    data = data .."ControlValue:"..ControlValue.."\n"

    ControlType = "_Gradient"
    ControlName = "Gradient"
    ControlMin = 0
    ControlMax = 0
    ControlValue = Call("GetGradient")
    data = data.."ControlType:"..ControlType.."\n"
    data = data .."ControlName:"..ControlName.."\n"
    data = data .."ControlMin:"..ControlMin.."\n"
    data = data .."ControlMax:"..ControlMax.."\n"
    data = data .."ControlValue:"..ControlValue.."\n"

    gData = gData ..data
end

function GetSpeedLimits()
    local data = ""
    local ControlType = "SpeedLimit"
    local ControlName = ""
    local ControlMin = 0
    local ControlMax = 0
    local ControlValue = ""

    ControlValue = Call("GetCurrentSpeedLimit")
    if (speedoType <= 1) then
        ControlValue = string.format("%1.1f", ControlValue * MPH)
    elseif (speedoType == 2) then
        ControlValue = string.format("%1.1f", ControlValue * KPH)
    end
    ControlName = "CurrentSpeedLimit"
    ControlMin = 0
    ControlMax = 300
    data = data.."ControlType:"..ControlType.."\n"
    data = data .."ControlName:"..ControlName.."\n"
    data = data .."ControlMin:"..ControlMin.."\n"
    data = data .."ControlMax:"..ControlMax.."\n"
    data = data .."ControlValue:"..ControlValue.."\n"

    gData = gData ..data
end

function WriteData()
    gData = gData .."ControlType:SimulationTime".."\n"
    gData = gData .."ControlName:SimulationTime".."\n"
    gData = gData .."ControlMin:0".."\n"
    gData = gData .."ControlMax:0".."\n"
    gData = gData .."ControlValue:"..Call("GetSimulationTime", 0).."\n"

    local file = io.open("plugins/GetData.txt", "w")
    file:write(gData)
    file:flush()
    file:close()
    gData = ""
end

function SendData()
    -- Read file & send data to Railworks
    for line in io.lines("plugins/SendCommand.txt") do
        if line ~= "" then
            local t = {}
            local i = 1
            for str in string.gmatch(line, "[^:]+") do
                t[i] = str
                i = i + 1
            end

            if dataread == 0 then
                previousValues[t[1]] = -1
                t[2] = 0
            end

            if t[1]~= "Wipers" and t[1] ~= "WiperSpeed" and t[1] ~= "swDriverWiper" then
                if previousValues[t[1]] ~= t[2] then
                    if OnControlValueChange then
                        OnControlValueChange(t[1], 0, tonumber(t[2]))
                    else
                        Call("SetControlValue", t[1], 0, tonumber(t[2]))
                    end
                    Call("SetControlTargetValue", t[1], 0, tonumber(t[2]))
                    previousValues[t[1]] = t[2]
                end
            end

            if t[1] == "Wipers" or t[1] == "WiperSpeed" or t[1] == "swDriverWiper" then
                if previousValues[t[1]] ~= 0 or previousValues[t[1]] ~= t[2] then
                    if OnControlValueChange then
                        OnControlValueChange(t[1], 0, tonumber(t[2]))
                    else
                        Call("SetControlValue", t[1], 0, tonumber(t[2]))
                    end
                    Call("SetControlTargetValue", t[1], 0, tonumber(t[2]))
                end
                previousValues[t[1]] = t[2]
            end
        end
    end
    dataread = 1
end

function deleteFiles()
    os.remove("Plugins/GetData.txt")
    os.remove("Plugins/sendcommand.txt")
    delete_Files = 0
end
