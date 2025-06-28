from django.shortcuts import render , redirect
from django.utils.timezone import now
from django.contrib import messages
import mysql.connector as sql
import yfinance as yf
import numpy as np
import pandas as pd
import json
from scipy.stats import norm
from alpha_vantage.timeseries import TimeSeries
import time
from datetime import datetime
fn = ''
ln = ''
em = ''
pn =''
usr =''
pwd =''

# Create your views here.
def Front_page(request) :
    return render (request , 'Front.html' , {'timestamp': now().timestamp()})

def Login_page(request) :
    return render (request ,'login.html')

def registration(request) :
    return render (request , 'registration.html', {'timestamp': now().timestamp()} )

def rg_Front_page(request) :
    return render (request , 'Front.html' , {'timestamp': now().timestamp()})

def contact(request) :
    return render (request , 'contact.html' , {'timestamp': now().timestamp()})

def signaction(request):
    global fn , ln , em , pn , usr , pwd 
    if request.method == 'POST':
        m = sql.connect(host='localhost',user='root',passwd='24password',database='PORTFOLIO_OPTIMIZATION_DB')
        cursor=m.cursor()
        d= request.POST
        for key , value in d.items():
            if key == 'first_name':
                fn = value
            if key == 'last_name':
                ln = value
            if key == 'email':
                em = value
            if key == 'phone_number':
                pn = value
            if key == 'username':
                usr = value
            if key == 'password':
                pwd = value
        

        c = "insert into users Values('{}','{}','{}','{}','{}','{}')".format(fn,ln,em,pn,usr,pwd)
        cursor.execute(c)
        m.commit()

    return render(request , "Front.html")



def loginaction(request):
    global pwd , usr
    if request.method=="POST":
        m=sql.connect(host="localhost",user="root",passwd="24password",database='PORTFOLIO_OPTIMIZATION_DB')
        cursor=m.cursor()
        d=request.POST
        for key,value in d.items():
            if key=="username":
                usr=value
            if key=="password":
                pwd=value
        
        c="select * from users where username='{}'and password='{}'".format(usr,pwd)
        cursor.execute(c)
        t=tuple(cursor.fetchall())
        if t==():
            return render(request,'error.html')
        else:
            return render(request,"portfolio.html")

    return render(request,'login.html')

def login_error(request) :
    return render (request , 'error.html' , {'timestamp': now().timestamp()})


def portfolio(request) :
    return render (request , 'portfolio.html' , {'timestamp': now().timestamp()})


def about(request) :
    return render (request , 'about.html' , {'timestamp': now().timestamp()})


