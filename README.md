# Requirements

Various packages will be needed for this project. I won't list them here since the list may grow or shrink drastically over the next few days, and inspection of the code should make the requirements evident. Most of them should be easy to install via pip. If you have trouble running one of these scripts, contact Karan. 


# Architecture

nytimes.py extracts articles from the New York Times Archive API. It saves their abstracts and the presence of each of the keywords (Apple, Amazon, Facebook, Google, and Microsoft). It then exports that data as a csv file and in a Kafka Producer to the "keywords" topic (where the key is the article's abstract and the value is the presence of the keywords).

Another program (currently unwritten) will consume from the keywords topic in Kafka. It will then perform TF-IDF calculations to identify the most important words and add these to the keywords list.

The keywords will be queried against Google Trends (which lacks an official API, so it must be done manually).

A program will be written to output data points, where the x-values will be the Search Volume Index of each of the keywords during a given week, and the y-value will be the stock market performance for that week. The program will then export the data points to the "regression" Kafka topic. This program should be pretty easy since it's literally just reading in data from a few csv's, mergng them, and outputing to Kafka.

Finally, the ml.py script reads in the data points, executes multiple forms of machine learning (currently, we have both Linear and Decision Tree Regression), and cross-validates the model to test its performance.



# Kafja Topics:

## keywords

this is the output of nytimes.py.

Key = abstract of an article

Value = space-separated string of True/False, where the first True/False corresponds to Apple, the second to Amazon, third to Facebook, fourth to Google, and fifth to Microsoft

## regression

this is the input to ml.py

Key = a data point's y value

Value = a data point's x values (features)