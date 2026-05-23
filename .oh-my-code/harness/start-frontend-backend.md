# Harness Graph: start-frontend-backend

> Status: in_progress

## User Intent
- Original: 启动前后端工程
- Acceptance: Identify frontend/backend start commands in `/Users/bytedance/Documents/workplace_self/WeWin`, launch both services, and report access URLs/PIDs or clear blockers.

## Assurance
- Mode: best_effort
- Why: User requested local service startup; verification is limited to process/log/port checks.

## Gates
### g1 services-started
- Status: pending
- Acceptance: Backend and frontend processes are running or a concrete startup blocker is reported.
- Repair: 0/2

## Understanding
- Pending initial discovery.

## Completed

## Pending
### n1 @omc-explore — discover-start-commands
- Goal: Discover repo structure and exact frontend/backend startup commands.
- Acceptance: Report directories, commands, dependency prerequisites, ports, env needs.
### n2 @omc-executor — depends:n1 — launch-services
- Goal: Launch backend and frontend with discovered commands.
- Acceptance: Long-running processes started; report PIDs/log files/ports or blocker.
### n3 @omc-verifier — depends:n2 — gate:g1
- Goal: Verify services are alive.
- Acceptance: Evidence from logs, process list, port checks, or HTTP health checks.
