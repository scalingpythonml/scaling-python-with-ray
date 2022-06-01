from ray import workflow
import time
 
# Create an event which finishes after 60 seconds.
event1_step = workflow.wait_for_event(workflow.event_listener.TimerListener, time.time() + 60)
 
# Create another event which finishes after 30 seconds.
event2_step = workflow.wait_for_event(workflow.event_listener.TimerListener, time.time() + 30)
 
@workflow.step
def gather(*args):
    return args;
 
# Gather will run after 60 seconds, when both event1 and event2 are done.
gather.step(event1_step, event2_step).run()