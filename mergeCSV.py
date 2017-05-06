from math import ceil
import time
import calendar, datetime

import pandas as pd

df = pd.read_csv("data/aapl.csv")

def week_of_month(dt):
    """ Returns the week of the month for the specified date.
    """

    first_day = dt.replace(day=1)

    dom = dt.day
    adjusted_dom = dom + first_day.weekday()

    return int(ceil(adjusted_dom/7.0))

def convert_to_week(x):
    day = x.split("-",1)[0]
    if len(day) == 1:
        x="0"+x
    dt = datetime.datetime.strptime(x,"%d-%b-%y")
    return week_of_month(dt)


df['Day'], df['Mon'], df['Year'] = df.iloc[:,0].str.split('-').str
df['Week'] = df.ix[:,0].apply(convert_to_week)
df1 = df.groupby(['Year','Mon','Week']).mean()
df1.to_csv("apple_avg.csv")
