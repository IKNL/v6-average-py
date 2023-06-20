from vantage6.tools.mock_client import MockAlgorithmClient

# Initialize the mock server. The datasets simulate the local datasets from
# the node. In this case we have two parties having two different datasets:
# a.csv and b.csv. The module name needs to be the name of your algorithm
# package. This is the name you specified in `setup.py`, in our case that
# would be v6-average-py.
client = MockAlgorithmClient(
    datasets=[
        {
            "database": "./v6-average-py/local/data.csv",
            "type": "csv",
            "input_data": {}
        },
        {
            "database": "./v6-average-py/local/database.csv",
            "type": "csv",
            "input_data": {}
        }
    ],
    module="v6-average-py"
)

# to inspect which organization are in your mock client, you can run the
# following
organizations = client.organization.list()
org_ids = ids = [organization["id"] for organization in organizations]

# we can either test a RPC method or the master method (which will trigger the
# RPC methods also). Lets start by triggering an RPC method and see if that
# works. Note that we do *not* specify the RPC_ prefix for the method! In this
# example we assume that both a.csv and b.csv contain a numerical column `age`.
average_partial_task = client.task.create(
    input_={
        'method': 'average_partial',
        'kwargs': {
            'column_name': 'age'
        }
    },
    organization_ids=org_ids
)

# You can directly obtain the result (we dont have to wait for nodes to
# complete the tasks)
results = client.result.get(average_partial_task.get("id"))

# To trigger the master method you also need to supply the `master`-flag
# to the input. Also note that we only supply the task to a single organization
# as we only want to execute the central part of the algorithm once. The master
# task takes care of the distribution to the other parties.
average_task = client.task.create(
    input_={
        'master': 1,
        'method': 'master',
        'kwargs': {
            'column_name': 'age'
        }
    },
    organization_ids=[org_ids[0]]
)

results = client.result.get(average_task.get("id"))
print(results)
