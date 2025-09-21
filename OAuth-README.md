# Carthooks Python SDK OAuth Support

The Carthooks Python SDK now supports OAuth 2.0 authentication with automatic token refresh capabilities.

## Features

- ✅ **Client Credentials Flow** - Machine-to-machine authentication
- ✅ **Client Credentials + User Token** - Server-side apps acting on behalf of users  
- ✅ **Authorization Code Flow** - Standard OAuth 2.0 for web applications
- ✅ **Automatic Token Refresh** - Seamless token renewal before expiration
- ✅ **Token Management** - Store and retrieve tokens with callbacks
- ✅ **Type Hints** - Full Python type hints for all OAuth operations
- ✅ **Context Manager** - Automatic resource cleanup with `with` statement

## Installation

```bash
pip install carthooks
```

## Supported Grant Types

### 1. Client Credentials (Machine-to-Machine)

For server-to-server communication without user context:

```python
from carthooks.sdk import Client, OAuthConfig

oauth_config = OAuthConfig(
    client_id="dvc-your-client-id",
    client_secret="dvs-your-client-secret",
    auto_refresh=True
)

client = Client(oauth_config=oauth_config)

try:
    # Initialize OAuth
    result = client.initialize_oauth()
    if not result.success:
        print(f"Failed to get token: {result.error}")
        exit(1)

    print(f"Access token: {result.data}")
    
    # Make API calls - tokens auto-refresh as needed
    items = client.getItems(app_id, collection_id, limit=10)
    if items.success:
        print(f"Items: {items.data}")

finally:
    client.close()
```

### 2. Client Credentials + User Token

For server-side applications acting on behalf of users:

```python
from carthooks.sdk import Client, OAuthConfig

oauth_config = OAuthConfig(
    client_id="dvc-your-client-id", 
    client_secret="dvs-your-client-secret",
    auto_refresh=True
)

client = Client(oauth_config=oauth_config)

try:
    # Use user access token from your frontend
    user_token = "user-access-token-from-frontend"
    result = client.initialize_oauth(user_token)

    if result.success:
        # This token represents the user and has their permissions
        user_info = client.get_current_user()
        if user_info.success:
            print(f"Acting as user: {user_info.data}")

finally:
    client.close()
```

### 3. Authorization Code Flow

For web applications with user authorization:

```python
from carthooks.sdk import Client, OAuthConfig, OAuthAuthorizeCodeRequest

oauth_config = OAuthConfig(
    client_id="dvc-your-client-id",
    client_secret="dvs-your-client-secret",
    auto_refresh=True
)

client = Client(oauth_config=oauth_config)

try:
    # Step 1: Get authorization URL (redirect user here)
    auth_request = OAuthAuthorizeCodeRequest(
        client_id="dvc-your-client-id",
        redirect_uri="https://your-app.com/oauth/callback",
        state="random-state-string",
        target_tenant_id=123  # For platform-level clients
    )

    auth_result = client.get_oauth_authorize_code(auth_request)
    if auth_result.success:
        redirect_url = auth_result.data.get('redirect_url')
        print(f"Redirect user to: {redirect_url}")

    # Step 2: Exchange code for tokens (in your callback handler)
    code = "authorization-code-from-callback"
    token_result = client.exchange_authorization_code(
        code, 
        "https://your-app.com/oauth/callback"
    )

    if token_result.success:
        # Store tokens and make API calls
        tokens = client.get_current_tokens()
        print(f"Access token: {tokens.access_token}")
        print(f"Refresh token: {tokens.refresh_token}")

finally:
    client.close()
```

## Token Management

### Automatic Refresh

Tokens are automatically refreshed 5 minutes before expiration:

```python
from carthooks.sdk import Client, OAuthConfig

def on_token_refresh(tokens):
    """Called whenever tokens are refreshed"""
    print(f"Token refreshed: {tokens.access_token}")
    # Save tokens to database/storage
    save_to_database(tokens.refresh_token)

oauth_config = OAuthConfig(
    client_id="dvc-your-client-id",
    client_secret="dvs-your-client-secret",
    auto_refresh=True,  # Default: True
    on_token_refresh=on_token_refresh
)

client = Client(oauth_config=oauth_config)

# All API calls will automatically refresh tokens as needed
result = client.getItems(app_id, collection_id, limit=20)
```

