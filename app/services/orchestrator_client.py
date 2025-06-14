"""
Shared orchestrator client module for querying orchestrator nodes.
This module provides a unified interface for interacting with orchestrators.
"""
import json
import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logger = logging.getLogger(__name__)

# State mapping
STATE_MAP = {
    0: "LiveState",
    1: "KeyGenState",
    2: "HaltedState",
    3: "EmergencyState",
    4: "ReSignState"
}

# Constants
DEFAULT_TIMEOUT = 5
DEFAULT_PORT = 55000
ONLINE_STATES = [0, 1]  # States that indicate orchestrator is online
MIN_ONLINE_FOR_BRIDGE = 16  # Minimum orchestrators online for bridge to be considered online

# Static pillar mapping - IP to pillar name and pubkey
PILLAR_MAPPING = {
    "5.161.213.40": {"name": "Anvil", "pubkey": "Cdq18YwdIT21VcOOl3uczUl/W+RGCqi9CgFIf4CLr8g="},
    "51.222.12.113": {"name": "Zeno", "pubkey": "HxX/6MM7jcjqHAyESWHvLVN3KLWjt6GKgRAgTY9CUqc="},
    "172.245.233.178": {"name": "0x3639.com", "pubkey": "LbNpGLiwr9ZVAx5Rzbq/dMI7ijkSZf6nMI7Zlof8j0k="},
    "161.97.167.129": {"name": "12N11", "pubkey": "NbxBOar2Q8pPYa2ABIap2aOCzpZO2MZuXwoLNrk3bdc="},
    "23.95.79.26": {"name": "NoMLabz.org", "pubkey": "WzKhvWcekYTdRyAGrB4bW3fbj/Zvk1aSQNUkxVst700="},
    "159.69.183.154": {"name": "ZenonORG3", "pubkey": "bLgOQXP9qEDm0snI/NFAO1kVzE17YHdzHxMmoPQawQU="},
    "49.13.221.207": {"name": "ZenonORG2", "pubkey": "dpJTNz+J+t+61CqNmqBCqN3jHhdiMbXqxAd6/eNlVmo="},
    "62.171.148.56": {"name": "StakeServe", "pubkey": "eP5mlLqa47bA5R79hh2ds/R5sOPa8nhWcDQN5w4BsEY="},
    "51.89.155.26": {"name": "ElderZ", "pubkey": "ePSgBL7qaYNU5OYpmqmPm1ayI6BNIt0XhH0v2Yh220g="},
    "51.222.12.145": {"name": "MoonBaZe", "pubkey": "fvGMCT2U5wAV9clv2LBpTMdSKHqcUiqI3NuglmWcZkk="},
    "34.125.216.244": {"name": "SultanOfStaking", "pubkey": "gwXonyuXWFRnz4lryObtUZKeOiq31Nh53GLRMDlha2M="},
    "93.127.202.74": {"name": "Nexus", "pubkey": "h1vpPABWPgtu0BE886LqRESoQ/WkokPQNO6JiyoVEsk="},
    "23.95.72.54": {"name": "DeeZNNutz.com", "pubkey": "i0MkFAj+f4FipCHu/L4Ee3g23pkRR7eoOPe1VRH2S4Y="},
    "51.79.147.224": {"name": "tapwoot", "pubkey": "iyyltT42L6pZgS0B7RQOSl5p26FsMSlt4V76ZI9+kcU="},
    "51.83.187.145": {"name": "WotGasFees", "pubkey": "k0VjkxdFXz3tgEszXcAvXInYUDRMzVPcUhyaVGREriI="},
    "109.104.152.53": {"name": "Stark", "pubkey": "nxPtMkX6BJn/NSOV9qTV/T4yXQ3b0QTPaySla38L8go="},
    "89.145.164.212": {"name": "Megalith", "pubkey": "p+bD1q4OniBmikRX2UscBFXV/mnOz/ILAoH5Kd6hRNA="},
    "51.79.147.166": {"name": "Time", "pubkey": "t8el+WTyESTS4Lke/+5hQX8cjnnoqjYM9uVBYJyxfUo="},
    "178.18.251.111": {"name": "Mariposa01", "pubkey": "vm37WOlgoQc2yCgVX2IUj5xCfOgObj5Za7xi9ZRpGq8="},
    "188.245.58.57": {"name": "ZenonORG", "pubkey": "wePlF1o2eLtxFvWgslazIhjGhlRI4lVQOduUr3v37W4="}
}


