-- Universal Counter Tokens      coded by: MrStump

-- edited by Spheniscine to support resizing and offsetting of buttons, and self-naming
kScale = 0.75
xOffset = 0
zOffset = 0.6
nameSuffix = ' Poison Counters'

--Saves the count value into a table (data_to_save) then encodes it into the Tabletop save
function onSave()
    local data_to_save = {saved_count = count}
    saved_data = JSON.encode(data_to_save)
    return saved_data
end

--Loads the saved data then creates the buttons
function onload(saved_data)
    generateButtonParamiters()
    --Checks if there is a saved data. If there is, it gets the saved value for 'count'
    if saved_data != '' then
        local loaded_data = JSON.decode(saved_data)
        count = loaded_data.saved_count
    else
        --If there wasn't saved data, the default value is set to 0.
        count = 0
    end

    --Generates the buttons after putting the count value onto the 'display' button
    b_display.label = tostring(count)
    if count >= 100 then
        b_display.font_size = 360 * kScale
    else
        b_display.font_size = 500 * kScale
    end
    self.createButton(b_display)
    self.createButton(b_plus)
    self.createButton(b_minus)
    self.createButton(b_plus5)
    self.createButton(b_minus5)
end

--Activates when + is hit. Adds 1 to 'count' then updates the display button.
function increase()
    count = count + 1
    updateDisplay()
end

--Activates when - is hit. Subtracts 1 from 'count' then updates the display button.
function decrease()
    --Prevents count from going below 0
    if count > 0 then
        count = count - 1
        updateDisplay()
    end
end

--Activates when + is hit. Adds 5 to 'count' then updates the display button.
function increase5()
    count = count + 5
    updateDisplay()
end

--Activates when - is hit. Subtracts 5 from 'count' then updates the display button.
function decrease5()
    --Prevents count from going below 0
    if count > 4 then
        count = count - 5
    else
        count = 0
    end
    updateDisplay()
end

function customSet()
    local description = self.getDescription()
    if description != '' and type(tonumber(description)) == 'number' then
        self.setDescription('')
        count = tonumber(description)
        updateDisplay()
    end
end

--function that updates the display. I trigger it whenever I change 'count'
function updateDisplay()
    --If statement to resize font size if it gets too long
    if count >= 100 then
        b_display.font_size = 360 * kScale
    else
        b_display.font_size = 500 * kScale
    end
    b_display.label = tostring(count)
    self.editButton(b_display)

    --Edit name
    self.setName(count .. nameSuffix)
end

--This is activated when onload runs. This sets all paramiters for our buttons.
--I do not have to put this all into a function, but I prefer to do it this way.
function generateButtonParamiters()
    b_display = {
        index = 0, click_function = 'customSet', function_owner = self, label = '',
        position = {xOffset,0.1,zOffset}, width = 600 * kScale, height = 500 * kScale, font_size = 500 * kScale
    }
    b_plus = {
        click_function = 'increase', function_owner = self, label =  '+1',
        position = {xOffset + 0.75 * kScale,0.1,zOffset + 0.22 * kScale}, width = 150 * kScale, height = 230 * kScale, font_size = 100 * kScale
    }
    b_minus = {
        click_function = 'decrease', function_owner = self, label =  '-1',
        position = {xOffset - 0.75 * kScale,0.1,zOffset + 0.22 * kScale}, width = 150 * kScale, height = 230 * kScale, font_size = 100 * kScale
    }
    b_plus5 = {
        click_function = 'increase5', function_owner = self, label =  '+5',
        position = {xOffset + 0.75 * kScale,0.1,zOffset -0.22 * kScale}, width = 150 * kScale, height = 230 * kScale, font_size = 100 * kScale
    }
    b_minus5 = {
        click_function = 'decrease5', function_owner = self, label =  '-5',
        position = {xOffset - 0.75 * kScale,0.1,zOffset -0.22 * kScale}, width = 150 * kScale, height = 230 * kScale, font_size = 100 * kScale
    }
end