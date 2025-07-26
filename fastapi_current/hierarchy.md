project/
│
├── app.py           # Main Flask app
├── config.py        # MySQL config
├── models.py        # SQLAlchemy models
├── routes/
│   ├── auth.py      # User register/login
│   ├── agent.py     # Agent register/heartbeat
│   ├── command.py   # Send commands
└── websocket/
    └── server.py    # Real-time command execution via WebSocket
Ansible api folder is empty 
Create API endpoint which has long commands 