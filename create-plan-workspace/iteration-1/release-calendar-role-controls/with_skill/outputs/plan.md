# Implementation Plan: Release Calendar Role Controls

**Date**: March 26, 2026 | **Spec**: /home/adam/.agents/skills/create-plan-workspace/iteration-1/inputs/spec-release-calendar-roles.md

## Summary

Add role-based permissions and approval workflow to release planning calendar. Implement three roles (viewer, editor, release_manager) with state-based access control, supporting state transitions (draft → proposed → approved/blocked → cancelled) with audit trails. Integrate with notification service for approval/rejection events.

## Technical Context

**Language/Version**: Node.js (backend), Next.js (frontend)  
**Primary Dependencies**: Node.js runtime, Next.js framework, notification service  
**Storage**: PostgreSQL (existing infrastructure in monorepo)  
**Testing**: Jest (unit), Playwright (e2e)  
**Target Platform**: Web application (monorepo: Node backend + Next.js frontend)  
**Project Type**: Web service with role-based access control  
**Performance Goals**: <150ms perceived latency for calendar UI; 300 concurrent users during planning week  
**Constraints**: Backward-compatible API for one quarter; existing test stack (Jest, Playwright)  
**Scale/Scope**: Calendar feature scope; assumes existing user/auth system

## AGENTS.md Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

**Status**: PASS  
- Node.js backend: express/fastify patterns supported
- Next.js frontend: API routes and middleware supported  
- Role-based access: Standard auth middleware pattern
- Notification service: External integration verified

## Project Structure

### Documentation (this feature)
