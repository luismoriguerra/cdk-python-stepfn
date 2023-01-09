from aws_cdk import (
    RemovalPolicy,
    Duration,
    Stack,
    # aws_sqs as sqs,
    aws_lambda as _lambda,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_logs as logs,

)
from constructs import Construct


class StepfnStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        log_group = logs.LogGroup(self, "StepFnLogGroup",
                                  removal_policy=RemovalPolicy.DESTROY,
                                  retention=logs.RetentionDays.ONE_DAY
                                  )

        get_users = _lambda.Function(self, "get_users",
                                     code=_lambda.Code.from_asset(
                                         "functions"),
                                     handler="get_users.handler",
                                     timeout=Duration.seconds(900),
                                     runtime=_lambda.Runtime.NODEJS_18_X
                                     )
        process_user = _lambda.Function(self, "process_user",
                                        code=_lambda.Code.from_asset(
                                            "functions"),
                                        handler="process_user.handler",
                                        timeout=Duration.seconds(900),
                                        runtime=_lambda.Runtime.NODEJS_18_X
                                        )

        getUsers = tasks.LambdaInvoke(self, 'GetUsers',
                                      lambda_function=get_users,
                                      )

        process_user = tasks.LambdaInvoke(self, 'ProcessUser',
                                          lambda_function=process_user,
                                          output_path="$.Payload"
                                          )

        usersMap = sfn.Map(self, "GetUsersMapState",
                           max_concurrency=10,
                           items_path=sfn.JsonPath.string_at("$.Payload.users")
                           )
        usersMap.iterator(process_user)

        definition = getUsers.next(
            usersMap
        ).next(sfn.Pass(self, "Done"))

        sfn.StateMachine(self, 'MyStateMachine',
                         definition=definition,
                         tracing_enabled=True,
                         logs=sfn.LogOptions(
                             destination=log_group,
                             level=sfn.LogLevel.ALL)
                         )
