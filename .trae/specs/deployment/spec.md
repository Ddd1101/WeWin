
# WeWin Deployment - Product Requirement Document

## Overview
- **Summary**: Deploy WeWin frontend and backend projects on a Ubuntu 20.04 server, with frontend served via nginx on port 8080 and backend served on port 8003, making them accessible from external networks.
- **Purpose**: Make the WeWin application available for external users to access and use.
- **Target Users**: End users accessing the WeWin store management system.

## Goals
- Deploy Page (frontend) on nginx port 8080
- Deploy Server (backend) on port 8003
- Ensure external accessibility

## Non-Goals (Out of Scope)
- Setting up SSL/TLS certificates (HTTPS)
- Domain name configuration
- Database backup/restore
- Performance optimization beyond basic deployment

## Background & Context
- WeWin is a store management system with frontend (Vue 3 + Vite) and backend (Django)
- Server OS is Ubuntu 20.04 LTS
- Project directories: /root/workplace_shop/WeWin/Page (frontend) and /root/workplace_shop/WeWin/Server (backend)

## Functional Requirements
- **FR-1**: Frontend is accessible from external networks via port 8080
- **FR-2**: Backend API is accessible from external networks via port 8003
- **FR-3**: Frontend can communicate with backend APIs

## Non-Functional Requirements
- **NFR-1**: Services should run in the background and persist after server reboot
- **NFR-2**: Basic error logging should be available
- **NFR-3**: Resource usage limitation - frontend compilation must use no more than 1GB memory

## Constraints
- **Technical**: Must use nginx for frontend, gunicorn for backend
- **Business**: Deployment must be completed on current server

## Assumptions
- Server has internet access to install packages and dependencies
- Current user has sudo privileges
- Ports 8080 and 8003 are not already in use by other services

## Acceptance Criteria

### AC-1: Frontend Accessible on Port 8080
- **Given**: Frontend has been built and nginx is configured
- **When**: User accesses http://&lt;server-ip&gt;:8080 from external network
- **Then**: Frontend loads successfully
- **Verification**: `programmatic`

### AC-2: Backend Accessible on Port 8003
- **Given**: Backend is running with gunicorn on 0.0.0.0:8003
- **When**: User sends request to http://&lt;server-ip&gt;:8003 from external network
- **Then**: Backend responds successfully
- **Verification**: `programmatic`

### AC-3: Frontend Can Communicate with Backend
- **Given**: Both frontend and backend are running
- **When**: Frontend makes API calls to backend
- **Then**: API calls succeed and data is properly exchanged
- **Verification**: `human-judgment`

## Open Questions
- None
