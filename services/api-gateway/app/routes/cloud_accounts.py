"""
Cloud Accounts Routes
Manages multi-cloud account credentials and metadata
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any
from datetime import datetime
import uuid

from app.models.cloud_account import (
    CloudAccountCreate,
    CloudAccountUpdate,
    CloudAccountResponse,
    CloudAccountDetail,
    CloudProvider,
    CloudAccountStatus
)
from app.middleware.auth import get_current_user

router = APIRouter()

# Mock in-memory storage (replace with database later)
# Structure: {user_id: {account_id: account_data}}
MOCK_ACCOUNTS: Dict[str, Dict[str, Dict[str, Any]]] = {}


def mask_credentials(provider: str, credentials: Dict[str, Any]) -> Dict[str, str]:
    """Mask sensitive credential data for API responses"""
    masked = {}

    if provider == CloudProvider.AWS:
        if "access_key_id" in credentials:
            key = credentials["access_key_id"]
            masked["access_key_id"] = f"{key[:4]}****{key[-7:]}" if len(key) > 11 else "****"
        if "region" in credentials:
            masked["region"] = credentials["region"]

    elif provider == CloudProvider.AZURE:
        if "subscription_id" in credentials:
            sub_id = credentials["subscription_id"]
            masked["subscription_id"] = f"{sub_id[:8]}-****-****-****-{sub_id[-12:]}" if len(sub_id) > 20 else "****"
        if "tenant_id" in credentials:
            tenant = credentials["tenant_id"]
            masked["tenant_id"] = f"{tenant[:8]}****" if len(tenant) > 8 else "****"

    elif provider == CloudProvider.GCP:
        if "project_id" in credentials:
            masked["project_id"] = credentials["project_id"]
        if "service_account_key" in credentials:
            masked["service_account_key"] = "****[KEY_PRESENT]****"

    return masked


@router.post("/", response_model=CloudAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_cloud_account(
    account: CloudAccountCreate,
    current_user: dict = Depends(get_current_user)
) -> CloudAccountResponse:
    """Create a new cloud account"""
    user_id = current_user.get("user_id") or current_user.get("sub")

    # Initialize user's accounts dict if not exists
    if user_id not in MOCK_ACCOUNTS:
        MOCK_ACCOUNTS[user_id] = {}

    # Generate account ID
    account_id = f"acc_{uuid.uuid4().hex[:12]}"

    # Create account record
    now = datetime.utcnow()
    account_data = {
        "id": account_id,
        "user_id": user_id,
        "name": account.name,
        "provider": account.provider.value,
        "description": account.description,
        "credentials": account.credentials,  # In production, encrypt this!
        "status": CloudAccountStatus.CONNECTED.value,
        "created_at": now,
        "updated_at": now,
        "last_scan_at": None,
        "resource_count": 0,
        "monthly_cost": 0.0
    }

    # Store account
    MOCK_ACCOUNTS[user_id][account_id] = account_data

    # Return response (without credentials)
    return CloudAccountResponse(
        id=account_data["id"],
        user_id=account_data["user_id"],
        name=account_data["name"],
        provider=account_data["provider"],
        description=account_data["description"],
        status=account_data["status"],
        created_at=account_data["created_at"],
        updated_at=account_data["updated_at"],
        last_scan_at=account_data["last_scan_at"],
        resource_count=account_data["resource_count"],
        monthly_cost=account_data["monthly_cost"]
    )


@router.get("/", response_model=List[CloudAccountResponse])
async def list_cloud_accounts(
    current_user: dict = Depends(get_current_user)
) -> List[CloudAccountResponse]:
    """List all cloud accounts for the current user"""
    user_id = current_user.get("user_id") or current_user.get("sub")

    # Get user's accounts
    user_accounts = MOCK_ACCOUNTS.get(user_id, {})

    # Convert to response models
    accounts = []
    for account_data in user_accounts.values():
        accounts.append(CloudAccountResponse(
            id=account_data["id"],
            user_id=account_data["user_id"],
            name=account_data["name"],
            provider=account_data["provider"],
            description=account_data["description"],
            status=account_data["status"],
            created_at=account_data["created_at"],
            updated_at=account_data["updated_at"],
            last_scan_at=account_data["last_scan_at"],
            resource_count=account_data["resource_count"],
            monthly_cost=account_data["monthly_cost"]
        ))

    return accounts


@router.get("/{account_id}", response_model=CloudAccountDetail)
async def get_cloud_account(
    account_id: str,
    current_user: dict = Depends(get_current_user)
) -> CloudAccountDetail:
    """Get details of a specific cloud account"""
    user_id = current_user.get("user_id") or current_user.get("sub")

    # Check if account exists and belongs to user
    user_accounts = MOCK_ACCOUNTS.get(user_id, {})
    if account_id not in user_accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cloud account not found"
        )

    account_data = user_accounts[account_id]

    # Mask credentials
    credentials_summary = mask_credentials(
        account_data["provider"],
        account_data["credentials"]
    )

    return CloudAccountDetail(
        id=account_data["id"],
        user_id=account_data["user_id"],
        name=account_data["name"],
        provider=account_data["provider"],
        description=account_data["description"],
        status=account_data["status"],
        created_at=account_data["created_at"],
        updated_at=account_data["updated_at"],
        last_scan_at=account_data["last_scan_at"],
        resource_count=account_data["resource_count"],
        monthly_cost=account_data["monthly_cost"],
        credentials_summary=credentials_summary
    )


@router.put("/{account_id}", response_model=CloudAccountResponse)
async def update_cloud_account(
    account_id: str,
    account_update: CloudAccountUpdate,
    current_user: dict = Depends(get_current_user)
) -> CloudAccountResponse:
    """Update a cloud account"""
    user_id = current_user.get("user_id") or current_user.get("sub")

    # Check if account exists and belongs to user
    user_accounts = MOCK_ACCOUNTS.get(user_id, {})
    if account_id not in user_accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cloud account not found"
        )

    account_data = user_accounts[account_id]

    # Update fields
    if account_update.name is not None:
        account_data["name"] = account_update.name
    if account_update.description is not None:
        account_data["description"] = account_update.description
    if account_update.credentials is not None:
        account_data["credentials"] = account_update.credentials
    if account_update.status is not None:
        account_data["status"] = account_update.status.value

    account_data["updated_at"] = datetime.utcnow()

    return CloudAccountResponse(
        id=account_data["id"],
        user_id=account_data["user_id"],
        name=account_data["name"],
        provider=account_data["provider"],
        description=account_data["description"],
        status=account_data["status"],
        created_at=account_data["created_at"],
        updated_at=account_data["updated_at"],
        last_scan_at=account_data["last_scan_at"],
        resource_count=account_data["resource_count"],
        monthly_cost=account_data["monthly_cost"]
    )


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cloud_account(
    account_id: str,
    current_user: dict = Depends(get_current_user)
) -> None:
    """Delete a cloud account"""
    user_id = current_user.get("user_id") or current_user.get("sub")

    # Check if account exists and belongs to user
    user_accounts = MOCK_ACCOUNTS.get(user_id, {})
    if account_id not in user_accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cloud account not found"
        )

    # Delete account
    del user_accounts[account_id]


@router.post("/{account_id}/scan", response_model=Dict[str, Any])
async def scan_cloud_account(
    account_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Trigger a resource scan for a cloud account"""
    user_id = current_user.get("user_id") or current_user.get("sub")

    # Check if account exists and belongs to user
    user_accounts = MOCK_ACCOUNTS.get(user_id, {})
    if account_id not in user_accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cloud account not found"
        )

    account_data = user_accounts[account_id]

    # In production, this would trigger actual cloud scanning
    # For now, just update the last_scan_at timestamp
    account_data["last_scan_at"] = datetime.utcnow()

    return {
        "message": "Scan initiated successfully",
        "account_id": account_id,
        "provider": account_data["provider"],
        "status": "scanning"
    }
