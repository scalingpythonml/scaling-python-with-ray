from ray import workflow

@workflow.step
def faulty_function() -> str:
    if random.random() > 0.95:
        raise RuntimeError("Found failure")
    return "OK"
 
# Run 5 times before giging up
s1 = faulty_function.options(max_retries=5).step()
s1.run()
 
@workflow.step
def handle_errors(result: Tuple[str, Exception]):
    # Setting the exception field to NONE on success 
    err = result[1]
    if err:
        return "There was an error: {}".format(err)
    else:
        return "OK"
 
# `handle_errors` receives a tuple of (result, exception).
s2 = faulty_function.options(catch_exceptions=True).step()
handle_errors.step(s2).run()

