#!/usr/bin/env python3
"""
Delete all vector stores matching the pattern FileSearchVectorStorexxxx.

This script connects to Azure AI and deletes all vector stores whose names
start with "FileSearchVectorStore" followed by any characters (typically random numbers).
"""

import os
import re
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


def delete_matching_vector_stores():
    """Delete all vector stores matching the FileSearchVectorStorexxxx pattern."""
    
    # Get Azure OpenAI configuration from environment
    azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://new-foundry-proj-resource.openai.azure.com/")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview")
    
    print("=" * 70)
    print("Vector Store Cleanup Utility (Responses API)")
    print("=" * 70)
    print(f"\nConnecting to: {azure_openai_endpoint}")
    print("🔐 Using Azure credential token authentication")
    
    try:
        # Create Azure credential token provider
        credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(
            credential,
            "https://cognitiveservices.azure.com/.default"
        )
        
        # Create Azure OpenAI client with token authentication
        client = AzureOpenAI(
            azure_ad_token_provider=token_provider,
            api_version=api_version,
            azure_endpoint=azure_openai_endpoint
        )
    except Exception as e:
        print(f"❌ Error: Failed to authenticate with Azure credentials: {e}")
        print("Please ensure you are logged in with 'az login' or have appropriate credentials configured")
        return
    
    try:
        # List all vector stores
        print("\n🔍 Listing all vector stores...")
        vector_stores_response = client.vector_stores.list()
        
        # Pattern to match ResponsesVectorStore followed by any characters
        pattern = re.compile(r'^ResponsesVectorStore.*')
        
        matching_stores = []
        all_stores = []
        
        for store in vector_stores_response.data:
            all_stores.append(store)
            if pattern.match(store.name):
                matching_stores.append(store)
        
        print(f"   Total vector stores found: {len(all_stores)}")
        print(f"   Matching stores (FileSearchVectorStore*): {len(matching_stores)}")
        
        if not matching_stores:
            print("\n✅ No matching vector stores found. Nothing to delete.")
            return
        
        # Display matching stores
        print("\n📋 Matching vector stores to delete:")
        for store in matching_stores:
            print(f"   - {store.name} (ID: {store.id})")
        
        # Confirm deletion
        print(f"\n⚠️  WARNING: This will delete {len(matching_stores)} vector store(s)")
        response = input("Do you want to proceed? (yes/no): ")
        
        if response.lower() not in ['yes', 'y']:
            print("\n❌ Deletion cancelled by user")
            return
        
        # Delete each matching vector store
        print("\n🗑️  Deleting vector stores...")
        deleted_count = 0
        failed_count = 0
        
        for store in matching_stores:
            try:
                client.vector_stores.delete(store.id)
                print(f"   ✓ Deleted: {store.name} (ID: {store.id})")
                deleted_count += 1
            except Exception as e:
                print(f"   ✗ Failed to delete {store.name}: {e}")
                failed_count += 1
        
        # Summary
        print("\n" + "=" * 70)
        print("Summary:")
        print(f"   ✓ Successfully deleted: {deleted_count}")
        if failed_count > 0:
            print(f"   ✗ Failed to delete: {failed_count}")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run the cleanup utility."""
    try:
        delete_matching_vector_stores()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
