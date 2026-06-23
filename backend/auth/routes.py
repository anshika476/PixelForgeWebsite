from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from .models import UserSignup, UserLogin, UserResponse, TokenResponse
from .utils import hash_password, verify_password, create_access_token
from .database import users_collection
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse)
async def signup(user: UserSignup):

    print("🔥 SIGNUP REQUEST RECEIVED")

    print("➡️ Email:", user.email)

    print("⏳ Checking if user exists...")
    existing_user = await users_collection.find_one({"email": user.email})
    print("✅ Existing user check done")
    if existing_user:
        print("⚠️ User already exists:", user.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    print("✅ User does not exist, proceeding")

    # 2️⃣ Hash password
    print("🔐 Hashing password...")
    hashed_pw = hash_password(user.password)
    print("🔐 Password hashed")

    # 3️⃣ Insert user
    user_doc = {
        "email": user.email,
        "name": user.name,
        "hashed_password": hashed_pw,
        "created_at": datetime.utcnow(),
    }

    print("💾 Inserting user into MongoDB...")
    result = await users_collection.insert_one(user_doc)
    print("✅ Mongo insert successful:", result.inserted_id)

    # 4️⃣ Create token
    print("🎟 Creating JWT token...")
    token = create_access_token(
        data={
            "sub": user.email,
            "user_id": str(result.inserted_id)
        }
    )
    print("✅ Token created")

    # 5️⃣ Prepare response
    user_response = UserResponse(
        id=str(result.inserted_id),
        email=user.email,
        name=user.name,
        created_at=user_doc["created_at"]
    )

    print("🎉 Signup completed successfully for:", user.email)

    return TokenResponse(token=token, user=user_response)


# @router.post("/login", response_model=TokenResponse)
# async def login(credentials: UserLogin):
#     print("🔑 LOGIN REQUEST")
#     print("📧 Email:", credentials.email)

#     # 1️⃣ Find user
#     print("🔍 Searching user in DB...")
#     user = await users_collection.find_one({"email": credentials.email})

#     if not user:
#         print("❌ User not found")
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid email or password"
#         )

#     print("✅ User found:", user["_id"])

#     # 2️⃣ Verify password
#     print("🔐 Verifying password...")
#     if not verify_password(credentials.password, user["hashed_password"]):
#         print("❌ Password mismatch")
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid email or password"
#         )

#     print("✅ Password verified")

#     # 3️⃣ Create token
#     print("🎟 Creating JWT token...")
#     token = create_access_token(
#         data={
#             "sub": user["email"],
#             "user_id": str(user["_id"])
#         }
#     )
#     print("✅ Token created")

#     user_response = UserResponse(
#         id=str(user["_id"]),
#         email=user["email"],
#         name=user["name"],
#         created_at=user["created_at"]
#     )

#     print("🎉 Login successful for:", credentials.email)

#     return TokenResponse(token=token, user=user_response)
