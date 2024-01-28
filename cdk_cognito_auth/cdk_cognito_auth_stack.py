import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_cognito as _cognito,
    aws_apigateway as _apigateway,
)
from constructs import Construct
import os


class CdkCognitoAuthStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Cria um pool de usuários do Cognito.
        user_pool = _cognito.UserPool(
            self,
            "TestUserPool",
            user_pool_name="TestUserPool",
            self_sign_up_enabled=True,
            sign_in_aliases=_cognito.SignInAliases(email=True),
            auto_verify=_cognito.AutoVerifiedAttrs(email=True),
            password_policy=_cognito.PasswordPolicy(
                min_length=8,
                require_digits=True,
                require_lowercase=True,
                require_uppercase=True,
            ),
            standard_attributes=_cognito.StandardAttributes(
                fullname=_cognito.StandardAttribute(required=True, mutable=True),
                email=_cognito.StandardAttribute(required=True, mutable=True),
                phone_number=_cognito.StandardAttribute(required=False, mutable=True),
            ),
            account_recovery=_cognito.AccountRecovery.EMAIL_ONLY,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # Cria um cliente do Cognito para o aplicativo móvel/web.
        # Sem um cliente a API não consegue conversar com o Cognito
        client_user_pool = _cognito.UserPoolClient(
            self,
            "test_client",
            user_pool=user_pool,
            auth_flows=_cognito.AuthFlow(user_password=True),
            supported_identity_providers=[
                _cognito.UserPoolClientIdentityProvider.COGNITO
            ],
        )

        # Define uma função Lambda que será disparada quando ocorrer uma chamada na API
        lambda_function = _lambda.Function(
            self,
            "lambda_test",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset(os.path.join("./", "functions")),
        )

        # Define o autorizador para a API usando o pool de usuários do Cognito
        auth = _apigateway.CognitoUserPoolsAuthorizer(
            self,
            "api_authorizer_cognito",
            cognito_user_pools=[user_pool],
        )

        # Cria a API RESTful integrada com a função Lambda e o autorizador do Cognito
        api = _apigateway.RestApi(
            self,
            "api_auth_test",
            minimum_compression_size=1,
        )
        api_v1 = api.root.add_resource("v1")
        api_v1.add_resource("hello").add_method(
            "GET",
            integration=_apigateway.LambdaIntegration(lambda_function),
            authorizer=auth,
        )

        # Para imprimir os ids do cliente e do pool de usuário
        # E a url da API em formato JSON
        # use o comando CLI `cdk deploy --outputs-file ./cdk-outputs.json`
        cdk.CfnOutput(self, "user_pool_id", value=user_pool.user_pool_id)
        cdk.CfnOutput(
            self, "client_user_pool_id", value=client_user_pool.user_pool_client_id
        )
        cdk.CfnOutput(self, "api_gateway_url", value=api.url_for_path("/hello"))
