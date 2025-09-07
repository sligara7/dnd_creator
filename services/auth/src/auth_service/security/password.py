"""Password service for secure password hashing and verification."""

import secrets
import string
from typing import Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash


class PasswordService:
    """Service for password hashing and verification using Argon2."""
    
    def __init__(
        self,
        time_cost: int = 2,
        memory_cost: int = 65536,
        parallelism: int = 1,
        hash_len: int = 32,
        salt_len: int = 16,
    ):
        """
        Initialize password service with Argon2 parameters.
        
        Args:
            time_cost: Number of iterations (default: 2)
            memory_cost: Memory usage in kilobytes (default: 64MB)
            parallelism: Number of parallel threads (default: 1)
            hash_len: Length of the hash in bytes (default: 32)
            salt_len: Length of the salt in bytes (default: 16)
        """
        self.hasher = PasswordHasher(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
            hash_len=hash_len,
            salt_len=salt_len,
        )
        
        # Password policy settings
        self.min_length = 8
        self.max_length = 128
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_digit = True
        self.require_special = True
        self.special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using Argon2id.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            Hashed password string
            
        Raises:
            ValueError: If password doesn't meet requirements
        """
        self.validate_password_strength(password)
        return self.hasher.hash(password)
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password to verify
            password_hash: Hashed password to verify against
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            self.hasher.verify(password_hash, password)
            return True
        except (VerifyMismatchError, VerificationError, InvalidHash):
            return False
    
    def needs_rehash(self, password_hash: str) -> bool:
        """
        Check if password hash needs to be rehashed with updated parameters.
        
        Args:
            password_hash: Current password hash
            
        Returns:
            True if rehashing is needed, False otherwise
        """
        try:
            return self.hasher.check_needs_rehash(password_hash)
        except (InvalidHash, AttributeError):
            return True
    
    def validate_password_strength(self, password: str) -> None:
        """
        Validate password meets strength requirements.
        
        Args:
            password: Password to validate
            
        Raises:
            ValueError: If password doesn't meet requirements
        """
        errors = []
        
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters")
        
        if len(password) > self.max_length:
            errors.append(f"Password must be no more than {self.max_length} characters")
        
        if self.require_uppercase and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.require_lowercase and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.require_digit and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")
        
        if self.require_special and not any(c in self.special_chars for c in password):
            errors.append(f"Password must contain at least one special character: {self.special_chars}")
        
        if errors:
            raise ValueError("; ".join(errors))
    
    def generate_strong_password(
        self,
        length: int = 16,
        exclude_ambiguous: bool = True
    ) -> str:
        """
        Generate a strong random password.
        
        Args:
            length: Length of password to generate (default: 16)
            exclude_ambiguous: Exclude ambiguous characters (0, O, l, I)
            
        Returns:
            Generated password string
        """
        # Build character set
        chars = ""
        
        if self.require_lowercase:
            chars += string.ascii_lowercase
        
        if self.require_uppercase:
            chars += string.ascii_uppercase
        
        if self.require_digit:
            chars += string.digits
        
        if self.require_special:
            chars += self.special_chars
        
        # Remove ambiguous characters if requested
        if exclude_ambiguous:
            ambiguous = "0OlI1"
            chars = "".join(c for c in chars if c not in ambiguous)
        
        # Ensure we have at least one of each required type
        password_chars = []
        
        if self.require_lowercase:
            password_chars.append(secrets.choice(string.ascii_lowercase))
        
        if self.require_uppercase:
            password_chars.append(secrets.choice(string.ascii_uppercase))
        
        if self.require_digit:
            password_chars.append(secrets.choice(string.digits))
        
        if self.require_special:
            password_chars.append(secrets.choice(self.special_chars))
        
        # Fill the rest randomly
        remaining_length = length - len(password_chars)
        password_chars.extend(
            secrets.choice(chars) for _ in range(remaining_length)
        )
        
        # Shuffle the password
        password = list(password_chars)
        for i in range(len(password) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            password[i], password[j] = password[j], password[i]
        
        return "".join(password)
    
    def generate_recovery_code(self) -> str:
        """
        Generate a recovery code for account recovery.
        
        Returns:
            Recovery code string (format: XXXX-XXXX-XXXX-XXXX)
        """
        chars = string.ascii_uppercase + string.digits
        # Exclude ambiguous characters
        chars = "".join(c for c in chars if c not in "0OI1")
        
        parts = []
        for _ in range(4):
            part = "".join(secrets.choice(chars) for _ in range(4))
            parts.append(part)
        
        return "-".join(parts)
    
    def generate_recovery_codes(self, count: int = 10) -> list[str]:
        """
        Generate multiple recovery codes.
        
        Args:
            count: Number of codes to generate (default: 10)
            
        Returns:
            List of recovery code strings
        """
        codes = set()
        while len(codes) < count:
            codes.add(self.generate_recovery_code())
        return list(codes)
