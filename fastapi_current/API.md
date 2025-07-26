✅ REST API Endpoints
1. Register Agent
http

POST /api/agent/register
Body: { "name": "agent1" }
Response: { "agent_id": "uuid", "token": "secure_token" }
2. Send Command
http

POST /api/command
Body: { "agent_id": "uuid", "command": "ls -la" }
Response: { "status": "pending" }
3. Agent Heartbeat
http

POST /api/agent/heartbeat
Headers: { "Authorization": "Bearer <token>" }
Body: { "status": "active" }

✅ Agent Management APIs
1. Register Agent


POST /api/agent/register
Body: { "name": "agent1" }
Response: { "agent_id": "UUID", "token": "secure_token" }
2. Agent Heartbeat (Keep alive)


POST /api/agent/heartbeat
Headers: Authorization: Bearer <token>
Body: { "status": "active" }
Response: { "status": "ok" }
3. Get Agent List (Admin)
pgsql

GET /api/agents	
Headers: Authorization: Bearer <admin-token>
Response: [ { "agent_id": "...", "status": "active" } ]
________________________________________
✅ Command Execution APIs
4. Send Command to Agent


POST /api/command
Headers: Authorization: Bearer <admin-token>
Body: { "agent_id": "UUID", "command": "ls -la" }
Response: { "command_id": 101, "status": "queued" }
5. Get Command Status
pgsql

GET /api/command/<command_id>
Headers: Authorization: Bearer <admin-token>
Response: { "status": "completed", "output": "file list..." }
________________________________________
✅ User Management APIs
6. Register User


POST /api/user/register
Body: { "username": "john", "password": "secret" }
Response: { "status": "created" }
7. Login User


POST /api/user/login
Body: { "username": "john", "password": "secret" }
Response: { "token": "jwt_token_here" }

