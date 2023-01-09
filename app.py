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

        log_group = logs.LogGroup(self, "StepFnLogGroup",
                                  removal_policy=RemovalPolicy.DESTROY,
                                  retention=logs.RetentionDays.ONE_DAY
                                  )
        print(os.environ.get("STAGE"))
        get_users = _lambda.Function(self, "get_users",
                                     code=_lambda.Code.from_asset(
                                         "functions"),
                                     handler="get_users.handler",
                                     timeout=Duration.seconds(900),
                                     runtime=_lambda.Runtime.NODEJS_18_X,
                                     environment={
                                         'STAGE': os.environ.get("STAGE"),
                                         "AUTH0_ADMIN_CLIENT_SECRET": os.environ.get(
                                             "AUTH0_ADMIN_CLIENT_SECRET"),
                                         "AUTH0_ADMIN_CLIENT":  os.environ.get(
                                             "AUTH0_ADMIN_CLIENT"),
                                     })
        process_user = _lambda.Function(self, "process_user",
                                        code=_lambda.Code.from_asset(
                                            "functions"),
                                        handler="process_user.handler",
                                        timeout=Duration.seconds(900),
                                        runtime=_lambda.Runtime.NODEJS_18_X,
                                        environment={
                                            'STAGE': os.environ.get("STAGE"),
                                            "AUTH0_ADMIN_CLIENT_SECRET": os.environ.get(
                                                "AUTH0_ADMIN_CLIENT_SECRET"),
                                            "AUTH0_ADMIN_CLIENT":  os.environ.get(
                                                "AUTH0_ADMIN_CLIENT"),
                                        }
                                        )

        getUsers = tasks.LambdaInvoke(self, 'GetUsers',
                                      lambda_function=get_users,
                                      )

        process_user = tasks.LambdaInvoke(self, 'ProcessUser',
                                          lambda_function=process_user,
                                          output_path="$.Payload"
                                          )

        usersMap = sfn.Map(self, "GetUsersMapState",
                           max_concurrency=2,
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


app = cdk.App()
StepfnStack(app, "LGStepfnStack",
            # If you don't specify 'env', this stack will be environment-agnostic.
            # Account/Region-dependent features and context lookups will not work,
            # but a single synthesized template can be deployed anywhere.

            # Uncomment the next line to specialize this stack for the AWS Account
            # and Region that are implied by the current CLI configuration.

            # env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

            # Uncomment the next line if you know exactly what Account and Region you
            # want to deploy the stack to. */

            # env=cdk.Environment(account='123456789012', region='us-east-1'),

            # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
            )

app.synth()
