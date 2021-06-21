from flask import Flask, render_template, request, redirect

app = Flask(__name__)
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['TESTING'] = True

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['Enter Stock Ticker Info here (i.e. GOOG)']
    processed_text = text.upper()
    return processed_text

@app.route('/')
def home():

    import re #string parsing
    import requests #to download html data
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from bokeh.plotting import figure, output_file, save
    from bokeh.io import output_notebook, push_notebook, show, save
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    import os
    from dotenv import load_dotenv

    API_KEY = os.environ[‘MY_API_KEY’]

    if request.method == 'POST':
        content = requests.get(
            "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=" +
            convert_input(request.form['stock_tick']) +
            "&interval=5min&apikey=" + API_KEY #+"+4PJK6E44KAP57MW0"
        json_response = json.loads(content.text)
        print json_response
        return render_template("General_attempt.html", response=json_response) if json_response != [] else render_template(
            "General_attempt.html", response="")
    else:
        return render_template("restaurant_list.html")

    url_nm = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol="+stock_tick+"&interval=5min&apikey=4PJK6E44KAP57MW0"
    url = url_nm#'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=4PJK6E44KAP57MW0'
    r = requests.get(url)
    APIdata = r.json()
    metadata = APIdata.pop("Meta Data")

    #print(APIdata)
    #API = pd.DataFrame.from_dict(APIdata)
    API = (pd.json_normalize(APIdata['Time Series (5min)'])).T
    API2= list((API).index)

    def conv_dt(fnx, dt):
      test= re.search("(\d+[-]\d+[-]\d+\s\d+[:]\d+[:]\d+)\.(\d+)\.\s(\w+)", fnx[dt])
      return test

    API['datetime']= pd.to_datetime([(conv_dt(API2,tm))[1] for tm in range(len(API2))])
    API['state'] = [(conv_dt(API2,tm))[2] for tm in range(len(API2))]
    API['statetxt'] = [(conv_dt(API2,tm))[3] for tm in range(len(API2))]

    API = API.reset_index(drop=True);
    API.rename(columns={0 :'value'}, inplace= True)
    API['value'] = pd.to_numeric(API['value'], downcast="float")

    bokeh_graph = figure(title = "Daily High", x_axis_type='datetime', plot_height=300, plot_width = 600, )

    y=API[API['statetxt']=='high'].value
    x=API[API['statetxt']=='high'].datetime

    bokeh_graph.line(x,y)
    bokeh_graph.xaxis.axis_label = "date/time of day"
    bokeh_graph.yaxis.axis_label = "Price ($)"

    home_path = "/Users/Aroob Abdelhamid/"
    currpath = os.path.join(home_path, "earth-analytics", "flask_repo_TDI", "flask-framework", "templates","bokeh_plot.html")
    output_file(currpath, title="Daily High Plot")
    save(bokeh_graph)

    # html_bokeh = file_html(bokeh_graph, CDN, "Daily High")
    # home_path = "/Users/Aroob Abdelhamid/"
    # currpath = os.path.join(home_path, "earth-analytics", "flask_repo_TDI", "flask-framework", "templates","bokeh_plot.html")
    # with open(currpath, "a") as f:
    #     f.write(html_bokeh)

    return render_template("General_attempt.html")

def index():
  return render_template('index.html')

@app.route('/about')
def about():
  return render_template('about.html')

if __name__ == '__main__':
   app.run(host = "localhost", debug=True)