class OrchestratorClient:
    """Client for interacting with orchestrator nodes."""
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT, max_workers: int = 10):
        """
        Initialize the orchestrator client.
        
        Args:
            timeout: Request timeout in seconds
            max_workers: Maximum number of concurrent threads
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    @staticmethod
    def extract_ip(addr: str) -> str:
        """Extract IP address from multiaddr format."""
        match = re.search(r'/ip4/(\d+\.\d+\.\d+\.\d+)', addr)
        if match:
            return match.group(1)
        raise ValueError(f"Could not extract IP from address: {addr}")
    
    @staticmethod
    def format_pillar_name(name: str) -> str:
        """Format pillar name for URL by removing special characters and converting to lowercase."""
        return ''.join(c.lower() for c in name if c.isalnum())
    
    def _make_request(self, ip: str, method: str, params: List = None) -> Dict:
        """
        Make a JSON-RPC request to an orchestrator.
        
        Args:
            ip: IP address of the orchestrator
            method: RPC method to call
            params: Method parameters
            
        Returns:
            Response data dictionary
        """
        url = f"http://{ip}:{DEFAULT_PORT}"
        headers = {"Content-Type": "application/json"}
        payload = {"method": method, "params": params or []}
        
        response = self.session.post(
            url,
            json=payload,
            headers=headers,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def query_single_orchestrator(self, ip: str) -> Dict:
        """
        Query a single orchestrator for its status.
        
        Args:
            ip: IP address of the orchestrator
            
        Returns:
            Dictionary containing orchestrator status information
        """
        try:
            # Query identity
            identity_data = self._make_request(ip, "getIdentity")
            
            # Small delay to avoid overwhelming the orchestrator
            time.sleep(0.1)
            
            # Query status
            status_data = self._make_request(ip, "getStatus")
            
            # Check for errors
            if identity_data.get("error") or status_data.get("error"):
                error_msg = identity_data.get("error") or status_data.get("error")
                logger.error(f"RPC error for {ip}: {error_msg}")
                return self._create_error_response(ip, error_msg)
            
            # Process the data
            return self._process_orchestrator_data(ip, identity_data, status_data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error querying orchestrator at {ip}: {str(e)}")
            return self._create_error_response(ip, f"Network error: {str(e)}")
        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"Data parsing error for orchestrator at {ip}: {str(e)}")
            return self._create_error_response(ip, f"Invalid response format: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error querying orchestrator at {ip}: {str(e)}")
            return self._create_error_response(ip, f"Unexpected error: {str(e)}")
    
    def _process_orchestrator_data(self, ip: str, identity_data: Dict, status_data: Dict) -> Dict:
        """Process raw orchestrator data into standardized format."""
        api_pillar_name = identity_data["result"]["pillarName"]
        producer_address = identity_data["result"]["producer"]
        state_num = status_data["result"].get("state", None)
        state_name = STATE_MAP.get(state_num, "Unknown")
        status = "online" if state_num in ONLINE_STATES else "offline"
        
        # Get static pillar info
        static_pillar = PILLAR_MAPPING.get(ip, {})
        static_pillar_name = static_pillar.get("name", f"Unknown-{ip}")
        
        # Validate API response against static mapping
        name_mismatch = False
        error_msg = None
        if api_pillar_name != static_pillar_name:
            name_mismatch = True
            error_msg = f"Name mismatch: API returned '{api_pillar_name}', expected '{static_pillar_name}'"
            logger.warning(f"Pillar name mismatch for {ip}: API='{api_pillar_name}' vs Static='{static_pillar_name}'")
        
        # Process network statistics
        network_stats = self._process_network_stats(status_data)
        
        return {
            "ip": ip,
            "pillar_name": static_pillar_name,  # Always use static name
            "pillar_url": self.format_pillar_name(static_pillar_name),
            "producer_address": producer_address,
            "status": status,
            "state": f"{state_num} ({state_name})",
            "state_num": state_num,
            "network_stats": network_stats,
            "error": error_msg,  # Include name mismatch error if any
            "last_checked": datetime.now().isoformat(),
            "api_pillar_name": api_pillar_name,  # Keep API name for debugging
            "name_mismatch": name_mismatch
        }
    
    def _process_network_stats(self, status_data: Dict) -> Dict:
        """Extract network statistics from status data."""
        network_stats = {
            'bnb': {'wraps': 0, 'unwraps': 0},
            'eth': {'wraps': 0, 'unwraps': 0},
            'supernova': {'wraps': 0, 'unwraps': 0}
        }
        
        if "result" in status_data and "networks" in status_data["result"]:
            networks = status_data["result"]["networks"]
            
            network_mapping = {
                'BNB Chain': 'bnb',
                'Ethereum': 'eth',
                'Supernova': 'supernova'
            }
            
            for network_name, network_key in network_mapping.items():
                if network_name in networks:
                    network_data = networks[network_name]
                    network_stats[network_key]['wraps'] = network_data.get('wrapsToSign', 0)
                    network_stats[network_key]['unwraps'] = network_data.get('unwrapsToSign', 0)
        
        return network_stats
    
    def _create_error_response(self, ip: str, error: str) -> Dict:
        """Create a standardized error response for a failed orchestrator query."""
        # Get static pillar info even for offline orchestrators
        static_pillar = PILLAR_MAPPING.get(ip, {})
        static_pillar_name = static_pillar.get("name", f"Unknown-{ip}")
        
        return {
            "ip": ip,
            "pillar_name": static_pillar_name,  # Use static name
            "pillar_url": self.format_pillar_name(static_pillar_name),
            "producer_address": "Unknown",
            "status": "offline",
            "state": "Unknown",
            "state_num": None,
            "network_stats": {
                'bnb': {'wraps': 0, 'unwraps': 0},
                'eth': {'wraps': 0, 'unwraps': 0},
                'supernova': {'wraps': 0, 'unwraps': 0}
            },
            "error": error,
            "last_checked": datetime.now().isoformat(),
            "api_pillar_name": None,  # No API response available
            "name_mismatch": False
        }
    
    def query_all_orchestrators(self, ip_addresses: List[str]) -> Tuple[List[Dict], Dict]:
        """
        Query all orchestrators concurrently.
        
        Args:
            ip_addresses: List of orchestrator IP addresses
            
        Returns:
            Tuple of (orchestrator_results, summary_stats)
        """
        results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_ip = {
                executor.submit(self.query_single_orchestrator, ip): ip 
                for ip in ip_addresses
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to query orchestrator {ip}: {e}")
                    results.append(self._create_error_response(ip, str(e)))
        
        # Sort results by pillar name
        results.sort(key=lambda x: x['pillar_name'].lower())
        
        # Calculate summary statistics
        elapsed_time = time.time() - start_time
        online_count = sum(1 for r in results if r['status'] == 'online')
        bridge_status = 'online' if online_count >= MIN_ONLINE_FOR_BRIDGE else 'offline'
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'bridge_status': bridge_status,
            'online_count': online_count,
            'total_count': len(results),
            'query_time_seconds': round(elapsed_time, 2)
        }
        
        return results, summary
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()