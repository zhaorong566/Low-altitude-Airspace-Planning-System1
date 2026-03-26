from fastapi import APIRouter, HTTPException
from app.services.simulation_service import SimulationService
from app.schemas.drone import DroneCreate, DronePositionUpdate

router = APIRouter(prefix="/drones", tags=["drones"])
sim_service = SimulationService()


@router.get("/", summary="获取无人机列表")
async def list_drones():
    """获取所有注册无人机"""
    drones = sim_service.get_demo_drones()
    return {"drones": drones, "total": len(drones)}


@router.get("/{drone_id}", summary="获取无人机详情")
async def get_drone(drone_id: str):
    """获取指定无人机信息"""
    drones = sim_service.get_demo_drones()
    for d in drones:
        if d["drone_id"] == drone_id:
            return d
    raise HTTPException(status_code=404, detail=f"无人机{drone_id}不存在")


@router.get("/{drone_id}/position", summary="获取无人机当前位置")
async def get_drone_position(drone_id: str):
    """获取无人机实时位置"""
    tasks = sim_service.get_demo_tasks()
    for task in tasks:
        if task["drone_id"] == drone_id and task.get("status") == "executing":
            sim_service.generate_route_for_task(task)
            pos = sim_service.get_current_position(task["id"])
            if pos:
                pos["drone_id"] = drone_id
                return pos
    raise HTTPException(status_code=404, detail=f"无人机{drone_id}当前无执行任务")


@router.post("/", summary="注册无人机")
async def register_drone(drone: DroneCreate):
    """注册新的无人机"""
    return {
        "drone_id": drone.drone_id,
        "name": drone.name,
        "model": drone.model,
        "status": "registered",
    }
