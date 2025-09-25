#!/bin/bash

echo "Testing registration API..."

# Test with the exact same data structure that the frontend will send
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "email": "newuser@example.com",
    "username": "newuser123",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "New",
    "last_name": "User",
    "user_type": "patient",
    "phone_number": "+256701234567"
  }'

echo -e "\n\nTesting with minimal data..."

# Test with minimal required data
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "email": "minimal@example.com",
    "username": "minimal123",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "Min",
    "last_name": "User",
    "user_type": "patient"
  }'