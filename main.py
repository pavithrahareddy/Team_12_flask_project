from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List, Optional
import datetime
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

# FastAPI app
app = FastAPI()

# MongoDB settings
MONGO_DB_URL = "mongodb://localhost:27017"
MONGO_DB_NAME = "cloud_subscription_management"
client = AsyncIOMotorClient(MONGO_DB_URL)
db = client[MONGO_DB_NAME]
SECRET_KEY = "mysecretkey"

# OAuth2 for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Credentials(BaseModel):
    username: str
    password: str

# Model for Subscription Plan
class SubscriptionPlan(BaseModel):
    name: str
    description: str
    permissions: List[str]
    usage_limit: int

# Model for Permission
class Permission(BaseModel):
    name: str
    endpoint: str
    description: str

# Model for User Subscription
class UserSubscription(BaseModel):
    user_id: str
    plan_id: str

# Model for API Usage Tracking
class APIUsage(BaseModel):
    user_id: str
    api_request: str

# Model for User Subscription Modification
class UserSubscriptionModification(BaseModel):
    plan_id: str

# MongoDB Collection Names
PLANS_COLLECTION = "subscription_plans"
PERMISSIONS_COLLECTION = "permissions"
SUBSCRIPTIONS_COLLECTION = "subscriptions"
USAGE_COLLECTION = "usage_tracking"
USERS_COLLECTION = "user_collection"

# Function to get MongoDB collection
def get_collection(collection_name):
    return db[collection_name]


# Function to get user subscription details
async def get_user_subscription(user_id: str):
    subscription_collection = get_collection(SUBSCRIPTIONS_COLLECTION)
    subscription = await subscription_collection.find_one({"user_id": user_id})
    return subscription

# Function to check user access permission
async def check_access_permission(user_id: str, api_request: str):
    subscription_collection = get_collection(SUBSCRIPTIONS_COLLECTION)
    plan_collection = get_collection(PLANS_COLLECTION)

    user_subscription = await subscription_collection.find_one({"user_id": user_id})
    if not user_subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User subscription not found")

    plan_id = user_subscription["plan_id"]
    plan = await plan_collection.find_one({"name": plan_id})

    if api_request not in plan["permissions"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")
    
async def check_authentication(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        current_user = payload['username']
        user_collection = get_collection(USERS_COLLECTION)
        user_exists = await user_collection.find_one({"username": current_user})
        if current_user=="admin" or user_exists:
            return current_user
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorised!") 
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorised!") 
    

# Routes for Subscription Plan Management
@app.get("/")
async def home():
  return {"Welcome All"}

@app.post("/adminlogin")
async def admin_login(credentials: Credentials):
    if credentials.password=='admin123':
        expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=180)
        token = jwt.encode({'username': credentials.username, 'exp': expiration}, SECRET_KEY, algorithm='HS256')
        return {token}
    else:
        return {"Please recheck your credentials"}
    
@app.post("/user_signup")
async def create_user(credentials: Credentials):
    user_collection = get_collection(USERS_COLLECTION)
    user_exists = await user_collection.find_one({"username": credentials.username})
    if not user_exists:
        result = await user_collection.insert_one(credentials.dict())
        return {"user created successfully!"}
    else:
        return {"username already exists!"}

@app.post("/user_signin")
async def create_user(credentials: Credentials):
    user_collection = get_collection(USERS_COLLECTION)
    user_exists = await user_collection.find_one({"username": credentials.username})
    if user_exists and user_exists["username"]==credentials.username and user_exists["password"]==credentials.password:
        expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=1)
        token = jwt.encode({'username': credentials.username, 'exp': expiration}, SECRET_KEY, algorithm='HS256')
        return {token}
    else:
        return {"You dont have access"}

@app.post("/plans", response_model=SubscriptionPlan)
async def create_plan(plan: SubscriptionPlan, token: str = Depends(oauth2_scheme)):
    current_user =  await check_authentication(token)
    if current_user=="admin":
        plan_collection = get_collection(PLANS_COLLECTION)
        result = await plan_collection.insert_one(plan.dict())
        return {**plan.dict(), "_id": str(result.inserted_id)}

@app.put("/plans/{plan_id}", response_model=SubscriptionPlan)
async def modify_plan(plan_id: str, plan: SubscriptionPlan, token: str = Depends(oauth2_scheme)):
    current_user =  await check_authentication(token)
    if current_user=="admin":
        plan_collection = get_collection(PLANS_COLLECTION)
        await plan_collection.update_one({"name": plan_id}, {"$set": plan.dict()})
        return {**plan.dict(), "_id": plan_id}

