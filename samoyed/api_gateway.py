from dataclasses import dataclass, field
from functools import wraps
from typing import Literal, Optional, Union, Dict, List, Callable


@dataclass(frozen=True)
class APIGatewayProxyEvent:
    """
    https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    resource: str  # Resource path
    path: str  # Path parameter
    http_method: Literal["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]  # Incoming request's method name
    headers: Dict[str, str]  # {String containing incoming request headers}
    multi_value_headers: Dict[str, List[str]]  # {List of strings containing incoming request headers}
    query_string_parameters: Dict[str, str]  # {query string parameters }
    multi_value_query_string_parameters: Optional[Dict[str, List[str]]]  # {List of query string parameters}
    path_parameters: Optional[Dict[str, str]]  # {path parameters}
    stage_variables: Optional[Dict[str, str]]  # {Applicable stage variables}
    request_context: Dict  # {Request context, including authorizer-returned key-value pairs} TODO: Objectify
    body: Optional[str]  # A JSON string of the request payload.
    is_base64_encoded: bool  # A boolean flag to indicate if the applicable request payload is Base64-encode


@dataclass
class APIGatewayProxyResult:
    """
    https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    status_code: int
    body: str
    headers: Dict[str, Union[bool, int, float, str]] = field(default={})
    multi_value_headers: Dict[str, List[Union[bool, int, float, str]]] = field(default={})
    is_base64_encoded: bool = False


RestApiHandler = Callable[[APIGatewayProxyEvent, dict], APIGatewayProxyResult]


def rest_api_handler(fn: RestApiHandler) -> Callable[[dict, dict], APIGatewayProxyResult]:
    @wraps
    def wrapper(event: dict, context: dict) -> APIGatewayProxyResult:
        rest_api_event = APIGatewayProxyEvent(
            resource=event["resource"],
            path=event["path"],
            http_method=event["httpMethod"],
            headers=event["headers"],
            multi_value_headers=event["multiValueHeaders"],
            query_string_parameters=event["queryStringParameters"],
            multi_value_query_string_parameters=event["multiValueQueryStringParameters"],
            path_parameters=event["pathParameters"],
            stage_variables=event["stageVariables"],
            request_context=event["requestContext"],
            body=event["body"],
            is_base64_encoded=event["isBase64Encoded"]
        )

        return fn(rest_api_event, context)

    return wrapper
