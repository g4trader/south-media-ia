from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from src.models.user import UserCreate, UserResponse, UserLogin, Token, UserRole
from src.services.auth_service import auth_service
from src.services.bigquery_service import BigQueryService
from typing import List, Dict, Any
import uuid
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Authentication"])
bigquery_service = BigQueryService()

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Login user and return JWT token"""
    try:
        # In a real implementation, you would fetch user from database
        # For now, we'll use mock data for demonstration
        
        # Mock user data (replace with database query)
        mock_users = {
            "admin@southmedia.com": {
                "id": "admin-001",
                "email": "admin@southmedia.com",
                "full_name": "Admin User",
                "role": UserRole.ADMIN,
                "status": "active",
                "hashed_password": auth_service.get_password_hash("admin123")
            },
            "agency@southmedia.com": {
                "id": "agency-001",
                "email": "agency@southmedia.com",
                "full_name": "Agency User",
                "role": UserRole.AGENCY,
                "status": "active",
                "agency_id": "agency-001",
                "hashed_password": auth_service.get_password_hash("agency123")
            },
            "client@example.com": {
                "id": "client-001",
                "email": "client@example.com",
                "full_name": "Client User",
                "role": UserRole.CLIENT,
                "status": "active",
                "agency_id": "agency-001",
                "client_id": "client-001",
                "hashed_password": auth_service.get_password_hash("client123")
            }
        }
        
        user_data = mock_users.get(user_credentials.email)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Authenticate user
        authenticated_user = auth_service.authenticate_user(
            user_credentials.email, 
            user_credentials.password, 
            user_data
        )
        
        if not authenticated_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create access token
        token_data = {
            "sub": authenticated_user["id"],
            "email": authenticated_user["email"],
            "role": authenticated_user["role"],
            "agency_id": authenticated_user.get("agency_id"),
            "client_id": authenticated_user.get("client_id")
        }
        
        access_token = auth_service.create_access_token(token_data)
        
        # Create user response
        user_response = UserResponse(
            id=authenticated_user["id"],
            email=authenticated_user["email"],
            full_name=authenticated_user["full_name"],
            role=authenticated_user["role"],
            status=authenticated_user["status"],
            agency_id=authenticated_user.get("agency_id"),
            client_id=authenticated_user.get("client_id"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, current_user: Dict[str, Any] = Depends(auth_service.require_role([UserRole.ADMIN]))):
    """Register a new user (admin only)"""
    try:
        # In a real implementation, you would save to database
        # For now, we'll return a mock response
        
        new_user = UserResponse(
            id=str(uuid.uuid4()),
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role,
            status=user_data.status,
            agency_id=user_data.agency_id,
            client_id=user_data.client_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return new_user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(auth_service.get_current_user)):
    """Get current user information"""
    try:
        # In a real implementation, you would fetch from database
        # For now, we'll return the current user data
        
        user_response = UserResponse(
            id=current_user["sub"],
            email=current_user["email"],
            full_name="Current User",  # Would come from database
            role=current_user["role"],
            status="active",
            agency_id=current_user.get("agency_id"),
            client_id=current_user.get("client_id"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return user_response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}"
        )

@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(auth_service.get_current_user)):
    """Logout user (in a real implementation, you might blacklist the token)"""
    return {"message": "Successfully logged out"}

@router.get("/users", response_model=List[UserResponse])
async def get_users(current_user: Dict[str, Any] = Depends(auth_service.require_role([UserRole.ADMIN]))):
    """Get all users (admin only)"""
    try:
        # In a real implementation, you would fetch from database
        # For now, we'll return mock data
        
        mock_users = [
            UserResponse(
                id="admin-001",
                email="admin@southmedia.com",
                full_name="Admin User",
                role=UserRole.ADMIN,
                status="active",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            UserResponse(
                id="agency-001",
                email="agency@southmedia.com",
                full_name="Agency User",
                role=UserRole.AGENCY,
                status="active",
                agency_id="agency-001",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            UserResponse(
                id="client-001",
                email="client@example.com",
                full_name="Client User",
                role=UserRole.CLIENT,
                status="active",
                agency_id="agency-001",
                client_id="client-001",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        
        return mock_users
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {str(e)}"
        )


