from fastapi import APIRouter, HTTPException
from app.services.health_service import HealthService

router = APIRouter()
health_service = HealthService()

@router.post("/health")
async def receive_health_data(data: dict):
    print("Received Health Data:", data)  # 로깅 추가
    try:
        result = await health_service.save_health_data(data)
        return {"status": "success", "data": result}
    except Exception as e:
        print("Error saving health data:", e)  # 에러 로깅
        raise HTTPException(status_code=500, detail=str(e))