@app.delete("/plans/{plan_id}", response_model=dict)
async def delete_plan(plan_id: str, token: str = Depends(oauth2_scheme)):
    current_user =  await check_authentication(token)
    if current_user=="admin":
        plan_collection = get_collection(PLANS_COLLECTION)
        result = await plan_collection.delete_one({"name": plan_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
        return {"message": "Plan deleted successfully"}

# Routes for Permission Management

@app.post("/permissions", response_model=Permission)
async def add_permission(permission: Permission, token: str = Depends(oauth2_scheme)):
    current_user =  await check_authentication(token)
    if current_user=="admin":
        permission_collection = get_collection(PERMISSIONS_COLLECTION)
        result = await permission_collection.insert_one(permission.dict())
        return {**permission.dict(), "_id": str(result.inserted_id)}

@app.put("/permissions/{permission_id}", response_model=Permission)
async def modify_permission(permission_id: str, permission: Permission, token: str = Depends(oauth2_scheme)):
    current_user =  await check_authentication(token)
    if current_user=="admin":
        permission_collection = get_collection(PERMISSIONS_COLLECTION)
        await permission_collection.update_one({"name": permission_id}, {"$set": permission.dict()})
        return {**permission.dict(), "_id": permission_id}

@app.delete("/permissions/{permission_id}", response_model=dict)
async def delete_permission(permission_id: str, token: str = Depends(oauth2_scheme)):
    current_user =  await check_authentication(token)
    if current_user=="admin":
        permission_collection = get_collection(PERMISSIONS_COLLECTION)
        result = await permission_collection.delete_one({"name": permission_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
        return {"message": "Permission deleted successfully"}

# Routes for User Subscription Handling

@app.post("/subscriptions", response_model=UserSubscription)
async def subscribe_to_plan(subscription: UserSubscription,  token: str = Depends(oauth2_scheme)):
    current_user =  await check_authentication(token)
    if current_user:
        subscription_collection = get_collection(SUBSCRIPTIONS_COLLECTION)
        plan_collection = get_collection(PLANS_COLLECTION)

        # Check if the user and plan exist
        user_exists = await subscription_collection.find_one({"user_id": subscription.user_id})
        plan_exists = await plan_collection.find_one({"name": subscription.plan_id})

        if not plan_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

        # Crate or Update user subscription
        if not user_exists:
            await subscription_collection.insert_one(subscription.dict())
        else:
            await subscription_collection.update_one({"user_id": subscription.user_id},
                                                {"$set": {"plan_id": subscription.plan_id}},
                                                upsert=True)
        return subscription.dict()

@app.get("/subscriptions/{user_id}", response_model=UserSubscription)
async def view_subscription_details(user_id: str, token: str = Depends(oauth2_scheme)):
    current_user =  await check_authentication(token)
    if current_user:
        subscription = await get_user_subscription(user_id)
        if not subscription:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User subscription not found")
        plan_collection = get_collection(PLANS_COLLECTION)
        result = await plan_collection.find_one({"name": subscription["plan_id"]})
        return {**subscription, **result}

@app.get("/subscriptions/{user_id}/usage", response_model=dict)
async def view_usage_statistics(user_id: str, token: str = Depends(oauth2_scheme)):
    current_user =  await check_authentication(token)
    if current_user:
        usage_collection = get_collection(USAGE_COLLECTION)
        usage_count = await usage_collection.count_documents({"user_id": user_id})
        return {"user_id": user_id, "usage_count": usage_count}

@app.put("/subscriptions/{user_id}", response_model=UserSubscription)
async def subscribe_to_plan(subscription: UserSubscription, token: str = Depends(oauth2_scheme)):
    current_user =  await check_authentication(token)
    if current_user:
        subscription_collection = get_collection(SUBSCRIPTIONS_COLLECTION)
        plan_collection = get_collection(PLANS_COLLECTION)

        # Check if the user and plan exist
        user_exists = await subscription_collection.find_one({"user_id": subscription.user_id})
        plan_exists = await plan_collection.find_one({"name": subscription.plan_id})

        if not plan_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

        if not user_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist!")
        else:
            await subscription_collection.update_one({"user_id": subscription.user_id},
                                                {"$set": {"plan_id": subscription.plan_id}},
                                                upsert=True)
        return subscription.dict()

# Routes for Access Control

@app.get("/access/{user_id}/{api_request}", response_model=dict)
async def check_access_permission_route(user_id: str, api_request: str, token: str = Depends(oauth2_scheme)):
    current_user =  await check_authentication(token)
    if current_user:
        await check_access_permission(user_id, api_request)
        return {"message": "Access granted"}

# Routes for Usage Tracking and Limit Enforcement

@app.post("/usage/{user_id}", response_model=dict)
async def track_api_request(usage : APIUsage, token: str = Depends(oauth2_scheme)):
    current_user =  await check_authentication(token)
    if current_user:
        usage_collection = get_collection(USAGE_COLLECTION)
        subscription_collection = get_collection(SUBSCRIPTIONS_COLLECTION)
        plan_collection = get_collection(PLANS_COLLECTION)

        # Check if the user and plan exist
        user_exists = await subscription_collection.find_one({"user_id": usage.user_id})
        if user_exists:
            plan_exists = await plan_collection.find_one({"name": user_exists["plan_id"]})
            if not plan_exists:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
        # Check if the user has exceeded the usage limit
        usage_count = await usage_collection.count_documents({"user_id": usage.user_id})

        if usage_count >= plan_exists["usage_limit"]:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Usage limit exceeded")

        # Track the API request
        await usage_collection.insert_one(usage.dict())
        return {"message": "API request tracked successfully"}

@app.get("/usage/{user_id}/limit", response_model=dict)
async def check_limit_status(user_id: str, token: str = Depends(oauth2_scheme)):
    current_user =  await check_authentication(token)
    if current_user:
        usage_collection = get_collection(USAGE_COLLECTION)
        plan_collection = get_collection(PLANS_COLLECTION)
        subscription_collection = get_collection(SUBSCRIPTIONS_COLLECTION)

        # Check if the user and plan exist
        user_exists = await subscription_collection.find_one({"user_id": user_id})
        plan_exists = await plan_collection.find_one({"name": user_exists["plan_id"]})

        if not user_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if not plan_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

        # Check if the user has exceeded the usage limit
        user_subscription = await get_user_subscription(user_id)
        usage_count = await usage_collection.count_documents({"user_id": user_id})

        return {"user_id": user_id, "usage_count": usage_count, "limit": plan_exists["usage_limit"]}