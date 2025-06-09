from fastapi import HTTPException, status
from app.models.focus_analysis import FocusAnalysis
# ...기존 import 유지...

@router.get("/user/{user_id}/focus-pattern", response_model=FocusAnalysis)
async def get_user_focus_pattern(
    user_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db = Depends(get_db)
):
    """사용자의 집중도 패턴을 조회합니다."""
    # ...기존 코드...
    
    # 데이터가 없는 경우 예외 발생 대신 빈 데이터 반환
    if not metrics or metrics_count == 0:
        logger.warning(f"[focus-pattern] 데이터 없음: user_id={user_id}")
        
        # 빈 데이터로 응답 구성
        return {
            "daily_average": 0.0,
            "weekly_trend": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "peak_hours": [],
            "improvement_areas": ["아직 데이터가 없습니다. 활동을 기록해보세요."]
        }
    
    # ...기존 코드 계속...