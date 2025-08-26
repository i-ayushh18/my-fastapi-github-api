# My FastAPI GitHub API

This project is a FastAPI-based API for interacting with GitHub data, designed for deployment on Vercel.

## Features
- Fetch organization and repository data from GitHub
- Get user information and repositories
- Health check endpoint

## Deployment
This project is ready to deploy on Vercel. See `vercel.json` for configuration.

## API Endpoints

### 1. Health Check
- **GET** `/api/health`
- **Example:**
  - `https://my-fastapi-github-api.vercel.app/api/health`

---

### 2. Get GitHub Data (for an org and repo)
- **GET** `/api/github-data`
- **Query Parameters:**
  - `org` (optional, default: `microsoft`)
  - `repo` (optional, default: `vscode`)
- **Example:**
  - `https://my-fastapi-github-api.vercel.app/api/github-data?org=microsoft&repo=vscode`

---

### 3. Get GitHub User (basic info)
- **GET** `/api/github/user?username=USERNAME`
- **Example:**
  - `https://my-fastapi-github-api.vercel.app/api/github/user?username=octocat`

---

### 4. Get User Repositories (detailed)
- **GET** `/api/github/user/{username}/repositories`
- **Example:**
  - `https://my-fastapi-github-api.vercel.app/api/github/user/octocat/repositories`

---

### 5. Get User Repository (detailed)
- **GET** `/api/github/user/{username}/repository/{repo_name}`
- **Example:**
  - `https://my-fastapi-github-api.vercel.app/api/github/user/octocat/repository/Hello-World`

---

## Usage
- Replace `octocat` and other placeholders with the actual GitHub username or repository name you want to query.
- You can use these endpoints in your browser, with `curl`, or in tools like Postman.

## Environment Variables
- `GITHUB_TOKEN` (optional, but recommended for higher rate limits)

