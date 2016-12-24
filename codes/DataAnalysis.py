import numpy as np
import csv
from matplotlib import pyplot as plt
import math as m
import pandas as pd
from statsmodels.tsa.stattools import adfuller
import statsmodels.tsa.stattools as sm
#from statsmodels.tsa.stattools import pacf, acf
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.ar_model import AR
import statsmodels.api as sms
import statsmodels.stats.api as sms1


filename = 'femtodata_24d_100p1.csv'

def rootmse(x,xpred):
    sum = 0.0
    for i in range(len(x)):
            sum += m.pow(x[i]-xpred[i],2)
    if sum > 0:
        rmse = m.sqrt (sum/(len(x)))
        return round(rmse,2)

    return 0


def movingaverage(values,window):
    weigths = np.repeat(1.0, window)/window
    smas = np.convolve(values, weigths, 'valid')
    return smas

def ExpSmoothing(data,a):
    S = [0]
    for i in range(1,len(data)):
        S.append(a*data[i-1] + (1-a)* S[i-1])

    return S


def task1(train,test):
    rmse=[]
    X=[]

    #for m in range(2,len(train)+1):
    for m in range(2,20):

        predicted = movingaverage(train,m)
        a = predicted.tolist()

        for i in range(m-1):
            a.insert(0,train[m-i-1])

        predicted = np.array(a)   
        rmse.append(rootmse(train,predicted))

    #print len(rmse)
    minimum = rmse.index(min(rmse))

    plt.plot(rmse)
    plt.ylabel("RMSE")
    plt.xlabel("k")
    plt.title('RMSE Vs k')
    plt.show()

    #Plot predicted values using best m value
    m = minimum + 2

    predicted = movingaverage(train,m)
    a = predicted.tolist()

    for i in range(m-1):
        a.insert(0,train[m-i-1])

    predicted = np.array(a)   

    for i in range(len(train)):
        X.append(i)
        
    fig, ax = plt.subplots()
    ax.plot(X, train, '-', color='blue', linewidth=1,label = 'Actual')
    ax.plot(X, predicted, '-', color='red', linewidth=1,label = 'Predicted')
    ax.set_ylabel("Magnitude")
    ax.set_xlabel("Observation")
    ax.set_title("Actual Vs Predicted")
    plt.legend()
    plt.show()

    print '---------------------------------------------------'
    print 'Best value of k: ', m
    print 'Minimum value RMSE: ', rmse[minimum]
    
    
    ######Task4
    #print len(test)
    predicted_test = movingaverage(test,m)
    a = predicted_test.tolist()

    for i in range(m-1):
        a.insert(0,test[m-i-1])

    predicted_test = np.array(a)

    #print len(predicted_test)

    rmse = rootmse(test,predicted_test)
    #print rmse
    X = []
    for i in range(len(test)):
        X.append(i)

    fig, ax = plt.subplots()
    ax.plot(X, test, '-', color='blue', linewidth=1,label = 'Actual_test')
    ax.plot(X, predicted_test, '-', color='red', linewidth=1,label = 'Predicted_test')
    ax.set_ylabel("Magnitude")
    ax.set_xlabel("Observation")
    ax.set_title("Actual Vs Predicted Test Values")
    plt.legend()
    plt.show()

    print 'Value of RMSE for test set: ', rmse
    print '---------------------------------------------------'

            
def task2(train,test):
    rmse=[]
    Y=[]

    #print len(train)

    a = np.linspace(0, 1, 100)
    a = np.round(a,2)
    #print a
    for m in range(2,len(a)+1):

        predicted = ExpSmoothing(train,a[m-1])

        E = [x2 - x1 for (x1, x2) in zip(train, predicted)]

        #rmse.append(np.linalg.norm(X - Xbar) / np.sqrt(n))
        rmse.append(rootmse(train,predicted))

    
        #print E
    #print rmse
    #print len(rmse)
    minimum = rmse.index(min(rmse))

    plt.plot(rmse)
    plt.ylabel("RMSE")
    plt.xlabel("a")
    plt.title('RMSE Vs a')
    plt.show()

    #Plot predicted values using best a value
    a = a[minimum]
    #print a

    predicted = ExpSmoothing(train,a)
    #print len(predicted)

    X  = []
    for i in range(len(train)):
        X.append(i)
        
    fig, ax = plt.subplots()
    ax.plot(X, train, '-', color='blue', linewidth=1,label = 'Actual')
    ax.plot(X, predicted, '-', color='red', linewidth=1,label = 'Predicted')
    ax.set_ylabel("Magnitude")
    ax.set_xlabel("Observation")
    ax.set_title("Actual Vs Predicted")
    plt.legend()
    plt.show()

    print '---------------------------------------------------'
    print 'Best value of a: ', a
    print 'Minimum value RMSE: ', rmse[minimum]
    
    
    ######Task4
    #print len(test)
    predicted_test = ExpSmoothing(test,a)
    #print len(predicted_test)

    rmse = rootmse(test,predicted_test)
    #print rmse
    X = []
    for i in range(len(test)):
        X.append(i)

    fig, ax = plt.subplots()
    ax.plot(test[3:], '-', color='blue', linewidth=1,label = 'Actual_test')
    ax.plot(predicted_test[3:], '-', color='red', linewidth=1,label = 'Predicted_test')
    ax.set_ylabel("Magnitude")
    ax.set_xlabel("Observation")
    ax.set_title("Actual Vs Predicted Test Values")
    plt.legend()
    plt.show()

    print 'Value of RMSE for test set: ', rmse
    print '---------------------------------------------------'


