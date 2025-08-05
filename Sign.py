import hashlib
import hmac
import datetime
from urllib.parse import urlencode

def hash_sha256(data):
    """Generate SHA256 hash of the input data"""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def get_x_date():
    """Get current UTC time in the required format"""
    t = datetime.datetime.utcnow()
    return t.strftime('%Y%m%dT%H%M%SZ')

def sign(key, msg):
    """HMAC-SHA256 signing function"""
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def get_signature_key(key, date_stamp, region_name, service_name):
    """Generate signing key for AWS-style signature"""
    k_date = sign(key.encode('utf-8'), date_stamp)
    k_region = sign(k_date, region_name)
    k_service = sign(k_region, service_name)
    k_signing = sign(k_service, 'request')
    return k_signing

def get_authorization(method, headers, query, service, region, ak, sk):
    """Generate authorization header for API request"""
    # Extract required values
    host = headers.get('Host', '')
    x_date = headers.get('X-Date', '')
    x_content_sha256 = headers.get('X-Content-Sha256', '')
    content_type = headers.get('Content-Type', 'application/json')
    
    # Parse date for credential scope
    t = datetime.datetime.strptime(x_date, '%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d')
    
    # Build canonical request
    canonical_uri = '/'
    canonical_querystring = urlencode(sorted(query.items()))
    signed_headers = 'content-type;host;x-content-sha256;x-date'
    
    canonical_headers = (
        f'content-type:{content_type}\n'
        f'host:{host}\n'
        f'x-content-sha256:{x_content_sha256}\n'
        f'x-date:{x_date}\n'
    )
    
    canonical_request = (
        f'{method}\n'
        f'{canonical_uri}\n'
        f'{canonical_querystring}\n'
        f'{canonical_headers}\n'
        f'{signed_headers}\n'
        f'{x_content_sha256}'
    )
    
    # Create string to sign
    algorithm = 'HMAC-SHA256'
    credential_scope = f'{date_stamp}/{region}/{service}/request'
    string_to_sign = (
        f'{algorithm}\n'
        f'{x_date}\n'
        f'{credential_scope}\n'
        f'{hash_sha256(canonical_request)}'
    )
    
    # Generate signature
    signing_key = get_signature_key(sk, date_stamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    
    # Build authorization header
    authorization_header = (
        f'{algorithm} '
        f'Credential={ak}/{credential_scope}, '
        f'SignedHeaders={signed_headers}, '
        f'Signature={signature}'
    )
    
    return authorization_header

def get_url(host, path, action, version):
    """Generate the full URL for the API request"""
    return f'https://{host}{path}?Action={action}&Version={version}'