# Cloud Service Access Management System
#### Project Team Members : Pavana Manjunath(CWID : 885154195), Pavithra Halanayakanahalli Amaresh (CWID : 885155101), Lakshmi Poojitha Lysetti (CWID : 885155077)
# Project Description
#### 
This Titan News FastAPI-based subscription management system utilizes MongoDB for data storage. It supports user authentication, admin access control, and includes functionalities for managing subscription plans, permissions, and tracking API usage. The system enforces access restrictions based on subscription plans and monitors usage limits, providing a comprehensive solution for cloud service subscription management.
### Drive Link For the Project Demonstration
https://drive.google.com/drive/folders/1A67rQYtsYdbQItyXA1fsPuq4Lay2oRSg?usp=sharing
# Getting Started
- "pip install -r requirements.txt"
- Set up a MongoDB instance and update the MONGO_DB_URL in the code accordingly.
- Run the FastAPI application with uvicorn main:app --reload.
- Open your browser and go to http://127.0.0.1:8000 to access the FastAPI Swagger documentation.
# Endpoints
- /adminlogin: Admin login to generate a JWT token for authentication.
- /user_signup: Create a new user account.
- /user_signin: Sign in with a user account to get a JWT token.
- /plans: CRUD operations for subscription plans (admin access required).
- /permissions: CRUD operations for permissions (admin access required).
- /subscriptions: Manage user subscriptions.
- /subscriptions/{user_id}/usage: View usage statistics for a user.
- /subscriptions/{user_id}: View and modify user subscriptions.
- /access/{user_id}/{api_request}: Check access permission for a user to an API endpoint.
- /usage/{user_id}: Track API requests and enforce usage limits.
- /usage/{user_id}/limit: Check the status of the API usage limit for a user.



# Features
### User Authentication
- Admin Login: The application allows admin login with predefined credentials.
- User Signup and Signin: Users can create accounts and sign in with their credentials.
### Subscription Plan Management
- Create Plans: Admin users can create subscription plans with a name, description, permissions, and usage limit.
- Modify Plans: Admin users can modify existing subscription plans.
- Delete Plans: Admin users can delete subscription plans.
### Permission Management
- Add Permissions: Admin users can add new permissions with a name, endpoint, and description.
- Modify Permissions: Admin users can modify existing permissions.
- Delete Permissions: Admin users can delete permissions.
### User Subscription Handling
- Subscribe to Plan: Users can subscribe to a specific plan, and the application manages user subscriptions.
- View Subscription Details: Users can view details of their subscriptions, including the associated plan details.
- View Usage Statistics: Users can view the usage statistics, including the count of API requests made.
### Access Control
- Check Access Permission: The application provides an endpoint to check if a user has access permission for a specific API request.
### Usage Tracking and Limit Enforcement
- Track API Requests: The application tracks API requests made by users and enforces usage limits specified in subscription plans.
- Check Limit Status: Users can check the status of their usage limits.
