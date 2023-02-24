function onload()
  surface_spawned = 0
  custom_image = 0
  custom_surface_guid = "0"
  table = getObjectFromGUID("0605eb")
  -- failsafe collider
  --table.assetBundle.playLoopingEffect(1)
  table.interactable = false
  -- seat variables
  tray_left = 1
  tray_right = 1

  s_red = 1
  s_white = 1
  s_pink = 1
  s_blue = 1
  s_green = 1
  s_yellow = 1

  surface = 1

  -- createbuttons
  -- surface toggle
  self.createButton({
    label="", click_function="surfaceToggle", function_owner=self,
    position={-6.4,0.5,-7.4}, height=1400, width=1400, font_size=0, rotation={0,0,0}
  })

  -- custom surface spawner
  self.createButton({
    label="", click_function="retractForCustomSurface", function_owner=self,
    position={2.1,0.5,-7.4}, height=1400, width=5900, font_size=0, rotation={0,0,0}
  })

  -- left and right trays
  self.createButton({
    label="", click_function="trayLeftToggle", function_owner=self,
    position={-3,0.5,-0.2}, height=1400, width=1400, font_size=0, rotation={0,0,0}
  })

  self.createButton({
    label="", click_function="trayRightToggle", function_owner=self,
    position={3.2,0.5,-0.2}, height=1400, width=1400, font_size=0, rotation={0,0,0}
  })


  -- player trays
  -- pink - top left
  self.createButton({
    label="", click_function="trayPinkToggle", function_owner=self,
    position={-4.9,0.5,7.5}, height=1400, width=1400, font_size=0, rotation={0,0,0}
  })
  -- green - top center
  self.createButton({
    label="", click_function="trayGreenToggle", function_owner=self,
    position={0,0.5,7.5}, height=1400, width=1400, font_size=0, rotation={0,0,0}
  })
  -- red - top left
  self.createButton({
    label="", click_function="trayRedToggle", function_owner=self,
    position={4.8,0.5,7.5}, height=1400, width=1400, font_size=0, rotation={0,0,0}
  })

  -- blue - bottom left
  self.createButton({
    label="", click_function="trayBlueToggle", function_owner=self,
    position={-4.8,0.5,11.5}, height=1400, width=1400, font_size=0, rotation={0,0,0}
  })
  -- white - bottom center
  self.createButton({
    label="", click_function="trayWhiteToggle", function_owner=self,
    position={0,0.5,11.5}, height=1400, width=1400, font_size=0, rotation={0,0,0}
  })
  -- yellow - bottom right
  self.createButton({
    label="", click_function="trayYellowToggle", function_owner=self,
    position={4.8,0.5,11.5}, height=1400, width=1400, font_size=0, rotation={0,0,0}
  })

end

function retractForCustomSurface()
  if surface == 1 then
    -- do nothing because it's retracted
  elseif surface == 0 then
    table.AssetBundle.playTriggerEffect(4)
    surface = 1
  end
  custom_image = self.getDescription()
  Timer.destroy("waitForRetract")
  Timer.create({identifier="waitForRetract", function_name='spawnCustomSurface', delay=1})
end

function spawnCustomSurface()
  local table_scale = table.getScale()
  local table_pos = table.getPosition()
  local obj = spawnObject({
    type="Custom_Model",
    position={0, table_pos['y']+7, 0},
    rotation={0, 90, 0},
    scale={table_scale['x'],table_scale['y'],table_scale['z']},
    callback = "spawn_callback",
    callback_owner = self,
    sound = false,
 })
  obj.setCustomObject({
    type=4,
    mesh="http://chry.me/up/custom_surface_30x.obj",
    diffuse=custom_image,
    specular_intensity=0,
  })

  surface_spawned = 1
end

function spawn_callback(object_spawned)
  object_spawned.lock()
  object_spawned.interactable = false
  object_spawned.grid_projection = true
  custom_surface_guid = object_spawned.getGUID()
  print("[ff0f47]GRID:[-] Using image: " .. custom_image .. " on object GUID #" .. custom_surface_guid .."\n Press the Raise/Lower button to reset.")
end

function surfaceToggle()
  if surface_spawned == 1 then
    local custom_surface = getObjectFromGUID(custom_surface_guid)
    custom_surface.destruct()
    surface_spawned = 0
  elseif surface_spawned == 0 then
    -- do nada
  end

  if surface == 0 then
    table.AssetBundle.playTriggerEffect(4)
    surface = 1
  elseif surface == 1 then
    table.assetBundle.playTriggerEffect(5)
    surface = 0
  end
end

function trayLeftToggle()
  if tray_left == 0 then
    table.AssetBundle.playTriggerEffect(0)
    tray_left = 1
  elseif tray_left == 1 then
    table.assetBundle.playTriggerEffect(1)
    tray_left = 0
  end
end

function trayRightToggle()
  if tray_right == 0 then
    table.AssetBundle.playTriggerEffect(3)
    tray_right = 1
  elseif tray_right == 1 then
    table.assetBundle.playTriggerEffect(2)
    tray_right = 0
  end
end

function trayPinkToggle()
  if s_pink == 0 then
    table.AssetBundle.playTriggerEffect(10)
    s_pink = 1
  elseif s_pink == 1 then
    table.assetBundle.playTriggerEffect(11)
    s_pink = 0
  end
end

function trayGreenToggle()
  if s_green == 0 then
    table.AssetBundle.playTriggerEffect(16)
    s_green = 1
  elseif s_green == 1 then
    table.assetBundle.playTriggerEffect(17)
    s_green = 0
  end
end

function trayRedToggle()
  if s_red == 0 then
    table.AssetBundle.playTriggerEffect(12)
    s_red = 1
  elseif s_red == 1 then
    table.assetBundle.playTriggerEffect(13)
    s_red = 0
  end
end

function trayBlueToggle()
  if s_blue == 0 then
    table.AssetBundle.playTriggerEffect(8)
    s_blue = 1
  elseif s_blue == 1 then
    table.assetBundle.playTriggerEffect(9)
    s_blue = 0
  end
end

function trayWhiteToggle()
  if s_white == 0 then
    table.AssetBundle.playTriggerEffect(14)
    s_white = 1
  elseif s_white == 1 then
    table.assetBundle.playTriggerEffect(15)
    s_white = 0
  end
end

function trayYellowToggle()
  if s_yellow == 0 then
    table.AssetBundle.playTriggerEffect(6)
    s_yellow = 1
  elseif s_yellow == 1 then
    table.assetBundle.playTriggerEffect(7)
    s_yellow = 0
  end
end

function failsafe()
  Timer.destroy("waitForReload")
  Timer.create({identifier="waitForReload", function_name='failsafeTrigger', delay=3})
end

function failsafeTrigger()
  -- retract surface on load for failsafe
  table.AssetBundle.playTriggerEffect(4)
end