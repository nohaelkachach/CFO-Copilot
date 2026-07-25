from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from routers import all_routers
from db.database import create_tables
# Initialize the FastAPI application
app = FastAPI(
    title="CFO Copilot",
    description="AI-powered financial intelligence platform for SMEs",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI — visit http://localhost:8080/docs to test your API
    redoc_url="/redoc"      # Alternative API docs
)

# CORS middleware — allows the React frontend (running on a different port)
# to communicate with this backend without being blocked by the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins= settings.ALLOWED_ORIGINS,  # React dev server — change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],    # Allow GET, POST, PUT, DELETE etc.
    allow_headers=["*"],    # Allow all headers
)

# Register all routers in one loop instead of one line per router
for router in all_routers:
    app.include_router(router)

# Health check endpoint — useful to confirm the server is running
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.on_event("startup")
def startup():
    create_tables()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
    # reload=True means the server restarts automatically when you save a file
    # host="0.0.0.0" makes it accessible from any network interface