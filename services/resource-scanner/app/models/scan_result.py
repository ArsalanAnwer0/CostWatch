from dataclasses import dataclass
from typing import Dict, Any, List
from datetime import datetime

@dataclass
class ScanResult:
    """Result of a resource scan operation."""
    scan_id: str
    scan_type: str
    timestamp: datetime
    region: str
    resources: List[Dict[str, Any]]
    optimization_opportunities: List[Dict[str, Any]]
    total_resources: int
    estimated_monthly_cost: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert scan result to dictionary."""
        return {
            "scan_id": self.scan_id,
            "scan_type": self.scan_type,
            "timestamp": self.timestamp.isoformat(),
            "region": self.region,
            "resources": self.resources,
            "optimization_opportunities": self.optimization_opportunities,
            "total_resources": self.total_resources,
            "estimated_monthly_cost": self.estimated_monthly_cost,
            "summary": {
                "total_resources": self.total_resources,
                "total_potential_savings": sum(
                    opp.get("potential_savings", 0) 
                    for opp in self.optimization_opportunities
                ),
                "high_priority_opportunities": len([
                    opp for opp in self.optimization_opportunities 
                    if opp.get("priority") == "high"
                ])
            }
        }

@dataclass
class ComprehensiveScanResult:
    """Result of a comprehensive multi-service scan."""
    scan_id: str
    timestamp: datetime
    regions: List[str]
    service_results: Dict[str, ScanResult]
    overall_summary: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert comprehensive scan result to dictionary."""
        return {
            "scan_id": self.scan_id,
            "timestamp": self.timestamp.isoformat(),
            "regions": self.regions,
            "services": {
                service: result.to_dict() 
                for service, result in self.service_results.items()
            },
            "overall_summary": self.overall_summary
        }