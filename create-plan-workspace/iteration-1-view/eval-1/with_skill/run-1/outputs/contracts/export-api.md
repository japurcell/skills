# Export API Contract

## Overview

REST API for requesting, managing, and downloading audit log exports.

## Endpoints

### POST /api/exports
Create a new export job.

**Headers**: Authorization: Bearer {token}  
**Body**: ExportRequest  
**Response**: 201 Created  
**Payload**: ExportJobResponse  

### GET /api/exports/{job_id}
Fetch export job status.

**Headers**: Authorization: Bearer {token}  
**Response**: 200 OK  
**Payload**: ExportJobResponse  

### POST /api/exports/{job_id}/cancel
Cancel a pending/running export.

**Headers**: Authorization: Bearer {token}  
**Response**: 200 OK  
**Payload**: ExportJobResponse  

## Schemas
