from ray import workflow

@workflow.step
def book_flight(...) -> Flight: ...
 
@workflow.step
def book_hotel(...) -> Hotel: ...
 
@workflow.step
def finalize_or_cancel(
    flights: List[Flight],
    hotels: List[Hotel]) -> Receipt: ...
 
@workflow.step
def book_trip(origin: str, dest: str, dates) ->
        "Workflow[Receipt]":
    # Note that the workflow engine will not begin executing
    # child workflows until the parent step returns.
    # This avoids step overlap and ensures recoverability.
    f1: Workflow = book_flight.step(origin, dest, dates[0])
    f2: Workflow = book_flight.step(dest, origin, dates[1])
    hotel: Workflow = book_hotel.step(dest, dates)
    return finalize_or_cancel.step([f1, f2], [hotel])
 
fut = book_trip.step("OAK", "SAN", ["6/12", "7/5"])
fut.run()  # returns Receipt(...)