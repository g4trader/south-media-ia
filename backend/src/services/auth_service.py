from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.config import settings
from src.models.user import UserRole, UserStatus

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()

class AuthService:
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def authenticate_user(self, email: str, password: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Authenticate a user with email and password"""
        if not user_data:
            return None
        
        if not self.verify_password(password, user_data.get("hashed_password", "")):
            return None
        
        if user_data.get("status") != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active"
            )
        
        return user_data
    
    def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """Get current user from JWT token"""
        token = credentials.credentials
        payload = self.verify_token(token)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        # In a real implementation, you would fetch user from database
        # For now, we'll return the payload data
        return payload
    
    def check_permission(self, user: Dict[str, Any], resource: str, action: str) -> bool:
        """Check if user has permission for a specific resource and action"""
        user_role = user.get("role")
        
        # Admin has all permissions
        if user_role == UserRole.ADMIN:
            return True
        
        # Agency users can access their own clients' data
        if user_role == UserRole.AGENCY:
            if resource in ["campaign", "dashboard", "reports"] and action == "read":
                return True
        
        # Client users can only access their own data
        if user_role == UserRole.CLIENT:
            if resource in ["campaign", "dashboard"] and action == "read":
                return True
        
        return False
    
    def require_permission(self, resource: str, action: str):
        """Decorator to require specific permissions"""
        def permission_checker(user: Dict[str, Any] = Depends(AuthService().get_current_user)):
            if not AuthService().check_permission(user, resource, action):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
            return user
        return permission_checker
    
    def require_role(self, allowed_roles: list):
        """Decorator to require specific user roles"""
        def role_checker(user: Dict[str, Any] = Depends(AuthService().get_current_user)):
            if user.get("role") not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
            return user
        return role_checker

# Global auth service instance
auth_service = AuthService()

# Permission decorators
require_admin = auth_service.require_role([UserRole.ADMIN])
require_agency = auth_service.require_role([UserRole.ADMIN, UserRole.AGENCY])
require_client = auth_service.require_role([UserRole.ADMIN, UserRole.AGENCY, UserRole.CLIENT])

# Resource-specific permission decorators
can_read_campaigns = auth_service.require_permission("campaign", "read")
can_write_campaigns = auth_service.require_permission("campaign", "write")
can_read_dashboards = auth_service.require_permission("dashboard", "read")
can_write_dashboards = auth_service.require_permission("dashboard", "write")
