#!/usr/bin/env python3
import os

import aws_cdk as cdk
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

        envVars = {
            'STAGE': os.environ.get("STAGE"),
            "AUTH0_ADMIN_CLIENT_SECRET": os.environ.get(
                "AUTH0_ADMIN_CLIENT_SECRET"),
            "AUTH0_ADMIN_CLIENT":  os.environ.get(
                "AUTH0_ADMIN_CLIENT"),
        }

        print('### Running in {} stage'.format(envVars['STAGE']))

        log_group = logs.LogGroup(self, "StepFnLogGroup",
                                  removal_policy=RemovalPolicy.DESTROY,
                                  retention=logs.RetentionDays.ONE_DAY
                                  )

        get_users = _lambda.Function(self, "get_users",
                                     code=_lambda.Code.from_asset(
                                         "functions"),
                                     handler="get_users.handler",
                                     timeout=Duration.seconds(900),
                                     runtime=_lambda.Runtime.NODEJS_18_X,
                                     environment=envVars)
        process_user = _lambda.Function(self, "process_user",
                                        code=_lambda.Code.from_asset(
                                            "functions"),
                                        handler="process_user.handler",
                                        timeout=Duration.seconds(900),
                                        runtime=_lambda.Runtime.NODEJS_18_X,
                                        environment=envVars
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

        definition = getUsers.next(usersMap).next(sfn.Pass(self, "Done"))

        sfn.StateMachine(self, 'MyStateMachine',
                         definition=definition,
                         tracing_enabled=True,
                         logs=sfn.LogOptions(
                             destination=log_group,
                             level=sfn.LogLevel.ALL)
                         )


app = cdk.App()
StepfnStack(app, "LGStepfnStack")

app.synth()
