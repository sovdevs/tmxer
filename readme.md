# to call
uvicorn main:app --reload --port 8001

# HTTP Client
http://127.0.0.1:8001/tmxs/
Multipart
file TMX
Query
clientId any UUID (not implemented)
categories ?

# what does it do?
parses TMX to tables

# Next
association table Segment Category Fix
DB to TMX based on category/categories

# 