### Manual Refresh

You can also manually refresh tokens:

```python
# Refresh using stored refresh token
refresh_result = client.refresh_oauth_token("stored-refresh-token")

if refresh_result.success:
    print(f"New access token: {refresh_result.data}")

# Or refresh using configured refresh token
result = client.refresh_oauth_token()
```

### Token Storage

Store and retrieve tokens for persistence:

```python
from carthooks.sdk import Client, OAuthConfig, OAuthTokens

def save_tokens(tokens: OAuthTokens):
    """Save tokens to persistent storage"""
    # Save to database, file, etc.
    with open('tokens.txt', 'w') as f:
        f.write(f"{tokens.access_token}\n{tokens.refresh_token}")

def load_refresh_token():
    """Load refresh token from storage"""
    try:
        with open('tokens.txt', 'r') as f:
            lines = f.readlines()
            return lines[1].strip() if len(lines) > 1 else None
    except FileNotFoundError:
        return None

# Load existing refresh token
stored_refresh_token = load_refresh_token()

oauth_config = OAuthConfig(
    client_id="dvc-your-client-id",
    client_secret="dvs-your-client-secret",
    refresh_token=stored_refresh_token,
    auto_refresh=True,
    on_token_refresh=save_tokens
)

client = Client(oauth_config=oauth_config)

# Try to refresh on startup
if stored_refresh_token:
    client.refresh_oauth_token()

# Get current tokens for storage
current_tokens = client.get_current_tokens()
if current_tokens:
    save_tokens(current_tokens)
```

## Configuration Options

### OAuthConfig Class

```python
from carthooks.sdk import OAuthConfig

config = OAuthConfig(
    client_id="dvc-your-client-id",      # Your OAuth client ID
    client_secret="dvs-your-client-secret",  # Your OAuth client secret  
    refresh_token="stored-refresh-token",    # Stored refresh token (optional)
    auto_refresh=True,                       # Auto-refresh tokens (default: True)
    on_token_refresh=callback_function       # Token refresh callback (optional)
)
```

### Client Configuration

```python
from carthooks.sdk import Client, OAuthConfig

client = Client(
    oauth_config=oauth_config,           # OAuth configuration
    access_token="direct-token",         # Direct access token (alternative to OAuth)
    timeout=30.0,                        # Request timeout
    max_connections=100,                 # Connection pool size
    http2=True,                          # Enable HTTP/2
    dns_cache=True                       # Enable DNS caching
)
```

## Context Manager Support

Use the client as a context manager for automatic cleanup:

```python
from carthooks.sdk import Client, OAuthConfig

oauth_config = OAuthConfig(
    client_id="dvc-your-client-id",
    client_secret="dvs-your-client-secret",
    auto_refresh=True
)

# Automatic resource cleanup
with Client(oauth_config=oauth_config) as client:
    # Initialize OAuth
    result = client.initialize_oauth()
    if result.success:
        # Make API calls
        items = client.getItems(123, 456, limit=10)
        print(f"Retrieved {len(items.data)} items")

# Client is automatically closed here
```

## Error Handling

The SDK provides detailed error information:

```python
result = client.initialize_oauth()

if not result.success:
    print(f"OAuth failed: {result.error}")
    if result.trace_id:
        print(f"Trace ID: {result.trace_id}")

# Handle specific OAuth errors
refresh_result = client.refresh_oauth_token()
if not refresh_result.success:
    if "invalid_refresh_token" in refresh_result.error:
        # Refresh token expired, need to re-authorize
        redirect_to_authorization_flow()
```

## Token Expiration

- **Access Tokens**: 24 hours
- **Refresh Tokens**: 12 months
- **Auto-refresh**: Triggered 5 minutes before expiration

## Security Best Practices

