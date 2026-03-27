# Contract: Release Calendar Events

## Overview

The Release Calendar system publishes events to a notification service queue whenever a significant action occurs. Consumers subscribe to these events to send notifications, update downstream systems, or audit.

## Event Bus Interface

Events are published to a message queue (e.g., Redis, RabbitMQ, AWS SQS) with the following contract.

**Queue name**: `release-calendar-events`  
**Format**: JSON  
**Guarantees**: At-least-once delivery (consuming system must be idempotent)

---

## Event Types

### 1. ReleaseWindowStateChanged

**Triggered**: When a release window transitions between states (draft → proposed → approved, etc.)

**Event Structure**:
