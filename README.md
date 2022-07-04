# message-backend-ray
A Ray port of the message backend

## Design

The core design is three actor types (pooled). 
1. The satelite actor type, for interacting with the swarm.space APIs. 
1. The smtp actor type, which sends/receives e-mails (not yet started)
1. The user actor type, which talks to the database ensures the user state. It passes messages between the satelite pool and messaging pools when condition are met. (not yet started).

In the future the plan is to add a SMS gateway actor type.
