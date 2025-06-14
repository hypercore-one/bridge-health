"""Status service for managing orchestrator data and updates"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from config.settings import Config
from app.services.orchestrator_client import OrchestratorClient


class StatusService:
    """Service class for managing orchestrator status data."""
    
    def __init__(self):
        self.client = OrchestratorClient(
            timeout=Config.ORCHESTRATOR_TIMEOUT,
            max_workers=Config.MAX_CONCURRENT_REQUESTS
        )
        self.status_file = os.path.join('data', Config.STATUS_FILE)
        self.orchestrator_ips = Config.get_orchestrator_ips()
    
    def load_cached_status(self) -> Optional[Dict]:
        """Load status from JSON file if it exists."""
        try:
            with open(self.status_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError as e:
            from app.main import get_logger
            logger = get_logger()
            logger.error(f"Error decoding status file: {e}")
            return None
    
    def update_status(self) -> Dict:
        """Update the status of all orchestrators and save to JSON file."""
        from app.main import get_logger
        logger = get_logger()
        
        logger.info("Starting orchestrator status update cycle...")
        
        # Query all orchestrators concurrently
        results, summary = self.client.query_all_orchestrators(self.orchestrator_ips)
        
        # Prepare the full status data
        status_data = {
            'timestamp': summary['timestamp'],
            'bridge_status': summary['bridge_status'],
            'online_count': summary['online_count'],
            'total_count': summary['total_count'],
            'query_time_seconds': summary['query_time_seconds'],
            'orchestrators': results
        }
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.status_file), exist_ok=True)
        
        # Save to file
        with open(self.status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
        
        logger.info(f"Orchestrator status update complete. Queried {summary['total_count']} orchestrators in {summary['query_time_seconds']}s")
        return status_data
    
    def get_status(self) -> Optional[Dict]:
        """Get current status data, returning cached data if available."""
        return self.load_cached_status()
    
    def get_summary(self) -> Optional[Dict]:
        """Get status summary without individual orchestrator details."""
        data = self.load_cached_status()
        if not data:
            return None
        
        return {
            'timestamp': data.get('timestamp'),
            'bridge_status': data.get('bridge_status'),
            'online_count': data.get('online_count'),
            'total_count': data.get('total_count'),
            'query_time_seconds': data.get('query_time_seconds')
        }
    
    def get_pillars(self) -> Optional[Dict]:
        """Get comprehensive pillar data combining static info and current status."""
        from app.services.orchestrator_client import PILLAR_MAPPING
        
        data = self.load_cached_status()
        if not data:
            return None
        
        # Create a lookup dictionary for current status
        current_status = {orch['ip']: orch for orch in data.get('orchestrators', [])}
        
        # Combine static pillar data with current status
        pillars = []
        for ip, static_info in PILLAR_MAPPING.items():
            current = current_status.get(ip, {})
            
            pillar_data = {
                # Static information
                'ip': ip,
                'pillar_name': static_info['name'],
                'pillar_url': self.client.format_pillar_name(static_info['name']),
                'pubkey': static_info['pubkey'],
                'zenonhub_url': f"https://zenonhub.io/pillar/{self.client.format_pillar_name(static_info['name'])}",
                
                # Current status (from live data or defaults)
                'status': current.get('status', 'unknown'),
                'producer_address': current.get('producer_address', 'Unknown'),
                'state': current.get('state', 'Unknown'),
                'state_num': current.get('state_num'),
                'network_stats': current.get('network_stats', {
                    'bnb': {'wraps': 0, 'unwraps': 0},
                    'eth': {'wraps': 0, 'unwraps': 0},
                    'supernova': {'wraps': 0, 'unwraps': 0}
                }),
                'error': current.get('error'),
                'last_checked': current.get('last_checked'),
                
                # Validation info
                'api_pillar_name': current.get('api_pillar_name'),
                'name_mismatch': current.get('name_mismatch', False),
                
                # Producer address links
                'producer_explorer_url': f"https://zenonhub.io/explorer/account/{current.get('producer_address')}" if current.get('producer_address') and current.get('producer_address') != 'Unknown' else None
            }
            
            pillars.append(pillar_data)
        
        # Sort by pillar name
        pillars.sort(key=lambda x: x['pillar_name'].lower())
        
        return {
            'timestamp': data.get('timestamp'),
            'total_pillars': len(pillars),
            'online_count': sum(1 for p in pillars if p['status'] == 'online'),
            'offline_count': sum(1 for p in pillars if p['status'] == 'offline'),
            'unknown_count': sum(1 for p in pillars if p['status'] == 'unknown'),
            'pillars': pillars
        }
    
    def close(self):
        """Close the orchestrator client."""
        self.client.close()