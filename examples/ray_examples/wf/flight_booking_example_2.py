from ray import workflow

@workflow.step
def generate_id() -> str:
   # Generate a unique idempotency token.
   return uuid.uuid4().hex
 
@workflow.step
def book_flight_idempotent(request_id: str) -> FlightTicket:
   if service.has_ticket(request_id):
       # Retrieve the previously created ticket.
       return service.get_ticket(request_id)
   return service.book_flight(request_id)
 
# SAFE: book_flight is written to be idempotent
request_id = generate_id.step()
book_flight_idempotent.step(request_id).run()