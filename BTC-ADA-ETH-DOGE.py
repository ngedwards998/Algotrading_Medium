import cbpro
import numpy as np
import datetime as dt
import time

public_client = cbpro.PublicClient()



public = ""
private = ""
secret = ""

auth_client = cbpro.AuthenticatedClient(public,private,secret)

                        ### Investment Details ###

# Amount to initially invest
initInvestment = 0

# Amount that will be used for purchase starts at the initial amount
funding = float(initInvestment*0.4)
funding1 = float(initInvestment*0.2)
funding2 = float(initInvestment*0.2)
funding3 = float(initInvestment*0.2)


# Currency to trade, for reference:
# 'BCH-USD' = Bitcoin Cash, 'BTC-USD' = Bitcoin, 'ETH-USD' = Ether
currency = 'DOGE-USD'
currency1 = 'BTC-USD'
currency2 = 'ETH-USD'
currency3 = 'ADA-USD'

# Will return the ID of your specific currency account
def getSpecificAccount(cur):
    x = auth_client.get_accounts()
    for account in x:
        if account['currency'] == cur:
            return account['id']

# Get the currency's specific ID

specificID = getSpecificAccount(str('DOGE'))
specificID1 = getSpecificAccount(str('BTC'))
specificID2 = getSpecificAccount(str('ETH'))
specificID3 = getSpecificAccount(str('ADA'))

# Granularity (in seconds). So 300 = data from every 5 min (its a stickler about the seconds tho)
period = 60

# We will keep track of how many iterations our bot has done
iteration = 1

# Start off by looking to buy
buy = True
sellstop = False

def CoppockFormula(price):
    ROC11 = np.zeros(13)
    ROC14 = np.zeros(13)
    ROCSUM = np.zeros(13)

    for ii in range(0,13):
        ROC11[ii] = (100*(price[ii]-price[ii+11]) / float(price[ii+11]))
        ROC14[ii] = (100*(price[ii]-price[ii+14]) / float(price[ii+14]))
        ROCSUM[ii] = ( ROC11[ii] + ROC14[ii] )

    coppock = np.zeros(4)
    # Calculate the past 4 Coppock values with Weighted Moving Average
    for ll in range(0,4):
        coppock[ll] = (((1*ROCSUM[ll+9]) + (2*ROCSUM[ll+8]) + (3*ROCSUM[ll+7]) \
        + (4*ROCSUM[ll+6]) + (5*ROCSUM[ll+5]) + (6*ROCSUM[ll+4]) \
        + (7*ROCSUM[ll+3]) + (8*ROCSUM[ll+2]) + (9*ROCSUM[ll+1]) \
        + (10*ROCSUM[ll])) / float(55))

    # Calculate the past 3 derivatives of the Coppock Curve
    coppockD1 = np.zeros(3)
    for mm in range(0,3):
        coppockD1[mm] = coppock[mm] - coppock[mm+1]
    CoppockFormula.variable = coppockD1

def BuySell(buy, coppockD1, currency, funding, currentPrice, possibleIncome, initInvestment, owned):
    print(coppockD1[0] / abs(coppockD1[0]))
    print(coppockD1[1] / abs(coppockD1[1]))
    if buy == True and (coppockD1[0] / abs(coppockD1[0])) == 1 and (coppockD1[1] / abs(coppockD1[1])) == -1:

        # Place the order
        auth_client.place_market_order(product_id=currency, side='buy', funds=str(funding))

        # Print message in the terminal for reference
        message = "Buying Approximately " + str(possiblePurchase) + " " + \
        currency + "  Now @ " + str(currentPrice) + "/Coin. TOTAL = " + str(funding)
        print(message)

        # Update funding level and Buy variable
        funding = 0
        buy = False

    print(coppockD1[0]/abs(coppockD1[0]))
    print(coppockD1[1]/abs(coppockD1[1]))
    # Sell Conditions: latest derivative is - and previous is +
    if buy == False and (coppockD1[0]/abs(coppockD1[0])) == -1 and (coppockD1[1]/abs(coppockD1[1])) == 1:

        # Place the order
        auth_client.place_market_order(product_id=currency,side='sell',size=str(owned))

        # Print message in the terminal for reference
        message = "Selling " + str(owned) + " " + currency + "Now @ " + \
        str(currentPrice) + "/Coin. TOTAL = " + str(possibleIncome)
        print(message)

        # Update funding level and Buy variable
        funding = int(possibleIncome)
        buy = True

    # Stop loss: sell everything and stop trading if your value is less than 80% of initial investment
    if (possibleIncome+funding) <= 0.8 * initInvestment:

        # If there is any of the crypto owned, sell it all
        if owned > 0.0:
            auth_client.place_market_order(product_id=currency, side='sell', size=str(owned))
            print("STOP LOSS SOLD ALL")
            time.sleep(1)
        # Will break out of the while loop and the program will end
        sellstop = True

def stats(currentPrice, funding, owned, currency, coppockres):
    print("Current Price: ", currentPrice)
    print("Your Funds: ", funding)
    print("You Own: ", owned, currency)
    print("coppock data: ", coppockres)


