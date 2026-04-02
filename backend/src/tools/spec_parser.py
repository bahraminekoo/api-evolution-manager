import json
from typing import Dict, Any, List
from pathlib import Path
from ..models.api_spec import (
    APISpec, Endpoint, Parameter, Schema, HTTPMethod, ParameterLocation
)


class SpecParser:
    """Parser for OpenAPI 3.0 specifications"""
    
    @staticmethod
    def parse_openapi_spec(spec_data: Dict[str, Any]) -> APISpec:
        """Parse OpenAPI 3.0 spec into APISpec model"""
        info = spec_data.get("info", {})
        version = info.get("version", "unknown")
        title = info.get("title", "Untitled API")
        description = info.get("description")
        
        base_url = None
        if "servers" in spec_data and spec_data["servers"]:
            base_url = spec_data["servers"][0].get("url")
        
        endpoints = []
        paths = spec_data.get("paths", {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.upper() not in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
                    continue
                
                endpoint = SpecParser._parse_endpoint(path, method.upper(), operation)
                endpoints.append(endpoint)
        
        return APISpec(
            version=version,
            title=title,
            description=description,
            base_url=base_url,
            endpoints=endpoints,
            raw_spec=spec_data
        )
    
    @staticmethod
    def _parse_endpoint(path: str, method: str, operation: Dict[str, Any]) -> Endpoint:
        """Parse a single endpoint operation"""
        parameters = SpecParser._parse_parameters(operation.get("parameters", []))
        request_body = SpecParser._parse_request_body(operation.get("requestBody"))
        responses = SpecParser._parse_responses(operation.get("responses", {}))
        
        return Endpoint(
            path=path,
            method=HTTPMethod(method),
            summary=operation.get("summary"),
            description=operation.get("description"),
            parameters=parameters,
            request_body=request_body,
            responses=responses,
            deprecated=operation.get("deprecated", False),
            tags=operation.get("tags", [])
        )
    
    @staticmethod
    def _parse_parameters(params: List[Dict[str, Any]]) -> List[Parameter]:
        """Parse parameters from OpenAPI spec"""
        result = []
        for param in params:
            schema = param.get("schema", {})
            param_type = schema.get("type", "string")
            
            result.append(Parameter(
                name=param.get("name", ""),
                location=ParameterLocation(param.get("in", "query")),
                required=param.get("required", False),
                type=param_type,
                description=param.get("description")
            ))
        return result
    
    @staticmethod
    def _parse_request_body(request_body: Dict[str, Any]) -> Schema:
        """Parse request body schema"""
        if not request_body:
            return None
        
        content = request_body.get("content", {})
        json_content = content.get("application/json", {})
        schema = json_content.get("schema", {})
        
        if not schema:
            return None
        
        return Schema(
            type=schema.get("type", "object"),
            properties=schema.get("properties"),
            required=schema.get("required"),
            description=schema.get("description")
        )
    
    @staticmethod
    def _parse_responses(responses: Dict[str, Any]) -> Dict[str, Schema]:
        """Parse response schemas"""
        result = {}
        for status_code, response in responses.items():
            content = response.get("content", {})
            json_content = content.get("application/json", {})
            schema = json_content.get("schema", {})
            
            if schema:
                result[status_code] = Schema(
                    type=schema.get("type", "object"),
                    properties=schema.get("properties"),
                    required=schema.get("required"),
                    description=response.get("description")
                )
        return result
    
    @staticmethod
    def load_from_file(file_path: str) -> APISpec:
        """Load and parse OpenAPI spec from file"""
        path = Path(file_path)
        with open(path, 'r') as f:
            spec_data = json.load(f)
        return SpecParser.parse_openapi_spec(spec_data)
