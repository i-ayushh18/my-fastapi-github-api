#!/usr/bin/env python3
"""
GitHub API
This is a Python API that fetches GitHub data for any organization.
You can integrate this with your existing Python API infrastructure.
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import logging
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="GitHub API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_BASE = "https://api.github.com"
ORGANIZATION = "github"  # Default organization

# Team structure configuration
ADMIN = "admin"  # Admin user
TEAM_LEADS = ["user1", "user2"]  # Team leads
INTERNS = ["intern1", "intern2", "intern3"]  # Intern users

# Pydantic models
class GitHubCommit(BaseModel):
    id: str
    message: str
    author: str
    date: str
    repository: str
    url: str

class GitHubPullRequest(BaseModel):
    id: str
    title: str
    author: str
    status: str
    repository: str
    url: str
    createdAt: str
    updatedAt: str

class GitHubIssue(BaseModel):
    id: str
    title: str
    author: str
    status: str
    priority: str
    repository: str
    url: str
    createdAt: str
    updatedAt: str

class GitHubRepository(BaseModel):
    name: str
    description: str
    language: str
    stars: int
    forks: int
    url: str
    lastUpdated: str

class GitHubStats(BaseModel):
    totalCommits: int
    totalPRs: int
    totalIssues: int
    activeContributors: int
    repositoriesCount: int

class GitHubData(BaseModel):
    commits: List[GitHubCommit]
    pullRequests: List[GitHubPullRequest]
    issues: List[GitHubIssue]
    repositories: List[GitHubRepository]
    stats: GitHubStats

class GitHubResponse(BaseModel):
    success: bool
    organization: str
    admin: str
    teamLeads: List[str]
    interns: List[str]
    data: GitHubData

def get_github_headers():
    """Get headers for GitHub API requests"""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-API"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers

def fetch_organization_repos() -> List[Dict]:
    """Fetch repositories for the user account"""
    try:
        url = f"{GITHUB_API_BASE}/users/{ORGANIZATION}/repos"
        response = requests.get(url, headers=get_github_headers())
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching repositories: {e}")
        return []

def fetch_commits(repo_name: str, since_date: str) -> List[Dict]:
    """Fetch commits for a specific repository"""
    try:
        url = f"{GITHUB_API_BASE}/repos/{ORGANIZATION}/{repo_name}/commits"
        params = {
            "since": since_date,
            "per_page": 100
        }
        response = requests.get(url, headers=get_github_headers(), params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching commits for {repo_name}: {e}")
        return []

def fetch_pull_requests(repo_name: str) -> List[Dict]:
    """Fetch pull requests for a specific repository"""
    try:
        url = f"{GITHUB_API_BASE}/repos/{ORGANIZATION}/{repo_name}/pulls"
        params = {
            "state": "all",
            "per_page": 100
        }
        response = requests.get(url, headers=get_github_headers(), params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching pull requests for {repo_name}: {e}")
        return []

def fetch_issues(repo_name: str) -> List[Dict]:
    """Fetch issues for a specific repository"""
    try:
        url = f"{GITHUB_API_BASE}/repos/{ORGANIZATION}/{repo_name}/issues"
        params = {
            "state": "all",
            "per_page": 100
        }
        response = requests.get(url, headers=get_github_headers(), params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching issues for {repo_name}: {e}")
        return []

def get_team_members() -> List[str]:
    """Get all team members (admin, team leads, interns)"""
    return [ADMIN] + TEAM_LEADS + INTERNS

@app.get("/api/github-data")
async def get_github_data(org: str = "microsoft", repo: str = "vscode"):
    """Get GitHub data for any organization and repository"""
    if not GITHUB_TOKEN:
        return {"error": "GitHub token not configured"}
    
    try:
        # Get organization data
        org_data = await get_organization_data(org)
        
        # Get specific repository data
        repo_data = await get_repository_data(org, repo)
        
        # Get commits from the specific repository
        commits_data = await get_repository_commits(org, repo)
        
        # Get pull requests from the specific repository
        prs_data = await get_repository_pull_requests(org, repo)
        
        # Get issues from the specific repository
        issues_data = await get_repository_issues(org, repo)
        
        return {
            "organization": org_data,
            "repository": repo_data,
            "commits": commits_data,
            "pullRequests": prs_data,
            "issues": issues_data,
            "stats": {
                "totalCommits": len(commits_data),
                "totalPRs": len(prs_data),
                "totalIssues": len(issues_data),
                "activeContributors": len(set([commit["author"] for commit in commits_data])),
                "repositoriesCount": 1
            }
        }
    except Exception as e:
        return {"error": str(e)}

async def get_organization_data(organization: str):
    """Get organization information"""
    url = f"{GITHUB_API_BASE}/orgs/{organization}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return {"name": organization, "description": f"{organization} Organization"}

async def get_repository_data(organization: str, repo_name: str):
    """Get specific repository information"""
    url = f"{GITHUB_API_BASE}/repos/{organization}/{repo_name}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            repo = response.json()
            return {
                "name": repo["name"],
                "description": repo.get("description", ""),
                "language": repo.get("language", "Unknown"),
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "url": repo["html_url"],
                "lastUpdated": repo["updated_at"]
            }
        return {"name": repo_name, "description": "Repository not found"}

async def get_repository_commits(organization: str, repo_name: str):
    """Get commits from specific repository with detailed information"""
    url = f"{GITHUB_API_BASE}/repos/{organization}/{repo_name}/commits"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            commits = response.json()
            detailed_commits = []
            
            for commit in commits[:10]:  # Limit to 10 most recent commits
                # Get detailed commit information
                commit_detail_url = f"{GITHUB_API_BASE}/repos/{organization}/{repo_name}/commits/{commit['sha']}"
                detail_response = await client.get(commit_detail_url, headers=headers)
                
                if detail_response.status_code == 200:
                    commit_detail = detail_response.json()
                    detailed_commits.append({
                        "id": commit["sha"][:7],
                        "message": commit["commit"]["message"],
                        "author": commit["commit"]["author"]["name"],
                        "date": commit["commit"]["author"]["date"],
                        "repository": repo_name,
                        "url": commit["html_url"],
                        "description": commit["commit"]["message"],
                        "files_changed": len(commit_detail.get("files", [])),
                        "additions": sum(file.get("additions", 0) for file in commit_detail.get("files", [])),
                        "deletions": sum(file.get("deletions", 0) for file in commit_detail.get("files", [])),
                        "commit_url": commit["html_url"],
                        "author_avatar": commit["author"]["avatar_url"] if commit.get("author") else None,
                    })
                else:
                    # Fallback to basic commit info
                    detailed_commits.append({
                        "id": commit["sha"][:7],
                        "message": commit["commit"]["message"],
                        "author": commit["commit"]["author"]["name"],
                        "date": commit["commit"]["author"]["date"],
                        "repository": repo_name,
                        "url": commit["html_url"],
                        "description": commit["commit"]["message"],
                        "files_changed": 0,
                        "additions": 0,
                        "deletions": 0,
                        "commit_url": commit["html_url"],
                        "author_avatar": commit["author"]["avatar_url"] if commit.get("author") else None,
                    })
            
            return detailed_commits
        return []

async def get_repository_pull_requests(organization: str, repo_name: str):
    """Get pull requests from specific repository with detailed information"""
    url = f"{GITHUB_API_BASE}/repos/{organization}/{repo_name}/pulls"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            prs = response.json()
            detailed_prs = []
            
            for pr in prs[:10]:  # Limit to 10 most recent PRs
                detailed_prs.append({
                    "id": str(pr["number"]),
                    "title": pr["title"],
                    "author": pr["user"]["login"],
                    "status": pr["state"],
                    "repository": repo_name,
                    "url": pr["html_url"],
                    "createdAt": pr["created_at"],
                    "updatedAt": pr["updated_at"],
                    "description": pr.get("body", ""),
                    "labels": [label["name"] for label in pr.get("labels", [])],
                    "assignees": [assignee["login"] for assignee in pr.get("assignees", [])],
                    "reviewers": [reviewer["login"] for reviewer in pr.get("requested_reviewers", [])],
                    "comments": pr.get("comments", 0),
                    "commits": pr.get("commits", 0),
                    "additions": pr.get("additions", 0),
                    "deletions": pr.get("deletions", 0),
                    "changed_files": pr.get("changed_files", 0),
                    "author_avatar": pr["user"]["avatar_url"],
                    "draft": pr.get("draft", False),
                    "merged": pr.get("merged", False),
                    "mergeable": pr.get("mergeable"),
                })
            
            return detailed_prs
        return []

async def get_repository_issues(organization: str, repo_name: str):
    """Get issues from specific repository with detailed information"""
    url = f"{GITHUB_API_BASE}/repos/{organization}/{repo_name}/issues"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            issues = response.json()
            detailed_issues = []
            
            for issue in issues[:10]:  # Limit to 10 most recent issues
                # Skip pull requests (they appear in issues endpoint too)
                if "pull_request" not in issue:
                    # Determine priority based on labels
                    priority = "medium"
                    if any("high" in label["name"].lower() for label in issue.get("labels", [])):
                        priority = "high"
                    elif any("low" in label["name"].lower() for label in issue.get("labels", [])):
                        priority = "low"
                    
                    detailed_issues.append({
                        "id": str(issue["number"]),
                        "title": issue["title"],
                        "author": issue["user"]["login"],
                        "status": issue["state"],
                        "priority": priority,
                        "repository": repo_name,
                        "url": issue["html_url"],
                        "createdAt": issue["created_at"],
                        "updatedAt": issue["updated_at"],
                        "description": issue.get("body", ""),
                        "labels": [label["name"] for label in issue.get("labels", [])],
                        "assignees": [assignee["login"] for assignee in issue.get("assignees", [])],
                        "comments": issue.get("comments", 0),
                        "author_avatar": issue["user"]["avatar_url"],
                        "milestone": issue.get("milestone", {}).get("title") if issue.get("milestone") else None,
                        "locked": issue.get("locked", False),
                        "closed_at": issue.get("closed_at"),
                        "reactions": {
                            "total_count": issue.get("reactions", {}).get("total_count", 0),
                            "thumbs_up": issue.get("reactions", {}).get("+1", 0),
                            "thumbs_down": issue.get("reactions", {}).get("-1", 0),
                            "laugh": issue.get("reactions", {}).get("laugh", 0),
                            "hooray": issue.get("reactions", {}).get("hooray", 0),
                            "confused": issue.get("reactions", {}).get("confused", 0),
                            "heart": issue.get("reactions", {}).get("heart", 0),
                        }
                    })
            
            return detailed_issues
        return []

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/github/user")
async def get_github_user(username: str):
    """Get GitHub user data and all their repositories"""
    if not GITHUB_TOKEN:
        return {"error": "GitHub token not configured"}
    
    try:
        # Get user data
        user_data = await get_user_data(username)
        
        # Get all repositories for the user
        repositories_data = await get_user_repositories(username)
        
        return {
            "user": user_data,
            "repositories": repositories_data,
        }
    except Exception as e:
        return {"error": str(e)}

async def get_user_data(username: str):
    """Get GitHub user information"""
    url = f"{GITHUB_API_BASE}/users/{username}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            user = response.json()
            return {
                "username": user["login"],
                "name": user.get("name"),
                "avatar_url": user.get("avatar_url"),
                "bio": user.get("bio"),
                "public_repos": user.get("public_repos", 0),
                "followers": user.get("followers", 0),
                "following": user.get("following", 0),
            }
        return {"username": username, "name": username}

async def get_user_repositories(username: str):
    """Get all repositories for a user (including private ones the token has access to)"""
    # Use /user/repos to get all repositories the authenticated user has access to
    # This includes private repositories where the token owner is a collaborator
    url = f"{GITHUB_API_BASE}/user/repos"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            all_repos = response.json()
            
            # Filter repositories that belong to the requested username
            user_repos = [
                {
                    "id": repo["id"],
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo.get("description", ""),
                    "language": repo.get("language", "Unknown"),
                    "stargazers_count": repo["stargazers_count"],
                    "forks_count": repo["forks_count"],
                    "updated_at": repo["updated_at"],
                    "html_url": repo["html_url"],
                    "private": repo["private"],
                    "fork": repo["fork"],
                }
                for repo in all_repos
                if repo["owner"]["login"] == username
            ]
            
            return user_repos
        return []

@app.get("/api/github/user/{username}/repositories")
async def get_user_repositories_detailed(username: str):
    """Get detailed GitHub data for any user's repositories (including private)"""
    if not GITHUB_TOKEN:
        return {"error": "GitHub token not configured"}
    
    try:
        # Get user data
        user_data = await get_user_data(username)
        
        # Get all repositories for the user
        repositories_data = await get_user_repositories(username)
        
        # Get detailed data for each repository
        detailed_data = {
            "user": user_data,
            "repositories": repositories_data,
            "total_repos": len(repositories_data),
            "private_repos": len([repo for repo in repositories_data if repo["private"]]),
            "public_repos": len([repo for repo in repositories_data if not repo["private"]]),
            "languages": list(set([repo["language"] for repo in repositories_data if repo["language"] != "Unknown"])),
            "total_stars": sum([repo["stargazers_count"] for repo in repositories_data]),
            "total_forks": sum([repo["forks_count"] for repo in repositories_data]),
        }
        
        return detailed_data
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/github/user/{username}/repository/{repo_name}")
async def get_user_repository_detailed(username: str, repo_name: str):
    """Get detailed data for a specific repository of any user"""
    if not GITHUB_TOKEN:
        return {"error": "GitHub token not configured"}
    
    try:
        # Get repository data
        repo_data = await get_repository_data(username, repo_name)
        
        # Get commits from the repository
        commits_data = await get_repository_commits(username, repo_name)
        
        # Get pull requests from the repository
        prs_data = await get_repository_pull_requests(username, repo_name)
        
        # Get issues from the repository
        issues_data = await get_repository_issues(username, repo_name)
        
        return {
            "repository": repo_data,
            "commits": commits_data,
            "pullRequests": prs_data,
            "issues": issues_data,
            "stats": {
                "totalCommits": len(commits_data),
                "totalPRs": len(prs_data),
                "totalIssues": len(issues_data),
                "activeContributors": len(set([commit["author"] for commit in commits_data])),
            }
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 