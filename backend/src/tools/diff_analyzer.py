from typing import List, Dict, Set, Tuple
from ..models.api_spec import APISpec, Endpoint, Parameter, HTTPMethod
from ..models.analysis_result import BreakingChange, ChangeType, ImpactLevel
from ..models.usage_data import UsageData


class DiffAnalyzer:
    """Analyzes differences between two API specifications"""
    
    @staticmethod
    def analyze_changes(
        old_spec: APISpec,
        new_spec: APISpec,
        usage_data: UsageData = None
    ) -> List[BreakingChange]:
        """Analyze breaking changes between two API versions"""
        changes = []
        
        old_endpoints = {old_spec.get_endpoint_key(ep): ep for ep in old_spec.endpoints}
        new_endpoints = {new_spec.get_endpoint_key(ep): ep for ep in new_spec.endpoints}
        
        old_keys = set(old_endpoints.keys())
        new_keys = set(new_endpoints.keys())
        
        # Detect removed endpoints
        removed_keys = old_keys - new_keys
        for key in removed_keys:
            endpoint = old_endpoints[key]
            usage = usage_data.get_usage_for_endpoint(key) if usage_data else None
            
            impact_level = DiffAnalyzer._calculate_impact_level(usage)
            
            changes.append(BreakingChange(
                change_type=ChangeType.ENDPOINT_REMOVED,
                endpoint_key=key,
                description=f"Endpoint {key} has been removed",
                impact_level=impact_level,
                affected_clients=usage.clients if usage else [],
                usage_count=usage.total_calls if usage else 0,
                details={"endpoint": endpoint.path, "method": endpoint.method.value}
            ))
        
        # Detect added endpoints
        added_keys = new_keys - old_keys
        for key in added_keys:
            endpoint = new_endpoints[key]
            changes.append(BreakingChange(
                change_type=ChangeType.ENDPOINT_ADDED,
                endpoint_key=key,
                description=f"New endpoint {key} has been added",
                impact_level=ImpactLevel.NONE,
                affected_clients=[],
                usage_count=0,
                details={"endpoint": endpoint.path, "method": endpoint.method.value}
            ))
        
        # Analyze changes in existing endpoints
        common_keys = old_keys & new_keys
        for key in common_keys:
            old_endpoint = old_endpoints[key]
            new_endpoint = new_endpoints[key]
            usage = usage_data.get_usage_for_endpoint(key) if usage_data else None
            
            endpoint_changes = DiffAnalyzer._analyze_endpoint_changes(
                old_endpoint, new_endpoint, usage
            )
            changes.extend(endpoint_changes)
        
        return changes
    
    @staticmethod
    def _analyze_endpoint_changes(
        old_endpoint: Endpoint,
        new_endpoint: Endpoint,
        usage
    ) -> List[BreakingChange]:
        """Analyze changes within a single endpoint"""
        changes = []
        endpoint_key = f"{old_endpoint.method.value} {old_endpoint.path}"
        
        # Check if deprecated
        if new_endpoint.deprecated and not old_endpoint.deprecated:
            impact_level = DiffAnalyzer._calculate_impact_level(usage)
            changes.append(BreakingChange(
                change_type=ChangeType.ENDPOINT_DEPRECATED,
                endpoint_key=endpoint_key,
                description=f"Endpoint {endpoint_key} is now deprecated",
                impact_level=impact_level,
                affected_clients=usage.clients if usage else [],
                usage_count=usage.total_calls if usage else 0
            ))
        
        # Analyze parameter changes
        param_changes = DiffAnalyzer._analyze_parameter_changes(
            old_endpoint, new_endpoint, usage
        )
        changes.extend(param_changes)
        
        # Analyze request body changes
        if old_endpoint.request_body and new_endpoint.request_body:
            body_changes = DiffAnalyzer._analyze_schema_changes(
                old_endpoint.request_body,
                new_endpoint.request_body,
                endpoint_key,
                usage,
                is_request=True
            )
            changes.extend(body_changes)
        
        return changes
    
    @staticmethod
    def _analyze_parameter_changes(
        old_endpoint: Endpoint,
        new_endpoint: Endpoint,
        usage
    ) -> List[BreakingChange]:
        """Analyze parameter changes in an endpoint"""
        changes = []
        endpoint_key = f"{old_endpoint.method.value} {old_endpoint.path}"
        
        old_params = {p.name: p for p in old_endpoint.parameters}
        new_params = {p.name: p for p in new_endpoint.parameters}
        
        # Removed parameters
        removed_params = set(old_params.keys()) - set(new_params.keys())
        for param_name in removed_params:
            impact_level = DiffAnalyzer._calculate_impact_level(usage)
            changes.append(BreakingChange(
                change_type=ChangeType.PARAMETER_REMOVED,
                endpoint_key=endpoint_key,
                description=f"Parameter '{param_name}' removed from {endpoint_key}",
                impact_level=impact_level,
                affected_clients=usage.clients if usage else [],
                usage_count=usage.total_calls if usage else 0,
                details={"parameter": param_name, "location": old_params[param_name].location.value}
            ))
        
        # Added required parameters
        added_params = set(new_params.keys()) - set(old_params.keys())
        for param_name in added_params:
            param = new_params[param_name]
            if param.required:
                impact_level = DiffAnalyzer._calculate_impact_level(usage)
                changes.append(BreakingChange(
                    change_type=ChangeType.PARAMETER_ADDED,
                    endpoint_key=endpoint_key,
                    description=f"New required parameter '{param_name}' added to {endpoint_key}",
                    impact_level=impact_level,
                    affected_clients=usage.clients if usage else [],
                    usage_count=usage.total_calls if usage else 0,
                    details={"parameter": param_name, "type": param.type}
                ))
        
        # Changed parameters
        common_params = set(old_params.keys()) & set(new_params.keys())
        for param_name in common_params:
            old_param = old_params[param_name]
            new_param = new_params[param_name]
            
            # Type changed
            if old_param.type != new_param.type:
                impact_level = DiffAnalyzer._calculate_impact_level(usage)
                changes.append(BreakingChange(
                    change_type=ChangeType.PARAMETER_TYPE_CHANGED,
                    endpoint_key=endpoint_key,
                    description=f"Parameter '{param_name}' type changed from {old_param.type} to {new_param.type}",
                    impact_level=impact_level,
                    affected_clients=usage.clients if usage else [],
                    usage_count=usage.total_calls if usage else 0,
                    details={"parameter": param_name, "old_type": old_param.type, "new_type": new_param.type}
                ))
            
            # Required status changed
            if not old_param.required and new_param.required:
                impact_level = DiffAnalyzer._calculate_impact_level(usage)
                changes.append(BreakingChange(
                    change_type=ChangeType.PARAMETER_REQUIRED_CHANGED,
                    endpoint_key=endpoint_key,
                    description=f"Parameter '{param_name}' is now required in {endpoint_key}",
                    impact_level=impact_level,
                    affected_clients=usage.clients if usage else [],
                    usage_count=usage.total_calls if usage else 0,
                    details={"parameter": param_name}
                ))
        
        return changes
    
    @staticmethod
    def _analyze_schema_changes(
        old_schema,
        new_schema,
        endpoint_key: str,
        usage,
        is_request: bool = True
    ) -> List[BreakingChange]:
        """Analyze schema changes in request/response bodies"""
        changes = []
        
        if not old_schema or not new_schema:
            return changes
        
        old_required = set(old_schema.required or [])
        new_required = set(new_schema.required or [])
        
        # New required fields
        added_required = new_required - old_required
        if added_required:
            impact_level = DiffAnalyzer._calculate_impact_level(usage)
            schema_type = "request" if is_request else "response"
            changes.append(BreakingChange(
                change_type=ChangeType.REQUEST_SCHEMA_CHANGED if is_request else ChangeType.RESPONSE_SCHEMA_CHANGED,
                endpoint_key=endpoint_key,
                description=f"New required fields in {schema_type} body: {', '.join(added_required)}",
                impact_level=impact_level,
                affected_clients=usage.clients if usage else [],
                usage_count=usage.total_calls if usage else 0,
                details={"added_required_fields": list(added_required)}
            ))
        
        return changes
    
    @staticmethod
    def _calculate_impact_level(usage) -> ImpactLevel:
        """Calculate impact level based on usage data"""
        if not usage:
            return ImpactLevel.MEDIUM
        
        total_calls = usage.total_calls
        num_clients = len(usage.clients)
        
        if total_calls >= 5000 or num_clients >= 3:
            return ImpactLevel.CRITICAL
        elif total_calls >= 1000 or num_clients >= 2:
            return ImpactLevel.HIGH
        elif total_calls >= 100:
            return ImpactLevel.MEDIUM
        else:
            return ImpactLevel.LOW
