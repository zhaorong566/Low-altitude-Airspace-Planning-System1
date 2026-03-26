from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.services.simulation_service import SimulationService

router = APIRouter(prefix="/tasks", tags=["tasks"])
sim_service = SimulationService()


@router.get("/demo", summary="获取演示任务列表")
async def get_demo_tasks():
    """返回预置的演示飞行任务"""
    tasks = sim_service.get_demo_tasks()
    for task in tasks:
        route = sim_service.generate_route_for_task(task)
        task["waypoints"] = route
    return {"tasks": tasks, "total": len(tasks)}


@router.get("/", summary="获取任务列表")
async def list_tasks(
    status: str = None,
    task_type: str = None,
    limit: int = 20,
    offset: int = 0,
):
    """获取飞行任务列表（演示模式返回模拟数据）"""
    tasks = sim_service.get_demo_tasks()
    if status:
        tasks = [t for t in tasks if t.get("status") == status]
    if task_type:
        tasks = [t for t in tasks if t.get("task_type") == task_type]
    return {
        "tasks": tasks[offset: offset + limit],
        "total": len(tasks),
        "limit": limit,
        "offset": offset,
    }


@router.post("/", summary="创建飞行任务")
async def create_task(task: TaskCreate):
    """创建新的飞行任务并触发路径规划"""
    from app.services.planning_service import PlanningService
    planner = PlanningService()

    new_task = {
        "id": f"task-{task.drone_id}-{int(__import__('time').time())}",
        "name": task.name,
        "drone_id": task.drone_id,
        "task_type": task.task_type.value,
        "priority": task.priority.value,
        "status": "planning",
        "origin": {"lat": task.origin_lat, "lon": task.origin_lon, "alt": task.origin_alt},
        "destination": {"lat": task.dest_lat, "lon": task.dest_lon, "alt": task.dest_alt},
        "planned_start": task.planned_start.isoformat() if task.planned_start else None,
    }

    try:
        route_result = await planner.plan_route(
            task_id=new_task["id"],
            origin=(task.origin_lat, task.origin_lon, task.origin_alt),
            destination=(task.dest_lat, task.dest_lon, task.dest_alt),
            max_altitude=task.origin_alt + 80,
        )
        new_task["waypoints"] = route_result["waypoints"]
        new_task["status"] = "approved"
        new_task["route_scores"] = {
            "risk": route_result.get("risk_score"),
            "noise": route_result.get("noise_score"),
            "efficiency": route_result.get("efficiency_score"),
        }
    except Exception as e:
        new_task["status"] = "failed"
        new_task["error"] = str(e)

    return new_task


@router.get("/{task_id}", summary="获取任务详情")
async def get_task(task_id: str):
    """获取指定任务的详细信息"""
    tasks = sim_service.get_demo_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["waypoints"] = sim_service.generate_route_for_task(task)
            return task
    raise HTTPException(status_code=404, detail=f"任务{task_id}不存在")


@router.put("/{task_id}/status", summary="更新任务状态")
async def update_task_status(task_id: str, status: str):
    """更新飞行任务状态"""
    valid_statuses = ["pending", "planning", "approved", "executing", "completed", "failed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"无效状态: {status}")
    return {"task_id": task_id, "status": status, "updated": True}