def portfolio_analysis(request):
    chart_data = None
    results = None
    corr_data = None
    scatter_data = None 
    sharpe_pie_data = None
    sma_chart_data = None 

    
    if request.method == "POST":
        try:
            # Extract stocks and weights from input
            stocks = [
                request.POST.get("stock1"),
                request.POST.get("stock2"),
                request.POST.get("stock3"),
                request.POST.get("stock4"),
            ]
            weights = [
                float(request.POST.get("weight1")),
                float(request.POST.get("weight2")),
                float(request.POST.get("weight3")),
                float(request.POST.get("weight4")),
            ]
            
            
            if None in stocks or None in weights :
                raise ValueError("Please enter all stock names and weights.")

            
            weights = np.array(weights) / np.sum(weights) 

           
            data= yf.download(stocks, period="1y",   interval="1d")["Close"]
            returns = data.pct_change().dropna()

            # Portfolio calculations
            expected_return = np.dot(returns.mean(), weights) * 252
            volatility = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
            sharpe_ratio = expected_return / volatility
            # var_95 = np.percentile(np.dot(returns, weights), 5)
            port_returns = np.dot(returns, weights)
            port_mean = np.mean(port_returns)
            port_std = np.std(port_returns)
            confidence_level = 0.95
            z_score = norm.ppf(1 - confidence_level)  
            VaR_95_daily = z_score * port_std
            VaR_95_annual = VaR_95_daily * np.sqrt(252)
            open_positions = (data.iloc[-1])



            risk_free_rate = 0.05  
            stock_expected_returns = returns.mean() * 252
            stock_volatility = returns.std() * np.sqrt(252)
            individual_sharpe_ratios = (stock_expected_returns - risk_free_rate) / stock_volatility  

            
            max_sharpe_stock = individual_sharpe_ratios.idxmax()
            min_sharpe_stock = individual_sharpe_ratios.idxmin()
            max_sharpe_value = individual_sharpe_ratios.max()
            min_sharpe_value = individual_sharpe_ratios.min()

           
            sharpe_pie_data = json.dumps({
                "labels": [max_sharpe_stock, min_sharpe_stock],  
                "values": [max_sharpe_value, min_sharpe_value],  
                "colors": ["#4CAF50", "#F44336"],  # Green for Max, Red for Min
            })

            chart_data = json.dumps({
                "labels": stocks,
                "weights": weights.tolist(),
            })
            

            corr = returns.corr().round(2)
            matrix_data = []
            for i , row  in enumerate(corr.index):
                for j , col in enumerate(corr.columns):
                    matrix_data.append({
                        'x': j,
                        'y': i,
                        'v': corr.iloc[i, j]
                    })

            corr_data = json.dumps({
                "labels": list(corr.columns),
                "data": matrix_data
            })

            num_portfolios = 1000
            port_returns = []
            port_volatility = []
            sharpe_ratios = []
            scatter_points = []

            max_sharpe_weights = []
            min_vol_weights = []

            

            for _ in range(num_portfolios):
                rand_weights = np.random.random(len(stocks))
                rand_weights /= np.sum(rand_weights)
                ret = np.dot(returns.mean(), rand_weights) * 252
                vol = np.sqrt(np.dot(rand_weights.T, np.dot(returns.cov() * 252, rand_weights)))
                sharpe = ret / vol
                port_returns.append(ret)
                port_volatility.append(vol)
                sharpe_ratios.append(sharpe)
                scatter_points.append({
                    'x': vol,
                    'y': ret,
                    'r': 5,  # dot size
                    'sharpe': sharpe,
                    'weights': rand_weights.tolist()
                })

            max_sharpe = np.argmax(sharpe_ratios)
            min_vol = np.argmin(port_volatility)
            max_sharpe_weights = scatter_points[max_sharpe]['weights']
            min_vol_weights = scatter_points[min_vol]['weights']
            min_vol_sharpe = sharpe_ratios[min_vol]

            scatter_data = json.dumps({
                "points": scatter_points,
                "best": {
                    "x": port_volatility[max_sharpe],
                    "y": port_returns[max_sharpe],
                    "weights": max_sharpe_weights,
                    "sharpe": sharpe_ratios[max_sharpe]
                },
                "min_vol": {
                    "x": port_volatility[min_vol],
                    "y": port_returns[min_vol],
                    "weights": min_vol_weights,
                    "sharpe": min_vol_sharpe,
                }
            })
 
                   # Calculate SMA30
            sma30 = data.rolling(window=30).mean()
            data.index = pd.to_datetime(data.index)
            sma_chart_data = {
                  "labels": data.index.strftime('%Y-%m-%d').tolist(),
                  "datasets": []
                  } 

            colors = ["blue", "green", "red", "orange"]  
            color = ["Black", "yellow", "voilet", "Brown"]  

            for i, stock in enumerate(stocks):
                 close_prices = data[stock].replace({np.nan: None}).tolist()
                 sma_values = sma30[stock].replace({np.nan: None}).tolist()
                #  close_prices = data[stock].fillna(None).tolist()
                #  sma_values = sma30[stock].fillna(None).tolist()

                 sma_chart_data["datasets"].append({
                      "label": f"{stock} Close Price",
                      "data": close_prices,
                      "borderColor": colors[i],
                      "fill": False
                      })
                 sma_chart_data["datasets"].append({
                      "label": f"{stock} SMA30",
                      "data":sma_values ,
                      "borderColor": color[i],
                      "borderDash": [5, 5],  # Dashed line for SMA30
                      "fill": False
                      })
                 
            sma_chart_data = json.dumps(sma_chart_data)
    

            # Results Dictionary
            results = {
                "expected_return": f"{expected_return:.2%}",
                "volatility": f"{volatility:.2%}",
                "sharpe_ratio": f"{sharpe_ratio:.2f}",
                # "var_95": f"{var_95:.2f}",
                "VaR_95_annual": f"{VaR_95_annual:.2f}",
                "VaR_95_daily": f"{VaR_95_daily:.2f}",
                "open_positions": open_positions.to_dict(),
            }
        except ValueError as e:
            return render(request, "portfolio.html", {"error": str(e)})

    return render(request, "portfolio.html", {"chart_data": chart_data, 
                                              "results": results , 
                                              "corr_data": corr_data , 
                                              "scatter_data": scatter_data ,
                                              "sharpe_pie_data": sharpe_pie_data ,
                                              "sma_chart_data": sma_chart_data
                                              })
