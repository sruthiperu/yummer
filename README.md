# Yummers

A website that recommends recipes based on the ingredients users have on hand and allows them to customize recipes using AI.

## Live Site
https://yummers-lemon.vercel.app/

## Building from the code

### Prerequisites

Make sure the following are installed:
* Python 3.11+
* Docker
* Node.js, npm

### 1. Clone the repository

```
git clone https://github.com/sruthiperu/yummers.git
```

### 2. Start PostgreSQL

Navigate to the project directory:
```
cd yummers
```

Start the PostgreSQL database with Docker Compose:
```
docker compose up db -d
```

If port 5432 is already in use, stop PostgreSQL first:
```
brew services stop postgresql
```
Then start the database again:
```
docker compose up db -d
```

### 3. Set up the backend
Navigate to the backend directory:
```
cd backend
```

Create and activate a virtual environment:
```
python3.11 -m venv .venv
```
```
source .venv/bin/activate
```

Install the backend dependencies
```
pip install -r requirements.txt
```

Create your local environment file:
```
cp .env.example .env
```

Fill in the required values in backend/.env:
```
DATABASE_URL=postgresql://recipeapp:recipeapp@127.0.0.1:5432/recipeapp
OPENAI_API_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
JWT_SECRET=
```

### 4. Run database migrations

From the backend directory:
```
cd backend
```

Run the migrations:
```
alembic upgrade head
```

### 5. Set up the frontend

In a new terminal, navigate to the frontend repository:
```
cd frontend
```

Install the frontend dependencies:
```
npm install
```

Create the local frontend environment file:
```
cp .env.example .env.local
```

The default local API URL is:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

Start the Next.js development server:
```
npm run dev
```

The frontend will be at:
```
http://localhost:3000
```

### 6. Google OAuth

For local Google login, configure the Google OAuth application with this redirect URI:
```
http://localhost:8000/api/v1/auth/callback/google
```

The corresponding credentials should be placed in backend/.env:
```
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

### 7. Running the app daily

Terminal 1: Backend
```
cd backend
```
```
source .venv/bin/activate
```
```
uvicorn app.main:app --reload --port 8000
```

The API will be at:
```
http://localhost:8000
```

Terminal 2: Frontend
```
cd frontend
```
```
npm run dev
```
Open:
```
http://localhost:3000
```

Database
If PostgreSQL is not already running:
```
docker compose up db -d
```

### 8. Populate the recipe database

The live app contains over 225,000 recipes. The recipe dataset and PostgreSQL database dump are not included in this repository because of their large file sizes.

To populate the database locally, I would recommend using a publicly available recipe dataset. For example, you can use a recipe dataset from Kaggle (like I did) or another free data source.

The repository includes an import_recipes.py script for importing recipe data into PostgreSQL.

Before running import_recipes.py, be sure to update the csv path on line 133 to point to the location of your downloaded dataset.

### 9. Environment files

Example environment files
* backend/.env.example
* frontend/.env.example

Do not commit .env or any other file containing secrets.

## Contributions
Contributions and suggestions for improvement are always welcome!

## Thanks for stopping by!
