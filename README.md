# message-backend-ray
A Ray port of the message backend

## Design

The core design is four actor types (pooled).
1. The satelite actor type, for interacting with the swarm.space APIs. 
1. The smtp server actor type, which receives e-mails.
1. The smtp client actor type, that sends outbound e-mails.
1. The user actor type, which talks to the database ensures the user state. It passes messages between the satelite pool and messaging pools when condition are met. (not yet started).

In the future the plan is to add a SMS gateway actor type.
