---
title: Todo App Chatbot API
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# Todo App Chatbot - Backend API

FastAPI backend for AI-powered Todo management chatbot.

## Features

- 🤖 AI Chatbot with Gemini API
- ✅ Task management (add, list, complete, delete, search)
- 🔐 JWT Authentication
- 💬 Conversation persistence
- 🌐 Bilingual support (English + Roman Urdu)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/{user_id}/chat` | Send message to AI |
| GET | `/api/{user_id}/conversations` | List conversations |
| GET | `/api/{user_id}/conversations/{id}/messages` | Get messages |
| GET | `/api/{user_id}/tasks` | List tasks |
| POST | `/api/{user_id}/tasks` | Create task |

## Environment Variables

Set these in Hugging Face Space Settings:

- `GEMINI_API_KEY` - Google Gemini API key
- `DATABASE_URL` - PostgreSQL connection string
- `BETTER_AUTH_SECRET` - JWT secret
- `FRONTEND_URL` - Frontend URL for CORS

## Documentation

Visit `/docs` for interactive API documentation.
