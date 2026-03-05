"""Demo video/NVR tool — STUB: returns fake clip URLs."""

from __future__ import annotations
from app.tools.base import BaseTool, ToolResult


class VideoTool(BaseTool):
    name = "search_video"
    description = "Search NVR/Dahua cameras for video clips in a time window (stub)."

    async def execute(self, params: dict) -> ToolResult:
        camera = params.get("camera", "cam-datacenter-01")
        time_from = params.get("time_from", "2026-03-04T10:00:00Z")
        time_to = params.get("time_to", "2026-03-04T11:00:00Z")
        return ToolResult(success=True, data={
            "camera": camera,
            "clips": [
                {
                    "clip_id": "clip_001",
                    "clip_url": f"https://nvr.company.local/clips/{camera}/clip_001.mp4",
                    "thumbnail_url": f"https://nvr.company.local/thumbs/{camera}/clip_001.jpg",
                    "start": time_from,
                    "end": time_to,
                    "duration_sec": 3600,
                }
            ],
            "total_clips": 1,
        })
