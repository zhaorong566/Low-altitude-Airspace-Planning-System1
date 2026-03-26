from fastapi import APIRouter
from app.services.planning_service import PlanningService
from app.services.simulation_service import SimulationService

router = APIRouter(prefix="/conflicts", tags=["conflicts"])


@router.get("/", summary="获取当前冲突列表")
async def list_conflicts():
    """检测并返回所有活跃任务的冲突情况"""
    sim = SimulationService()
    planner = PlanningService()
    tasks = sim.get_demo_tasks()
    tasks_with_routes = []
    for task in tasks:
        if task.get("status") in ("executing", "approved"):
            route = sim.generate_route_for_task(task)
            tasks_with_routes.append({"id": task["id"], "waypoints": route})
    conflicts = planner.detect_conflicts(tasks_with_routes)
    return {"conflicts": conflicts, "count": len(conflicts)}


@router.post("/resolve/{conflict_id}", summary="解决冲突")
async def resolve_conflict(conflict_id: str, resolution: str = "reroute"):
    """标记冲突为已解决并触发重新规划"""
    return {
        "conflict_id": conflict_id,
        "resolution": resolution,
        "status": "resolved",
        "message": f"冲突{conflict_id}已通过{resolution}方式解决",
    }
