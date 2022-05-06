from ray import workflow
import ray
 
@workflow.virtual_actor
class ShoppingCart:
    ...
    # check status via ``self.shipment_workflow_id`` for avoid blocking
    def do_checkout():
        # Deterministically generate a workflow id for idempotency.
        self.shipment_workflow_id = "ship_{}".format(self.order_id)
        # Run shipping workflow as a separate async workflow.
        ship_items.step(self.items).run_async
            workflow_id=self.shipment_workflow_id