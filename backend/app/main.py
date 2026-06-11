from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import history, matches, optimize

app = FastAPI(
    title="Odds Optimizer",
    description="竞彩赔率优化器 - 最优盈亏比投注方案",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matches.router, prefix="/api/matches", tags=["matches"])
app.include_router(optimize.router, prefix="/api/optimize", tags=["optimize"])
app.include_router(history.router, prefix="/api/history", tags=["history"])


@app.get("/")
async def root():
    return {"message": "Odds Optimizer API", "docs": "/docs"}
