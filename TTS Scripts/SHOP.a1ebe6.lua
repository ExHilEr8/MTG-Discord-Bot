wrhost = "http://127.0.0.1:5000/"

local prevCardCount = 0
local cardCount = 0
local cardArray = {}
local realCardCount = 0

local discordIDToPosition = {
    ["123536697769197569"] = vector(0, 3, -20),
    ["123768566016245760"] = vector(-37, 3, 20)
}

-- Expand rejectStrings into a list of all unique tokens 
local rejectStrings = {"Plains", "Island", "Swamp", "Mountain", "Forest", "Basic Land"}

function reinitializeCardArray()
    cardArray = {}
    cardCount = 0
    realCardCount = 0
end

function onLoad(script_state)
    resetDBShopQuantities()

    cardList = {}

    for _, card in ipairs(self.getObjects()) do
        cardList[#cardList+1] = card.name
        print(card.name)
    end

    syncWithDB(cardList)
end

function onObjectEnterContainer(container, object)
    if (self.getGUID() == container.getGUID()) then
        local reject = false
        local cardName = object.getName()

        for _, rejstr in ipairs(rejectStrings) do
            if string.find(cardName, rejstr, 1, true) then
                reject = true
            end
        end

        if(not reject) then
            cardArray[realCardCount + 1] = cardName
            realCardCount = realCardCount + 1
        else
            local rejectcontainer = getObjectFromGUID('23104d')
            rejectcontainer.putObject(container.takeObject())
        end
        cardCount = cardCount - 1

        if(cardCount <= 0) then
            addToLocal(cardArray)
            reinitializeCardArray()
        end
    end
end

function checkObjectEnter(object)
    local objname = object.name

    if not (objname == 'Card' or objname == 'Deck' or objname == 'CardCustom') then
        return false
    end

    local objqnt = object.getQuantity()
    if(objqnt > 1) then
        cardCount = objqnt 
        prevCardCount = cardCount
        deckReorderAboveContainer(self, object)
        return false
    end

    return true
end

function tryObjectEnter(object)
    return checkObjectEnter(object)
end

function deckReorderAboveContainer(container, object)
    for _=1, object.getQuantity() do
        container.putObject(object.takeObject())
    end
end

function tableLength(T)
    local count = 0
    for _ in ipairs(T) do count = count + 1 end
    return count
end

function addToLocal(obj)
    function callback(wr)
        if wr.is_error then
            log(wr.url)
            log(wr.error)
        else
            log(wr.url)
            print(wr.text)
        end
    end

    WebRequest.post("http://127.0.0.1:5000/addcards", obj, callback)
end

function resetDBShopQuantities()
    function callback(wr)
        if wr.is_error then
            log(wr.url)
            log(wr.error)
        else
            log(wr.url)
            print(wr.text)
        end
    end

    WebRequest.get("http://127.0.0.1:5000/resetDB", callback)
end

function checkoutCardsFromBag(discord_id, cardlist)
    local putPosition = discordIDToPosition[discord_id]
    local takenList = {}

    print(cardlist)

    for _, card in ipairs(cardlist) do
        for _, bagcard in ipairs(self.getObjects()) do
            if(card == bagcard.name) then
                print(bagcard.name)
                local takenobject = self.takeObject({position = putPosition, index = bagcard.index})
                takenobject.use_hands = false
                takenList[#takenList+1]=takenobject
                break
            end
        end
    end

    print(takenList)

    Wait.time(function()
        for _, takencard in ipairs(takenList) do
            takencard.use_hands = true
        end
    end,
    1)
end

function useHands(takenList)
    for _, takencard in ipairs(takenList) do
        takencard.use_hands = true
    end
end

function exCheckout()
    discordShopCheckout("123536697769197569")
end

function ediCheckout()
    discordShopCheckout("123768566016245760")
end

function discordShopCheckout(id)
    function callback(wr)
        if wr.is_error then
            log(wr.url)
            log(wr.error)
        else
            log(wr.url)
            print(wr.text)
            checkoutCardsFromBag(id, JSON.decode(wr.text))
        end
    end

    WebRequest.post("http://127.0.0.1:5000/getcart", id, callback)
end

function syncWithDB(cardList)
    function callback(wr)
        if wr.is_error then
            log(wr.url)
            log(wr.error)
        else
            log(wr.url)
            print(wr.text)
        end
    end

    WebRequest.post("http://127.0.0.1:5000/syncWithDB", cardList, callback)
end