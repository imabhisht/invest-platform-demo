#!/bin/bash

# Install Python Packages
pip install -r requirements.txt

# Start Docker Compose
docker-compose up -d


# Start the application
streamlit run app.py
