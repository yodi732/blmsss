OpenNAMU Render-ready package
============================

This package was auto-generated to allow immediate deployment to Render.com.

How to use
1. Upload the repository contents to a new empty GitHub repo (or push this zip's content).
2. Create a new Web Service on Render, connect the GitHub repo.
3. Set Environment Variables in Render > Settings > Environment:
   - NAMU_DB_TYPE = sqlite
   - NAMU_DB = data
   - NAMU_HOST = 0.0.0.0
   - NAMU_PORT = 5000
   - NAMU_DEBUG = 0
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `python app.py`  (or `hypercorn app:app --bind 0.0.0.0:5000`)

Notes
- The route/ folder is included. If the real opennamu route package is larger, replace it with your route folder.
- If your repository already contains the full engine, merge `app.py` and `func.py` into that repo instead.
- This package contains safety fallbacks to avoid Golang or interactive prompts during Render deployment.
