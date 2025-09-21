#!/usr/bin/env python3
"""
OAuth usage examples for Carthooks Python SDK
"""

import os
import sys
import time
from typing import Optional

# Add the parent directory to the path so we can import carthooks
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from carthooks.sdk import Client, OAuthConfig, OAuthTokens, OAuthAuthorizeCodeRequest

def save_tokens_to_storage(tokens: OAuthTokens) -> None:
    """Save tokens to storage (implement based on your needs)"""
    print(f"Saving tokens to storage: {tokens.access_token}")
    # In a real application, save to database, file, etc.

def load_refresh_token_from_storage() -> Optional[str]:
    """Load refresh token from storage (implement based on your needs)"""
    # In a real application, load from database, file, etc.
    return None

def client_credentials_example():
    """Example 1: Client Credentials Mode (Machine-to-Machine)"""
    print("=== Client Credentials Example ===")

    oauth_config = OAuthConfig(
        client_id="dvc-your-client-id",
        client_secret="dvs-your-client-secret",
        auto_refresh=True,
        on_token_refresh=save_tokens_to_storage
    )

    client = Client(
        oauth_config=oauth_config,
        timeout=30.0
    )

    try:
        # Initialize OAuth with client credentials
        result = client.initialize_oauth()
        if not result.success:
            print(f"Failed to get token: {result.error}")
            return

        print(f"Got access token: {result.data}")

        # Now you can make API calls - tokens will be automatically refreshed
        items_result = client.getItems(123, 456, limit=10)
        if items_result.success:
            print(f"Items: {items_result.data}")
        else:
            print(f"Failed to get items: {items_result.error}")

        # Get current user info
        user_result = client.get_current_user()
        if user_result.success:
            print(f"Current user: {user_result.data}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

def client_credentials_with_user_example():
    """Example 2: Client Credentials with User Token Mode"""
    print("=== Client Credentials with User Token Example ===")

    oauth_config = OAuthConfig(
        client_id="dvc-your-client-id",
        client_secret="dvs-your-client-secret",
        auto_refresh=True
    )

    client = Client(oauth_config=oauth_config)

    try:
        # Initialize OAuth with user access token
        user_access_token = "user-access-token-from-frontend"
        result = client.initialize_oauth(user_access_token)

        if result.success:
            print(f"Got user-context token: {result.data}")

            # This token represents the user and has their permissions
            user_info = client.get_current_user()
            if user_info.success:
                print(f"User info: {user_info.data}")
        else:
            print(f"Failed to get token: {result.error}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

def authorization_code_example():
    """Example 3: Authorization Code Flow"""
    print("=== Authorization Code Flow Example ===")

    oauth_config = OAuthConfig(
        client_id="dvc-your-client-id",
        client_secret="dvs-your-client-secret",
        auto_refresh=True
    )

    client = Client(oauth_config=oauth_config)

    try:
        # Step 1: Get authorization URL (this would be done in your web app)
        auth_request = OAuthAuthorizeCodeRequest(
            client_id="dvc-your-client-id",
            redirect_uri="https://your-app.com/callback",
            state="random-state-string",
            target_tenant_id=456  # For platform-level clients
        )

        auth_result = client.get_oauth_authorize_code(auth_request)
        if auth_result.success:
            print(f"Redirect user to: {auth_result.data.get('redirect_url')}")

        # Step 2: Exchange authorization code for tokens (after user authorizes)
        auth_code = "authorization-code-from-callback"
        token_result = client.exchange_authorization_code(
            auth_code,
            "https://your-app.com/callback"
        )

        if token_result.success:
            print(f"Got tokens: {token_result.data}")

            # Now you can make API calls on behalf of the user
            user_info = client.get_current_user()
            if user_info.success:
                print(f"Authorized user: {user_info.data}")
        else:
            print(f"Failed to exchange code: {token_result.error}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

def manual_refresh_example():
    """Example 4: Manual Token Refresh"""
    print("=== Manual Token Refresh Example ===")

    oauth_config = OAuthConfig(
        client_id="dvc-your-client-id",
        client_secret="dvs-your-client-secret",
        refresh_token="your-stored-refresh-token",
        auto_refresh=False  # Disable auto refresh
    )

    client = Client(oauth_config=oauth_config)

    try:
        # Manually refresh token
        refresh_result = client.refresh_oauth_token()
        if refresh_result.success:
            print(f"Refreshed token: {refresh_result.data}")

            # Get current tokens
            tokens = client.get_current_tokens()
            if tokens and tokens.refresh_token:
                print(f"New refresh token: {tokens.refresh_token}")
                # Store refresh_token for next time
        else:
            print(f"Refresh failed: {refresh_result.error}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

def token_management_example():
    """Example 5: Token Management with Callbacks"""
    print("=== Token Management Example ===")

    def on_token_refresh(tokens: OAuthTokens):
        """Callback function called when tokens are refreshed"""
        save_tokens_to_storage(tokens)
        print(f"Tokens refreshed and saved: {tokens.access_token}")

    # Simulate loading refresh token from storage
    stored_refresh_token = load_refresh_token_from_storage()

    oauth_config = OAuthConfig(
        client_id="dvc-your-client-id",
        client_secret="dvs-your-client-secret",
        refresh_token=stored_refresh_token,
        auto_refresh=True,
        on_token_refresh=on_token_refresh
    )

    client = Client(oauth_config=oauth_config)

    try:
        # Try to refresh token on startup if we have one
        if stored_refresh_token:
            refresh_result = client.refresh_oauth_token()
            if refresh_result.success:
                print("Token refreshed on startup")
        else:
            # Initialize with client credentials if no refresh token
            init_result = client.initialize_oauth()
            if init_result.success:
                print("Initialized with client credentials")

        # Check current token status
        current_tokens = client.get_current_tokens()
        if current_tokens:
            print(f"Current access token: {current_tokens.access_token}")
            print(f"Token scope: {current_tokens.scope}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

def error_handling_example():
    """Example 6: Error Handling"""
    print("=== Error Handling Example ===")

    # Client without OAuth config
    client_without_oauth = Client()

    try:
        result = client_without_oauth.refresh_oauth_token()
        if not result.success:
            print(f"Expected error: {result.error}")

        # Client with invalid credentials
        oauth_config = OAuthConfig(
            client_id="invalid-client-id",
            client_secret="invalid-secret"
        )

        client_with_bad_creds = Client(oauth_config=oauth_config)
        bad_result = client_with_bad_creds.initialize_oauth()
        if not bad_result.success:
            print(f"Authentication failed: {bad_result.error}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_without_oauth.close()

def advanced_usage_example():
    """Example 7: Advanced Usage with Custom Configuration"""
    print("=== Advanced Usage Example ===")

    def token_refresh_callback(tokens: OAuthTokens):
        print(f"Token refreshed: {tokens.access_token}")
        save_tokens_to_storage(tokens)

    oauth_config = OAuthConfig(
        client_id="dvc-your-client-id",
        client_secret="dvs-your-client-secret",
        auto_refresh=True,
        on_token_refresh=token_refresh_callback
    )

    client = Client(
        oauth_config=oauth_config,
        timeout=60.0,
        max_connections=50,
        max_keepalive_connections=10,
        http2=True,
        dns_cache=True
    )

    try:
        # Initialize OAuth
        result = client.initialize_oauth()
        if result.success:
            print("OAuth initialized successfully")

            # Make API calls with automatic token refresh
            items_result = client.getItems(123, 456, limit=20)
            if items_result.success:
                print(f"Query result: {items_result.data}")

            # Create new item
            new_item = {
                "title": "New Item",
                "status": "active"
            }

            create_result = client.createItem(123, 456, new_item)
            if create_result.success:
                print(f"Created item: {create_result.data}")

            # Update OAuth config dynamically
            new_config = OAuthConfig(
                client_id="dvc-new-client-id",
                client_secret="dvs-new-secret",
                auto_refresh=True
            )
            client.set_oauth_config(new_config)

            # Get current config
            config = client.get_oauth_config()
            if config:
                print(f"Current OAuth config: client_id={config.client_id}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

def context_manager_example():
    """Example 8: Using Client as Context Manager"""
    print("=== Context Manager Example ===")

    oauth_config = OAuthConfig(
        client_id="dvc-your-client-id",
        client_secret="dvs-your-client-secret",
        auto_refresh=True
    )

    # Using with statement for automatic cleanup
    with Client(oauth_config=oauth_config) as client:
        # Initialize OAuth
        result = client.initialize_oauth()
        if result.success:
            print("OAuth initialized in context manager")

            # Make API calls
            items = client.getItems(123, 456, limit=5)
            if items.success:
                print(f"Items retrieved: {len(items.data) if items.data else 0}")

        # Client will be automatically closed when exiting the with block

def main():
    """Run OAuth examples"""
    print("Carthooks Python SDK OAuth Examples")
    print("===================================")

    # Run examples (uncomment the ones you want to test)
    
    # client_credentials_example()
    # client_credentials_with_user_example()
    # authorization_code_example()
    # manual_refresh_example()
    # token_management_example()
    # error_handling_example()
    # advanced_usage_example()
    # context_manager_example()

    print("\nNote: Update the client credentials and URLs before running these examples")

if __name__ == "__main__":
    main()
