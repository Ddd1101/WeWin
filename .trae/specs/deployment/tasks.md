
# WeWin Deployment - The Implementation Plan (Decomposed and Prioritized Task List)

## [ ] Task 1: Install and configure nginx
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - Install nginx on Ubuntu 20.04
  - Create nginx configuration file for serving Page (frontend) on port 8080
  - Enable and start nginx
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-1.1: Verify nginx is installed and running
  - `programmatic` TR-1.2: Verify nginx configuration is valid (nginx -t)
  - `programmatic` TR-1.3: Verify nginx is listening on port 8080
- **Notes**: Frontend will be built in Task 2.

## [ ] Task 2: Build frontend (Page)
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - Install npm dependencies in Page directory
  - Build production version of frontend using vite with memory limit (max 1GB)
- **Acceptance Criteria Addressed**: [AC-1, AC-3, NFR-3]
- **Test Requirements**:
  - `programmatic` TR-2.1: Verify npm install completes successfully
  - `programmatic` TR-2.2: Verify npm run build completes and creates dist directory
  - `programmatic` TR-2.3: Verify build process memory usage does not exceed 1GB
- **Notes**: After building, the dist directory will be served by nginx. Use NODE_OPTIONS="--max-old-space-size=1024" to limit Node.js memory to 1GB.

## [ ] Task 3: Deploy and start backend (Server)
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - Set up Python virtual environment in Server directory
  - Install Python dependencies (including gunicorn)
  - Run database migrations
  - Start gunicorn server on 0.0.0.0:8003 (external access)
- **Acceptance Criteria Addressed**: [AC-2, AC-3]
- **Test Requirements**:
  - `programmatic` TR-3.1: Verify virtual environment is created successfully
  - `programmatic` TR-3.2: Verify pip install requirements completes successfully
  - `programmatic` TR-3.3: Verify database migrations run without errors
  - `programmatic` TR-3.4: Verify gunicorn is running and listening on 0.0.0.0:8003
- **Notes**: Need to ensure gunicorn runs in background and persists (using systemd or nohup).

## [ ] Task 4: Verify frontend and backend communication
- **Priority**: P0
- **Depends On**: [Task 1, Task 2, Task 3]
- **Description**: 
  - Test frontend access from external network
  - Test backend API access from external network
  - Verify frontend API calls work with backend
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3]
- **Test Requirements**:
  - `programmatic` TR-4.1: Test accessing frontend on port 8080
  - `programmatic` TR-4.2: Test backend API endpoints
  - `human-judgement` TR-4.3: Verify frontend pages load and interact with backend
- **Notes**: Ensure no CORS issues.
