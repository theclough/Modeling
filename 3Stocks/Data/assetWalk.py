import math
import random
import numpy as np
import matplotlib.pyplot as plt

def driver():

    times = {'min': 1, 'day': 1440, 'year': 525600}
    tInt = times['day']
    opens, closes, volFracsMax, tradeFracsMax, n = initialize('BTCDay.csv',tInt)
    xVals = list(range(n))

    for sims in range(10):
        walk = assetWalk(opens,closes,volFracsMax,tradeFracsMax,n)
        # if sims == 0:
        # # initialize walkMin
        #     best = walk
        # else:
        #     if best[-1] > walk[-1]:
        #         best = walk
        plt.plot(xVals,walk,'b-')
    plt.plot(xVals,closes[1:],'g-')
    plt.xlabel('t [day]')
    plt.ylabel('BTC ($)')
    # plt.title('1st '+str(num)+' Data Points')
    plt.show()
    errors = walk - closes[1:]
    plt.bar(range(n),errors)
    plt.show()
    plt.bar(range(n),errors/closes[1:])
    plt.show()

    return

def dataCreator(l,opens,highs,lows,closes,volumes,trades):
# creates desired np.array()s

    maxVol = -1; maxTrade = -1
    volatilitys = np.zeros(l)
    # avgVals = np.zeros(l)
    # pSlopes = np.zeros(l-1)
    # concavitys = np.zeros(l-2)
    # volFracs = np.zeros(l-1); tradeFracs = np.zeros(l-1)
    for ii in range(l):
        vol = volumes[ii]
        trade = trades[ii]
        avgVal = 0.5*(opens[ii]+closes[ii])
        if maxVol < vol:
            maxVol = vol
        if maxTrade < trade:
            maxTrade = trade
        # if ii != 0:
        #     volFracs[ii-1] = volumes[ii]/volumes[ii-1]
        #     tradeFracs[ii-1] = trades[ii]/trades[ii-1]
        #     pAvgVal = 0.5*(opens[ii-1]+closes[ii-1])
        #     pSlopes[ii-1] = abs(avgVal - pAvgVal)
        #     if ii != 1:
        #         concavitys[ii-2] = (pSlopes[ii-1]-pSlopes[ii-2])#/tInt
        # avgVals[ii] = avgVal
        volatilitys[ii] = (highs[ii]-lows[ii])/avgVal
    volFracsMax = volumes/maxVol
    tradeFracsMax = trades/maxTrade

    return volFracsMax, tradeFracsMax

def initialize(filename, tInt):
# Inputs:
#     filename    :   .csv file with BTC data
#     tInt        :   time interval ('day','min','week')
# Outpus:
#     see dataCreator()
    '''
    labels: 
        [symbol,timestamp,open,high,low,close,volume,trade_count,vwap]
    '''
    with open(filename, 'r') as fp:
        data = fp.readlines()[1:]
    
    l = len(data)
    xVals = list(range(l))
    opens = np.zeros(l)
    highs = np.zeros(l)
    lows = np.zeros(l)
    closes = np.zeros(l+1)
    volumes = np.zeros(l)
    trades = np.zeros(l)
    for stuff,ii in zip(data,range(l)):
        dataPt = stuff.strip('\n').split(',')
        opens[ii] = float(dataPt[2])
        highs[ii] = float(dataPt[3])
        lows[ii] = float(dataPt[4])
        closes[ii+1] = float(dataPt[5])
        volumes[ii] = float(dataPt[6])
        trades[ii] = int(dataPt[7].split('.')[0])
    closes[0] = opens[0]
    
    volFracsMax, tradeFracsMax = dataCreator(l,opens,highs,lows,closes,volumes,trades)
    return opens, closes, volFracsMax, tradeFracsMax, l

def deltaMu(priceData):
# Inputs:
#     priceData   :   vector of all prices up to time t_i
# Output:
#     mu1, mu2    :   mean(priceData), mean(priceData[:-1])
    
    ct = 0
    sum = 0
    for price in priceData:
        ct += 1
        sum += price

    mu2 = sum/ct
    mu1 = (sum-priceData[-1])/(ct-1)

    return mu1,mu2

def deltaVar(mu1,mu2,P1,P2):
# Inputs:
#     mu1,mu2     :   means at t_[i-1],t_i
#     P1,P2       :   prices at t_[i-1],t_i
# Output:
#     dVar        :   delta variance btween time t_[i-1] & t_i

    dVar = (mu2-mu1)*(mu2+mu1) + 2.*(mu1*P1-mu2*P2) + (P2-P1)*(P2+P1)
    # = (m2-S2)**2 - (m1-S1)**2
    
    return dVar

def volatility(vFMax,tFMax):
# Inputs:
#     vFMax   :   volFracMaxs[ii]
#     tFMax   :   tradeFracMaxs[ii]
# Output:
#     volty   :   volatility from linear regression in dimless.py

    return math.e**(-1.99539)*(vFMax**(0.24023))*(tFMax**(0.24198))

def assetWalk(opens,closes,volFracsMax,tradeFracsMax,n):
# predicts given open price of session
# Inputs:
#     averagePrices   :   np.array with bitcoin data pts = 0.5(open+close)
#     voFracsMax      :   np.array with volume data pts = volume[ii]/maxVolume
#     tradeFracsMax   :   np.array with volume data pts = volume[ii]/maxVolume
#     n               :   length of data (bc already have)
# Outputs:
#     walk            :   predicted values of asset using random walk

# walk[ii+1] = open[ii] + calc stuff

    walk = np.zeros(n-1)
    # starts at 2nd session so enough to calc. parameters
    walk[0] = opens[0]

# walk accodring to formula
    volMax = volumes[0]
    tMax = trades[0]
    for ii in range(1,n):
        vol = volumes[ii]; trade = trades[ii];
        if volMax < volumes[ii]:
            volMax = vol
        if tMax < trade:
            tMax = trade
'''
    cal maxes as go along rather than volFracsMAx and tFracsMax arrays
'''
        data1 = closes[ii-1]; data2 = opens[ii];
        mu1,mu2 = deltaMu(closes[:ii-1].append(opens[ii]))
        dVar = deltaVar(mu1,mu2,data1,data2)
        # volFrac = vData[ii]/vData[ii-1]
        # pSlope = prevSlope(data1,data2,deltaT)
        sigma = volatility(volFracsMax[ii],tradeFracsMax[ii])
        
        # walk[ii+1] = walk[ii] + (mu2-mu1)*random.uniform(0,pSlope) + dVar/math.sqrt(abs(dVar))*random.uniform(0,volFrac)
        '''
        make walk[ii+1] = open[ii] + stuff
        '''
        value = (mu2-mu1)*volFracsMax[ii]*random.uniform(0,1) + dVar/math.sqrt(abs(dVar))*random.uniform(0,1)
        if abs(value/walk[ii]) >= sigma:
            walk[ii+1] = (1+sigma)*opens[ii]
        else:
            walk[ii+1] = opens[ii] + (mu2-mu1)*volFracsMax[ii]*random.uniform(0,1) + dVar/math.sqrt(abs(dVar))*random.uniform(0,1)
#        walk[ii+1] = data[ii] + (mu2-mu1)*volFrac*random.uniform(0,1) + dVar/math.sqrt(abs(dVar))*random.uniform(0,0.2)
        # walk[ii+1] = walk[ii] + (mu2-mu1) + dVar/math.sqrt(abs(dVar))*random.uniform(0,volFrac)
        # walk[ii+1] = walk[ii] + (mu2-mu1) + dVar/math.sqrt(abs(dVar))*random.uniform(0,volFrac)
    
    return walk

driver()