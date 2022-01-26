from confluent_kafka.admin import AdminClient, NewTopic
from time import sleep

def wait_for_operation_completion(futures: dict, success: str, failure: str):
    for topic, f in futures.items():
        try:
            f.result()  # The result itself is None
            print(f'Topic {topic} {success}')
        except Exception as e:
            print(f'{failure} {topic} error {e}')

admin = AdminClient({'bootstrap.servers': 'localhost:9092'})

# Delete topics
fs = admin.delete_topics(['test'])

# Wait for each operation to finish.
wait_for_operation_completion(fs, " is deleted", "Failed to delete topic ")

sleep(2)

# Call create_topics to asynchronously create topics.
fs = admin.create_topics([NewTopic('test', num_partitions=10, replication_factor=1)])

# Wait for each operation to finish.
wait_for_operation_completion(fs, " is created", "Failed to create topic ")