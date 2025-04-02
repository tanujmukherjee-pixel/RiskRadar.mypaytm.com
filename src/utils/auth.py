"""
Google OAuth2 utilities for generating tokens for service accounts.

This module provides functionality for generating OAuth tokens
using a service account without domain-wide delegation.
"""
import os
from typing import Dict, List, Optional, Any
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from ..constants.auth import DEFAULT_SERVICE_ACCOUNT_FILE, GOOGLE_SCOPES, DEFAULT_USER_EMAIL
import requests
import warnings

def generate_token_for_user_email(
    user_email: Optional[str] = None,
    service_account_file: Optional[str] = None,
    scopes: Optional[List[str]] = None,
    lifetime_seconds: int = 3600,
    disable_ssl_verification: bool = False,
) -> Dict[str, Any]:
    """
    Generate a Google OAuth token for a service account.
    
    This function uses a service account directly without domain-wide delegation.
    
    Prerequisites:
    1. A service account with appropriate permissions
    
    Args:
        user_email: Not used, kept for backward compatibility
        service_account_file: Path to the service account JSON key file (optional)
        scopes: List of OAuth scopes to request (optional)
        lifetime_seconds: Lifetime of the token in seconds (default: 1 hour)
        disable_ssl_verification: Whether to disable SSL certificate verification (default: False)
        
    Returns:
        Dictionary containing the access token and related information
    """

    # Use provided service account file or default from environment
    service_account_file = service_account_file or DEFAULT_SERVICE_ACCOUNT_FILE
        
    if not service_account_file or not os.path.exists(service_account_file):
        raise FileNotFoundError(f"Service account file not found: {service_account_file}")
    
    # Use provided scopes or default from environment
    used_scopes = scopes or GOOGLE_SCOPES
    
    try:
        # Load credentials from the service account file
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=used_scopes
        )
        
        # If the credentials can be refreshed, ensure it's valid
        if hasattr(credentials, 'refresh'):
            if disable_ssl_verification:
                # Warning about security implications
                warnings.warn(
                    "SSL verification is disabled. This is insecure and should only be used "
                    "in development environments."
                )
                
                # Create a custom session with SSL verification disabled
                session = requests.Session()
                session.verify = False
                
                # Disable urllib3 warnings about insecure requests
                requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
                
                # Use the custom session for the request
                request = Request(session=session)
                credentials.refresh(request)
            else:
                # Use default request with SSL verification
                credentials.refresh(Request())
        
        # Get the access token info
        token_info = {
            "access_token": credentials.token,
            "expires_in": lifetime_seconds,
            "token_type": "Bearer",
            "scope": " ".join(credentials.scopes),
            "email": credentials.service_account_email,
            "ssl_verification": not disable_ssl_verification,
        }
        
        # Add expiry timestamp if available
        if hasattr(credentials, 'expiry'):
            token_info["expires_at"] = credentials.expiry.isoformat()
        
        print(f"Successfully generated token for service account: {credentials.service_account_email}")
        return token_info
        
    except Exception as e:
        service_account_email = "service account"
        if hasattr(credentials, 'service_account_email'):
            service_account_email = credentials.service_account_email
        
        print(f"Error generating token for {service_account_email}: {str(e)}")
        raise ValueError(f"Failed to generate token for {service_account_email}: {str(e)}")