def task3(train,test):
    
    rmse=[]
    Y=[]
    pacf1 = sm.pacf(train,nlags=20)
    
    #Plot PACF:
    
    plt.subplot(111)
    plt.stem(np.linspace(0,len(pacf1),len(pacf1)),pacf1)
    plt.axhline(y=0,linestyle='--',color='gray')
    plt.axhline(y=0.2,linestyle='--',color='gray')
    plt.axhline(y=-0.2,linestyle='--',color='gray')
    plt.title('Partial Autocorrelation Function')
    plt.tight_layout()
    plt.show()
    
    pacf1 = pacf1.tolist()
    for i in pacf1:
        if i < 0.2:
            p = pacf1.index(i)
            break
    p = p - 1
    model = ARIMA(train, order=(p, 0, 0))
    results_AR = model.fit()
    print results_AR.summary()
    
    predicted = results_AR.fittedvalues
    parameters = results_AR.params
    DWtest = sms.stats.durbin_watson(results_AR.resid)

    a = predicted.tolist()

    #QQ plot of residuals
    fig = sms.qqplot(results_AR.resid,dist="norm",line='s')
    plt.show()

    #Scatter plot of residuals
    plt.figure();
    plt.scatter(predicted,results_AR.resid);
    plt.plot([6.95, 7.07], [0,0], 'k-',color='red');
    plt.title('Residual Dependence/Correlation Plot');
    plt.ylabel('Residuals');
    plt.xlabel('Fitted values');
    plt.show()

    #Plot Hitogram of residuals
    plt.figure();
    plt.hist(results_AR.resid);
    plt.title('Histogram of residuals');
    plt.show()

    name = ['Jarque-Bera', 'Chi^2 two-tail prob.', 'Skew', 'Kurtosis']
    test1 = sms1.jarque_bera(results_AR.resid)
    chi = zip(name, test1)
    
    rmse = rootmse(train,predicted)
    print ''
    print '---------------------------------------------------'
    print 'Best value of p chosen from pacf: ', p
    print 'Parameters of AR(' + str(p) + ') model: \ncons: ' + str(results_AR.params[0]) + '\na1: ' + str(results_AR.params[1])
    #+ '\na2: ' + str(results_AR.params[2]) + '\n'
    print 'RMSE value for training data: ', rmse
    print 'chi-Squared test value: ', chi[1]
    

    X = []
    for i in range(len(train)):
        X.append(i)
    
    fig, ax = plt.subplots()
    ax.plot(X, train, '-', color='blue', linewidth=1,label = 'Actual')
    ax.plot(X, predicted, '-', color='red', linewidth=1,label = 'Predicted')
    ax.set_ylabel("Magnitude")
    ax.set_xlabel("Observation")
    ax.set_title("Actual Vs Predicted")
    plt.legend()
    plt.show()
    
    ######Task4
    #predicted_test = results_AR.predict(1500,1980,dynamic=True)
    #a = predicted_test.tolist()

    a1 = results_AR.params[1]
    #a2 = results_AR.params[2]
    mean = results_AR.params[0]
    const = mean*(1-a1)
    #-a2)
    
    predictedT = []
    for i in range(1, len(test)+1):
        value = const + a1*test[i-1]
        #+ a2*test[i-2]
        predictedT.append(value)

    #predictedT.insert(0,(mean*(1-a1) + a1*test[0]))
    predictedT.insert(0,mean)
    
    #rmse = rootmse(test,predicted_test)
    rmseT = rootmse(test,predictedT)
    
    fig, ax = plt.subplots()
    ax.plot(test, '-', color='blue', linewidth=1,label = 'Actual_test')
    ax.plot(predictedT, '-', color='red', linewidth=1,label = 'Predicted_test')
    ax.set_ylabel("Magnitude")
    ax.set_xlabel("Observation")
    ax.set_title("Actual Vs Predicted Test Values")
    plt.legend()
    plt.show()

    print 'Value of RMSE for test set: ', rmseT
    print '---------------------------------------------------'

def dktest(timeseries):
    print 'Results of Dickey-Fuller Test:'
    dftest = adfuller(timeseries, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in dftest[4].items():
        dfoutput['Critical Value (%s)'%key] = value
    print dfoutput

def main():
    data=[]
    X= []
    
    #Read column wise data
    with open(filename,'r') as dest_f:
        data_iter = csv.DictReader(dest_f, delimiter = ',')
        headers = data_iter.fieldnames
        for row in data_iter:
            X.append(float(row['F1']))

    #X = np.log(X)
    #X = X.tolist()
    #X = X - X.shift()
    #dktest(X)
    #X=X[20:]
    train = X[:1440]
    test = X[1440:1728]
    
    plt.plot(train)
    plt.show()

    task1(train,test)
    task2(train,test)
    task3(train,test)

main()
