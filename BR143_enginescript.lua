-- This script is used to call the original code from the enegine script and
-- inject a call to my code which will extract data from and inject data into
-- TS2015. I originally wrote a C# program  that decompiled the engine files
-- then automatically injected my script into into the decompiled code and
-- then recompiled the code. This was a bit long winded and thanks to 'Havner'
-- from UKTrainSim he pointed me in the right direction so I could rewrite my
-- code without having to decompile and recompile.

-- Require the original renamed script, we still need it
require ("assets/GermanRailroadsRW/Rollmaterial/Elloks/BR143/BR143_enginescript.lua.rdbak")

--  keep previous functions before we provide our own
-- you can similarly override any other function (OnControlChange, OnConsistMessage, etc...)

--Check the script is not already loaded as in AP sound files
--If it is just return
previous_getdata = getdata
if previous_getdata then 
	return 
end

previous_update = Update
previous_MainUpdate = MainUpdate

first_run = 1
file_exists = 0

-- Require my script
if first_run == 1 then
	file = io.open("plugins/Railworks_GetData_Script.lua", "r")
	if file then
		file_exists = 1
		file:close()
		require ("plugins/Railworks_GetData_Script")
	end
	first_run = 0
end


-- Provide a basic Initialise for some of the old locos such as in the Kuju folder that don't have one.
function DummyInitialise()
   Call("BeginUpdate")
end

-- Check if we have an Initialise, if not call our DummyInitialise
if not Initialise then
   Initialise = DummyInitialise
end

-- Our Update function that is called continuously
function Update(interval)

	if Call("GetIsPlayer") == 1 then
		Call("SetControlValue", "Active",0, 1)
	end
	-- Check if we have an Update function in the original engine script
	-- If we do then call it.
	if previous_update then
		previous_update(interval)
	end
	-- Now call my function in the Railworks_GetData_Script
	if file_exists == 1 then
		getdata() --Call my function in the Railworks_GetData_Script
	end
end

function MainUpdate(interval)
	if Call("GetIsPlayer") == 1 then
		Call("SetControlValue", "Active",0, 1)
	end
	if previous_MainUpdate then
		previous_MainUpdate(interval)
	end
	-- Now call my function in the Railworks_GetData_Script
	if file_exists == 1 then
		getdata() --Call my function in the Railworks_GetData_Script
	end
end