Django Social API – A Token-Based Social Networking Backend
Welcome to the Django Social API, a lightweight backend built with Django REST Framework that supports essential social networking features like user registration, login, posting, liking, unliking, sending connection requests, and even smart user recommendations — all powered with token-based authentication (Knox).

🚀 Tech Stack
Python 3.10+

Django 4.x

Django REST Framework

Knox for token authentication

SQLite 

🔐 Features Overview
Feature	Description
🧾 Register/Login	Register new users and authenticate using Knox token
📝 Create & List Posts	Users can create posts and see all posts sorted by time
❤️ Like/Unlike Posts	Like or unlike a post using its id
🤝 Connection Requests	Send, accept, and manage friend/connection requests
🌟 Recommendations	Suggest new users based on mutual connections

🛠 Setup Instructions
Clone the repository


git clone https://github.com/yourusername/django-social-api.git
cd django-social-api
Create a virtual environment and activate

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install requirements


pip install -r requirements.txt
Run migrations


python manage.py migrate
Run the server


python manage.py runserver
🔑 Authentication (Knox Token)
Use the login API to get a token, then pass it as:

Authorization: Bearer <your_token_here>
📡 API Endpoints
🔐 Authentication
Method	Endpoint	Description
POST	/api/register/	Register a new user
POST	/api/login/	Login and get token
POST	/api/logout/	Logout (invalidate)

📝 Post APIs
Method	Endpoint	Description
GET	/api/posts/	List all posts
POST	/api/posts/create/	Create a new post
POST	/api/posts/<id>/like/	Like a post
POST	/api/posts/<id>/unlike/	Unlike a post

🤝 Connections
Method	Endpoint	Description
POST	/api/connect/<user_id>/	Send connection request
GET	/api/connections/incoming/	View incoming requests
POST	/api/connections/accept/<user_id>/	Accept connection request

🌟 Recommendations
Method	Endpoint	Description
GET	/api/recommendations/	Suggested users based on mutuals

⚙️ Validations & Security
All user input is validated using Django REST Framework serializers.

API access is secured using Knox Token Authentication.

Only authenticated users can create, like, connect, or view private data.

📄 Example Usage (Thunder Client / Postman)
Register/Login and copy the token from the response.

In your request headers, set:


Authorization: Bearer <token>
Try hitting /api/posts/create/ with a body:

json

{
  "content": "Hello, this is a new post!"
}
