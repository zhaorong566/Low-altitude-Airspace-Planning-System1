from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.route import PlanningRequest, RouteResponse
from app.services.planning_service import PlanningService

router = APIRouter(prefix="/planning", tags=["planning"])
planning_service = PlanningService()


@router.post("/plan", summary="规划单条航路")
async def plan_route(request: PlanningRequest, background_tasks: BackgroundTasks):
    """为指定任务规划最优飞行路径"""
    try:
        task = await _get_task_info(str(request.task_id))
        result = await planning_service.plan_route(
            task_id=str(request.task_id),
            origin=(task["origin"]["lat"], task["origin"]["lon"], task["origin"]["alt"]),
            destination=(task["destination"]["lat"], task["destination"]["lon"], task["destination"]["alt"]),
            max_altitude=request.max_altitude,
            preferred_speed=request.preferred_speed,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-conflicts", summary="检测航路冲突")
async def detect_conflicts(task_ids: list[str]):
    """检测指定任务列表之间的4D冲突"""
    from app.services.simulation_service import SimulationService
    sim = SimulationService()
    all_tasks = sim.get_demo_tasks()
    tasks_with_routes = []
    for t in all_tasks:
        if t["id"] in task_ids:
            route = sim.generate_route_for_task(t)
            tasks_with_routes.append({"id": t["id"], "waypoints": route})

    conflicts = planning_service.detect_conflicts(tasks_with_routes)
    return {"conflicts": conflicts, "count": len(conflicts)}


@router.get("/no-fly-zones", summary="获取禁飞区列表")
async def get_no_fly_zones():
    """获取当前生效的禁飞区数据"""
    from app.services.planning_service import BEIJING_NO_FLY_ZONES
    return {"zones": BEIJING_NO_FLY_ZONES}


@router.get("/noise-zones", summary="获取噪音敏感区域")
async def get_noise_zones():
    """获取噪音敏感区域列表"""
    from app.services.planning_service import NOISE_ZONES
    return {"zones": NOISE_ZONES}


async def _get_task_info(task_id: str) -> dict:
    from app.services.simulation_service import SimulationService
    sim = SimulationService()
    tasks = sim.get_demo_tasks()
    for t in tasks:
        if t["id"] == task_id:
            return t
    raise ValueError(f"任务{task_id}不存在")
