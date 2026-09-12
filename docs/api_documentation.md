# Navigators Cloud API

The Navigators Cloud Backend is a FastAPI service that manages session synchronization, telemetry aggregation, and OTA model distribution.

## Endpoints

### Authentication
`POST /auth/token`
Generates a Bearer JWT for device authentication.
- **Parameters**: `device_id` (string)
- **Returns**: `{"access_token": "...", "token_type": "bearer"}`

### Telemetry & Sync
`POST /telemetry/batch`
Receives offline telemetry batches from edge devices.
- **Headers**: `Authorization: Bearer <token>`
- **Body**: JSON Array of `TelemetryPoint` objects (max 1000 per batch).
- **Behavior**: Validates payload, stores in SQLite `navigators_cloud.db`, and broadcasts via WebSockets to live dashboard viewers. 

`GET /telemetry/live` (WebSocket)
Streams real-time telemetry batches for active sessions.

### Session Management
`GET /sessions`
Lists all recorded field test sessions.

`GET /sessions/{session_id}/report`
Reconstructs and returns the full trajectory and statistics for a given session.

### OTA Updates
`GET /models/latest`
Returns the metadata for the currently active AI speed estimation model.
- **Returns**: `{"version": "vX.X", "url": "...", "checksum": "..."}`
