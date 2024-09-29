from prefect import flow, task
from prefect.blocks.system import String

string_block = String.load("redback-operations-trial")

@task
def create_message():
    msg = string_block.value
    return(msg)

@flow
def something_else():
    result = 10
    return(result)

@flow
def hello_world():
    sub_flow_message = something_else()
    task_message = create_message()
    new_message = task_message + str(sub_flow_message)
    print(new_message)

if __name__ == "__main__":
   hello_world.serve(name="my-first-deployment",
                      tags=["onboarding"],
                      parameters={"goodbye": True},
                      interval=60)
   # this is all the code required for the data orchestration
   # we will do the required testing for the files that need data orchestration.