while True:
    try:
        historicData = auth_client.get_product_historic_rates(currency, granularity=period)

        # Make an array of the historic price data from the matrix
        price = np.squeeze(np.asarray(np.matrix(historicData)[:,4]))
        
        # Wait for 1 second, to avoid API limit
        time.sleep(1)

        # Get latest data and show to the user for reference
        newData = auth_client.get_product_ticker(product_id=currency)
        print(newData)
        currentPrice = newData['price']
    except:
        # In case something went wrong with cbpro
        print("Error Encountered")
        break
    
    try:
        historicData1 = auth_client.get_product_historic_rates(currency1, granularity=period)

        # Make an array of the historic price data from the matrix
        price1 = np.squeeze(np.asarray(np.matrix(historicData1)[:,4]))
        
        # Wait for 1 second, to avoid API limit
        time.sleep(1)

        # Get latest data and show to the user for reference
        newData1 = auth_client.get_product_ticker(product_id=currency1)
        print(newData1)
        currentPrice1 = newData1['price']
    except:
        # In case something went wrong with cbpro
        print("Error Encountered")
        break

    try:
        historicData2 = auth_client.get_product_historic_rates(currency2, granularity=period)

        # Make an array of the historic price data from the matrix
        price2 = np.squeeze(np.asarray(np.matrix(historicData2)[:,4]))
        
        # Wait for 1 second, to avoid API limit
        time.sleep(1)

        # Get latest data and show to the user for reference
        newData2 = auth_client.get_product_ticker(product_id=currency2)
        print(newData2)
        currentPrice2 = newData2['price']
    except:
        # In case something went wrong with cbpro
        print("Error Encountered")
        break


    try:
        historicData3 = auth_client.get_product_historic_rates(currency3, granularity=period)

        # Make an array of the historic price data from the matrix
        price3 = np.squeeze(np.asarray(np.matrix(historicData3)[:,4]))
        
        # Wait for 1 second, to avoid API limit
        time.sleep(1)

        # Get latest data and show to the user for reference
        newData3 = auth_client.get_product_ticker(product_id=currency3)
        print(newData3)
        currentPrice3 = newData3['price']
    except:
        # In case something went wrong with cbpro
        print("Error Encountered")
        break

    # Calculate the rate of change 11 and 14 units back, then sum them
    CoppockFormula(price)
    coppockres = CoppockFormula.variable

    # The maximum amount of Cryptocurrency that can be purchased with your funds
    possiblePurchase = (float(funding)) / float(currentPrice)
    possiblePurchase1 = (float(funding1)) / float(currentPrice1)
    possiblePurchase2 = (float(funding2)) / float(currentPrice2)
    possiblePurchase3 = (float(funding3)) / float(currentPrice3)

    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    print("ids for currencies")
    print(specificID)
    print(specificID1)
    print(specificID2)
    print(specificID3)
    time.sleep(1)
    print('\n')

    # The amount of currency owned
    owned = float(auth_client.get_account(specificID)['available'])
    owned1 = float(auth_client.get_account(specificID1)['available'])
    owned2 = float(auth_client.get_account(specificID2)['available'])
    owned3 = float(auth_client.get_account(specificID3)['available'])


    # The value of the cryptourrency in USD
    possibleIncome = (float(currentPrice) * owned)
    possibleIncome1 = (float(currentPrice1) * owned1)
    possibleIncome2 = (float(currentPrice2) * owned2)
    possibleIncome3 = (float(currentPrice3) * owned3)

    # Buy Conditions: latest derivative is + and previous is -
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    print("Coppock/BuySell stats")
    statscoppock = coppockres
    print(coppockres)
    print(currency)
    BuySell(buy, coppockres, currency, funding, currentPrice, possibleIncome, funding, owned)

    CoppockFormula(price1)
    coppockres = CoppockFormula.variable
    print(coppockres)
    print(currency1)
    statscoppock1 = coppockres
    BuySell(buy, coppockres, currency1, funding1, currentPrice1, possibleIncome1, funding1, owned1)



    CoppockFormula(price2)
    coppockres = CoppockFormula.variable
    print(coppockres)
    print(currency2)
    statscoppock2 = coppockres
    BuySell(buy, coppockres, currency2, funding2, currentPrice2, possibleIncome2, funding2, owned2)


    CoppockFormula(price3)
    coppockres = CoppockFormula.variable
    statscoppock3 = coppockres
    print(coppockres)
    print(currency3, "\n")
    time.sleep(4)
    BuySell(buy, coppockres, currency3, funding3, currentPrice3, possibleIncome3, funding3, owned3)



    # Printing here to make the details easier to read in the terminal
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    print("iteration number", iteration)

    # Print the details for reference
    stats(currentPrice, funding, owned, currency, statscoppock)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    stats(currentPrice1, funding1, owned1, currency1, statscoppock1)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    stats(currentPrice2, funding2, owned2, currency2, statscoppock2)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    stats(currentPrice3, funding3, owned3, currency3, statscoppock3)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

    # Wait for however long the period variable is before repeating
    time.sleep(60)
    iteration += 1
    if sellstop == True:
        break
