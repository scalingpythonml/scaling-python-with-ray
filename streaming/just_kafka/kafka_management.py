from confluent_kafka.admin import AdminClient, NewTopic

admin = AdminClient({'bootstrap.servers': 'localhost:9092'})

# Delete topics
fs = admin.delete_topics(['test'])

# Wait for each operation to finish.
for topic, f in fs.items():
    try:
        f.result()  # The result itself is None
        print("Topic ", topic, " is deleted")
    except Exception as e:
        print("Failed to delete topic ", topic, " error ", e)

# Call create_topics to asynchronously create topics.
fs = admin.create_topics([NewTopic('test', num_partitions=10, replication_factor=1)])

# Wait for each operation to finish.
for topic, f in fs.items():
    try:
        f.result()  # The result itself is None
        print("Topic ", topic, " is created")
    except Exception as e:
        print("Failed to create topic ", topic, " error ", e)