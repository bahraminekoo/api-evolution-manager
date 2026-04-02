from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum


class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class ParameterLocation(str, Enum):
    QUERY = "query"
    PATH = "path"
    HEADER = "header"
    COOKIE = "cookie"


class Parameter(BaseModel):
    name: str
    location: ParameterLocation
    required: bool = False
    type: str
    description: Optional[str] = None


class Schema(BaseModel):
    type: str
    properties: Optional[Dict[str, Any]] = None
    required: Optional[List[str]] = None
    description: Optional[str] = None


class Endpoint(BaseModel):
    path: str
    method: HTTPMethod
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: List[Parameter] = Field(default_factory=list)
    request_body: Optional[Schema] = None
    responses: Dict[str, Schema] = Field(default_factory=dict)
    deprecated: bool = False
    tags: List[str] = Field(default_factory=list)


class APISpec(BaseModel):
    version: str
    title: str
    description: Optional[str] = None
    base_url: Optional[str] = None
    endpoints: List[Endpoint] = Field(default_factory=list)
    raw_spec: Optional[Dict[str, Any]] = None
    
    def get_endpoint_key(self, endpoint: Endpoint) -> str:
        return f"{endpoint.method.value} {endpoint.path}"
    
    def find_endpoint(self, path: str, method: HTTPMethod) -> Optional[Endpoint]:
        for endpoint in self.endpoints:
            if endpoint.path == path and endpoint.method == method:
                return endpoint
        return None
