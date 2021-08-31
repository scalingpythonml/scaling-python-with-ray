# Ray streaming

Based on [blog post](https://www.anyscale.com/blog/serverless-kafka-stream-processing-with-ray), with the code
[here](https://github.com/anyscale/blog/tree/main/ServerlessKafkaStreamProcessing)

Ray also provides a powerfull [streaming library](https://github.com/ray-project/ray/tree/master/streaming) that 
simplifies building of streaming applications

## Kafka with Python

We first show how to use Kafka with Python. Start from the installation of 
[required libraries](https://github.com/confluentinc/confluent-kafka-python/blob/master/examples/requirements.txt):

````
pip3 install -r /Users/boris/Projects/RayStreaming/install/requirements.txt
````

Our example uses JSON message to communicate between Kafka producers and consumers. 
The actual implementation is based on [producer](https://github.com/confluentinc/confluent-kafka-python/blob/master/examples/producer.py) and 
[consumer](https://github.com/confluentinc/confluent-kafka-python/blob/master/examples/consumer.py)

[Install Kafka locally (for Mac)](https://gist.github.com/jarrad/3528a5d9128fe693ca84)

Start zookeeper and kafka

````
brew services start zookeeper
brew services start kafka
````

To create a topic with multiple partitions run [kafka_management](just_kafka/kafka_management.py)
Kafka consumer is [here](just_kafka/data_consumer.py) and producer is [here](just_kafka/data_producer.py)

Once done, stop kafka and zookeeper services:

````
brew services stop kafka
brew services stop zookeeper
````

## Kafka with RAY

We are using Ray 2.0. Install is done using:

````
pip3 install https://s3-us-west-2.amazonaws.com/ray-wheels/latest/ray-2.0.0.dev0-cp37-cp37m-macosx_10_15_intel.whl
````
The image that we will use is:
````
docker pull rayproject/ray:880797-py37
````

Following Ray [blog post](https://www.anyscale.com/blog/serverless-kafka-stream-processing-with-ray)
both Kafka consumer and producer are implemented as [Ray Actors](https://docs.ray.io/en/master/_modules/ray/actor.html)

The [code](ray_with_kafka/ray_kafka.py) demonstrate how to integrate Ray with Kafka Producer/Consumer

See also this [blog post](https://www.anyscale.com/blog/serverless-kafka-stream-processing-with-ray) on how to run it 
on the cluster and scale it up and down. This is done by Ray autoscaler based on the CPU/memory requirements
We still run the fix number of listeners, but autoscaler will decide on the amount of nodes to deploy them on.
So unlike K8 native autoscalers, for example, [keda](https://keda.sh/), which is trying to manage the amount of Kafka
consumers based on the queue depth, A Ray approach is different. Instead of trying to add/remove kafka instances
Ray based application starts the amount of Kafka listeners (actors) and manages the amount of Ray nodes, moving
actors (transparently) to a new node, as the load on the actors increases.

## Kafka with Ray streaming

Based on the example [here](https://github.com/ray-project/ray/blob/master/streaming/python/examples/wordcount.py)