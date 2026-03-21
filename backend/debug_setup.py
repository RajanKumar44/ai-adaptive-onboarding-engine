#!/usr/bin/env python3
"""
Simple test to debug the API setup
"""
import sys
sys.path.insert(0, '/c/Users/Rajan/OneDrive/Desktop/ai-adaptive-onboarding-engine-main/backend')

# Test 1: Check config
print("=" * 60)
print("TEST 1: Checking config settings...")
print("=" * 60)
try:
    from app.core.config import get_settings
    settings = get_settings()
    print(f"✓ App name: {settings.APP_NAME}")
    print(f"✓ JWT enabled: {settings.JWT_SECRET_KEY != ''}")
    print(f"✓ PASSWORD_MIN_LENGTH: {settings.PASSWORD_MIN_LENGTH}")
    print(f"✓ PASSWORD_REQUIRE_UPPERCASE: {settings.PASSWORD_REQUIRE_UPPERCASE}")
    print(f"✓ PASSWORD_REQUIRE_LOWERCASE: {settings.PASSWORD_REQUIRE_LOWERCASE}")
    print(f"✓ PASSWORD_REQUIRE_DIGITS: {settings.PASSWORD_REQUIRE_DIGITS}")
except Exception as e:
    print(f"✗ Config error: {e}")

# Test 2: Check models registration
print("\n" + "=" * 60)
print("TEST 2: Checking model registration...")
print("=" * 60)
try:
    from app.core.database import Base
    from app.models import User, Analysis, AuditLog
    print(f"✓ Base metadata tables: {list(Base.metadata.tables.keys())}")
    print(f"✓ User model: {User.__tablename__}")
    print(f"✓ Analysis model: {Analysis.__tablename__}")
    print(f"✓ AuditLog model: {AuditLog.__tablename__}")
except Exception as e:
    print(f"✗ Model error: {e}")

# Test 3: Check security manager
print("\n" + "=" * 60)
print("TEST 3: Checking security manager...")
print("=" * 60)
try:
    from app.core.security import SecurityManager
    # Test password validation with the new config
    is_valid, msg = SecurityManager.validate_password_strength("TestPass123")
    print(f"✓ Password validation works")
    print(f"  Test password 'TestPass123': {'VALID' if is_valid else 'INVALID'}")
    if not is_valid:
        print(f"  Error: {msg}")
    
    # Test with weak password
    is_valid_weak, msg_weak = SecurityManager.validate_password_strength("test")
    print(f"✓ Weak password correctly rejected: {not is_valid_weak}")
    if not is_valid_weak:
        print(f"  Error: {msg_weak}")
except Exception as e:
    print(f"✗ Security error: {e}")

# Test 4: Check routes
print("\n" + "=" * 60)
print("TEST 4: Checking route registration...")
print("=" * 60)
try:
    from app.routes.auth_routes import router as auth_router
    from app.routes.bulk_routes import router as bulk_router
    from app.routes.llm_routes import router as llm_router
    from app.routes.metrics_routes import router as metrics_router
    
    print(f"✓ Auth router prefix: {auth_router.prefix}")
    print(f"✓ Bulk router prefix: {bulk_router.prefix}")
    print(f"✓ LLM router prefix: {llm_router.prefix}")
    print(f"✓ Metrics router prefix: {metrics_router.prefix}")
except Exception as e:
    print(f"✗ Route error: {e}")

# Test 5: Try to validate database initialization
print("\n" + "=" * 60)
print("TEST 5: Checking database connectivity...")
print("=" * 60)
try:
    from app.core.database import engine, Base, init_db
    # Check if we can connect to the database
    with engine.connect() as conn:
        print(f"✓ Can connect to database at {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
        # Try to create tables
        try:
            Base.metadata.create_all(bind=engine)
            print(f"✓ Database tables created successfully")
        except Exception as create_err:
            print(f"✗ Error creating tables: {create_err}")
except Exception as e:
    print(f"✗ Database error: {e}")
    print(f"  This is expected if Docker database isn't running")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("If all tests pass, the issue is with Docker/networking")
print("If tests fail, read the error messages above")
