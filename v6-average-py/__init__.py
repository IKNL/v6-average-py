import pandas as pd

from vantage6.algorithm.tools.util import info
from vantage6.algorithm.client import AlgorithmClient
from vantage6.algorithm.tools.decorators import algorithm_client, data


@algorithm_client
def central_average(client: AlgorithmClient, column_name: str):
    """Combine partials to global model

    First we collect the parties that participate in the collaboration or study
    for which the task is created. Then we send a task to all the parties to compute
    their partial (the row count and the column sum). Then we wait for the results to be
    ready. Finally when the results are ready, we combine them to a global average.

    The algorithm client, provided in the first argument, gives an interface to
    the central server. This is needed to create tasks (for the partial
    results) and collect their results later on. Note that this algorithm client
    is a different client than the user client that you use as a user.
    """
    # Info messages can help you when an algorithm crashes. These info
    # messages are stored in a log file which is send to the server when
    # either a task finished or crashes.
    info("Collecting participating organizations")

    # Collect all organization that participate in this collaboration.
    # These organizations will receive the task to compute the partial.
    organizations = client.organization.list()
    ids = [organization.get("id") for organization in organizations]

    # Request all participating parties to compute their partial. This
    # will create a new task at the central server for them to pick up.
    # We've used a kwarg but is is also possible to use `args`. Although
    # we prefer kwargs as it is clearer.
    info("Requesting partial computation")
    task = client.task.create(
        input_={"method": "partial_average", "kwargs": {"column_name": column_name}},
        organizations=ids,
    )

    # Now we need to wait until all organizations(/nodes) finished
    # their partial. We do this by polling the server for results. It is
    # also possible to subscribe to a websocket channel to get status
    # updates.
    info("Waiting for results")
    results = client.wait_for_results(task_id=task.get("id"))
    info("Partial results are in!")

    # Now we can combine the partials to a global average.
    info("Computing global average")
    global_sum = 0
    global_count = 0
    for output in results:
        global_sum += output["sum"]
        global_count += output["count"]

    return {"average": global_sum / global_count}


@data(1)
def partial_average(df: pd.DataFrame, column_name: str):
    """Compute the average partial

    The data argument contains a pandas-dataframe containing the local
    data from the node.
    """
    # extract the column_name from the dataframe.
    info(f"Extracting column {column_name}")
    numbers = df[column_name]

    # compute the sum, and count number of rows
    info("Computing partials")
    local_sum = float(numbers.sum())
    local_count = len(numbers)

    # return the values as a dict
    return {"sum": local_sum, "count": local_count}
