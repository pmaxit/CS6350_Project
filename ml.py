#	DOCUMENTATION	#
#		How to execute:
#			spark-submit ml.py
#		Data Format in Kafka:
#			Key: y value
#			Value: x values (space-separated)
#			Example:
#				y = 1.0		x = 1.0 2.0 3.0


#	SOURCES		#
#		https://spark.apache.org/docs/1.6.2/api/python/pyspark.sql.html
#		http://spark.apache.org/docs/1.6.1/api/python/pyspark.ml.html
#		https://spark.apache.org/docs/1.6.1/ml-classification-regression.html
#		spark.apache.org/docs/1.6.1/ml-guide.html


#	IMPORTS		#
from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.mllib.linalg import Vectors
from pyspark.ml.regression import LinearRegression, DecisionTreeRegressor
from pyspark.ml.evaluation import RegressionEvaluator
from kafka import KafkaConsumer
import os


#	CONSTANTS	#
sc = SparkContext("local", "ml", pyFiles=['ml.py'])
sqlContext = SQLContext(sc)
KAFKA_TOPIC = 'my-topic'
KAFKA_GROUP = 'my-group'
KAFKA_PORT = 'localhost:9092'


#	FUNCTIONS	#
def kafkaStream(topic, group = KAFKA_GROUP, port = KAFKA_PORT):
	return 	KafkaConsumer(topic,
			group_id=group,
			bootstrap_servers=[port])

# returns data as a List of (y, x) Tuples, where x is a Vector
def getFromTopic(topic):
	# Actual Data streamed from Kafka:
	# data = []
	# for message in kafkaStream(topic=topic):
	# 	if message.key == "END":
	# 		break
	# 	y = message.key
	# 	x = Vectors.dense(message.value.split(" "))
	# 	data_point = (y, x)
	# 	data.extend(data_point)

	# Sample Data: use for testing purposes
	data = [
	(1.0, Vectors.dense(2.0)),
	(1.0, Vectors.dense(3.0)),
	(1.0, Vectors.dense(4.0)),
	(2.0, Vectors.dense(5.0)),
	]
	return data

def toDataFrame(data):
	return sqlContext.createDataFrame(data, ["y", "x"])

def trainLRmodel(training_df):
	return LinearRegression(featuresCol="x", labelCol="y", predictionCol="prediction").fit(training_df)

def trainDTmodel(training_df):
	return DecisionTreeRegressor(featuresCol="x", labelCol="y", predictionCol="prediction").fit(training_df)

def test(lr_model, dt_model, testing_df):
	print "The Root-Mean-Square-Error of the Linear Regression Model is " + str(root_mean_square_error(lr_model, testing_df))
	print "The Root-Mean-Square-Error of the Decision Tree Model is " + str(root_mean_square_error(dt_model, testing_df))

def root_mean_square_error(model, testing_df):
	predictions = model.transform(testing_df)
	evaluator = RegressionEvaluator(labelCol="y", predictionCol="prediction", metricName="rmse")
	rmse = evaluator.evaluate(predictions)
	return rmse


#	MAIN METHOD	#
if __name__ == "__main__":
	data = toDataFrame(getFromTopic(KAFKA_TOPIC))
	(training_df, testing_df) = data.randomSplit([0.75,0.25])
	lr_model = trainLRmodel(training_df)
	dt_model = trainDTmodel(training_df)
	test(lr_model, dt_model, testing_df)