1. **Store secrets securely**: Never expose client secrets in logs or client-side code
2. **Use HTTPS**: Always use secure connections for token exchange
3. **Rotate tokens**: Implement proper token rotation and storage
4. **Handle expiration**: Gracefully handle token expiration scenarios
5. **Scope limitation**: Request only necessary scopes for your application

## API Endpoints

The SDK automatically handles these OAuth endpoints:

- `POST /open/api/oauth/token` - Token exchange and refresh
- `POST /api/oauth/get-authorize-code` - Get authorization code  
- `GET /open/api/v1/me` - Get current user information

## Complete Example

```python
#!/usr/bin/env python3

from carthooks.sdk import Client, OAuthConfig, OAuthTokens
import sys

def save_tokens(tokens: OAuthTokens):
    """Save tokens to storage"""
    print(f"Saving tokens: {tokens.access_token}")
    # Implement your storage logic here

def main():
    # Create OAuth configuration
    oauth_config = OAuthConfig(
        client_id="dvc-your-client-id",
        client_secret="dvs-your-client-secret",
        auto_refresh=True,
        on_token_refresh=save_tokens
    )

    # Use context manager for automatic cleanup
    with Client(oauth_config=oauth_config, timeout=30.0) as client:
        # Initialize OAuth
        result = client.initialize_oauth()
        if not result.success:
            print(f"OAuth initialization failed: {result.error}")
            sys.exit(1)

        print("OAuth initialized successfully")

        # Get current user
        user_result = client.get_current_user()
        if user_result.success:
            print(f"Current user: {user_result.data}")

        # Get items with auto token refresh
        items_result = client.getItems(123, 456, limit=10)
        if items_result.success:
            print(f"Retrieved {len(items_result.data)} items")

        # Create new item
        new_item = {
            "title": "New Item",
            "status": "active"
        }

        create_result = client.createItem(123, 456, new_item)
        if create_result.success:
            print(f"Created item: {create_result.data}")

if __name__ == "__main__":
    main()
```

## Migration from Access Token

If you're currently using direct access tokens:

```python
# Old way
client = Client(access_token="your-access-token")

# New way with OAuth
oauth_config = OAuthConfig(
    client_id="dvc-your-client-id",
    client_secret="dvs-your-client-secret",
    auto_refresh=True
)

client = Client(oauth_config=oauth_config)
client.initialize_oauth()
```

The OAuth approach provides better security and automatic token management.

## Environment Variables

You can also configure OAuth using environment variables:

```bash
export CARTHOOKS_API_URL="https://your-instance.carthooks.com"
export CARTHOOKS_ACCESS_TOKEN="your-access-token"  # For legacy auth
export CARTHOOKS_TIMEOUT="30.0"
```

## Examples

See `examples/oauth_example.py` for complete working examples of all OAuth flows.

## Testing

```bash
# Run examples
python examples/oauth_example.py

# Run with specific example
python -c "from examples.oauth_example import client_credentials_example; client_credentials_example()"
```

## Type Hints

The SDK provides full type hints for better IDE support:

```python
from carthooks.sdk import Client, OAuthConfig, OAuthTokens, Result
from typing import Optional

def handle_tokens(tokens: Optional[OAuthTokens]) -> None:
    if tokens:
        print(f"Access token: {tokens.access_token}")

def make_api_call(client: Client) -> Result:
    return client.getItems(123, 456, limit=10)
```

## Async Support

For async/await support, consider using `httpx.AsyncClient` directly or wrapping the SDK methods in async functions:

```python
import asyncio
from carthooks.sdk import Client, OAuthConfig

async def async_api_call():
    oauth_config = OAuthConfig(
        client_id="dvc-your-client-id",
        client_secret="dvs-your-client-secret"
    )
    
    client = Client(oauth_config=oauth_config)
    
    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, client.initialize_oauth)
    
    if result.success:
        items = await loop.run_in_executor(None, client.getItems, 123, 456, 10)
        return items
    
    client.close()

# Usage
# result = asyncio.run(async_api_call())
```
