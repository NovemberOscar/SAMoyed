from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from typing_extensions import Literal

VT = TypeVar("VT")
Mapping = Dict[str, VT]
MultiValueMapping = Dict[str, List[VT]]


@dataclass(frozen=True)
class APIGatewayProxyEvent:
    """
    https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    resource: str  # Resource path
    path: str  # Path parameter
    http_method: Literal["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]  # Incoming request's method name
    headers: Mapping[Union[bool, int, float, str]]  # {String containing incoming request headers}
    multi_value_headers: MultiValueMapping[
        Union[bool, int, float, str]
    ]  # {List of strings containing incoming request headers}
    query_string_parameters: Mapping[str]  # {query string parameters }
    multi_value_query_string_parameters: Optional[MultiValueMapping[str]]  # {List of query string parameters}
    path_parameters: Optional[Mapping[str]]  # {path parameters}
    stage_variables: Optional[Mapping[str]]  # {Applicable stage variables}
    request_context: Mapping[Any]  # {Request context, including authorizer-returned key-value pairs} TODO: Objectify
    body: Optional[str]  # A JSON string of the request payload.
    is_base64_encoded: bool  # A boolean flag to indicate if the applicable request payload is Base64-encode


class APIGatewayProxyBaseException(Exception):
    status_code: int = 500
    body: str = ""
    headers: Dict[str, Union[bool, int, float, str]] = {}
    multi_value_headers: Dict[str, List[Union[bool, int, float, str]]] = {}
    is_base64_encoded: bool = False

    def __init__(
        self,
        status_code: int = None,
        body: str = None,
        *,
        is_base64_encoded: bool = None,
        headers: Mapping[str] = None,
        multi_value_headers: MultiValueMapping[Union[bool, int, float, str]] = None
    ):
        self.status_code = self.status_code if status_code is None else status_code
        self.body = self.body if body is None else body
        self.is_base64_encoded = self.is_base64_encoded if is_base64_encoded is None else is_base64_encoded
        self.headers = self.headers if headers is None else headers
        self.multi_value_headers = self.multi_value_headers if multi_value_headers is None else multi_value_headers


@dataclass
class APIGatewayProxyResult:
    """
    https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    status_code: int
    body: str
    headers: Mapping[Union[bool, int, float, str]] = field(default_factory=dict)
    multi_value_headers: MultiValueMapping[Union[bool, int, float, str]] = field(default_factory=dict)
    is_base64_encoded: bool = False

    @staticmethod
    def from_exception(exc: APIGatewayProxyBaseException) -> "APIGatewayProxyResult":
        return APIGatewayProxyResult(
            status_code=exc.status_code,
            body=exc.body,
            headers=exc.headers,
            multi_value_headers=exc.multi_value_headers,
            is_base64_encoded=exc.is_base64_encoded,
        )


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
            is_base64_encoded=event["isBase64Encoded"],
        )

        try:
            return fn(rest_api_event, context)
        except APIGatewayProxyBaseException as e:
            return APIGatewayProxyResult.from_exception(e)

    return wrapper
