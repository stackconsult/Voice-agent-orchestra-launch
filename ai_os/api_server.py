#!/usr/bin/env python3
"""
Enhanced AI-OS API Server
=========================
FastAPI server to bridge the Enhanced Skill Engine with UI clients (Electron, Web, Mobile).

Provides REST endpoints for:
- Skill execution via EnhancedSkillExecutor
- Skill generation via EnhancedSkillGenerator
- System status and health checks
- Skill listing and discovery

Usage:
    python ai_os/api_server.py
    # Server runs on http://localhost:8000
    # API docs at http://localhost:8000/docs
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import enhanced components
from .workflows.enhanced_skill_executor import EnhancedSkillExecutor
from .workflows.enhanced_skill_generator import EnhancedSkillGenerator, ModelSelector

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI App Setup ---
app = FastAPI(
    title="Enhanced AI-OS API",
    description="REST API for the Enhanced Skill Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for Electron/web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Initialize Enhanced Components ---
executor = EnhancedSkillExecutor()
generator = EnhancedSkillGenerator()
model_selector = ModelSelector()

# --- Pydantic Models for API ---

class SkillRequest(BaseModel):
    """Request model for skill execution."""
    name: str = Field(..., description="Name of the skill to execute")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for execution")

class GenerateRequest(BaseModel):
    """Request model for skill generation."""
    prompt: str = Field(..., description="Natural language description of the skill to create")
    author: Optional[str] = Field(default="AI-OS User", description="Author of the skill")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for generation")

class SkillAnalysisRequest(BaseModel):
    """Request model for model selection analysis."""
    description: str = Field(..., description="Task description to analyze")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")

class SkillListResponse(BaseModel):
    """Response model for skill listing."""
    skills: List[Dict[str, Any]] = Field(description="List of available skills")
    total: int = Field(description="Total number of skills")

class ExecutionResponse(BaseModel):
    """Response model for skill execution."""
    status: str = Field(description="Execution status")
    skill: str = Field(description="Skill name")
    steps_completed: int = Field(description="Number of steps completed")
    final_context: Optional[Dict[str, Any]] = Field(description="Final execution context")
    execution_time: Optional[float] = Field(description="Execution time in seconds")
    error: Optional[str] = Field(description="Error message if execution failed")

class GenerationResponse(BaseModel):
    """Response model for skill generation."""
    status: str = Field(description="Generation status")
    skill_name: str = Field(description="Generated skill name")
    path: str = Field(description="Path to generated skill files")
    mode: str = Field(description="Execution mode")
    model: str = Field(description="Recommended model")
    internet_required: bool = Field(description="Whether internet access is required")
    error: Optional[str] = Field(description="Error message if generation failed")

class AnalysisResponse(BaseModel):
    """Response model for task analysis."""
    mode: str = Field(description="Recommended execution mode")
    model: str = Field(description="Recommended AI model")
    internet_required: bool = Field(description="Whether internet access is required")
    fallback_model: Optional[str] = Field(description="Fallback model if available")
    reasoning: str = Field(description="Explanation for the recommendation")

class SystemStatusResponse(BaseModel):
    """Response model for system status."""
    status: str = Field(description="System status")
    version: str = Field(description="API version")
    components: Dict[str, str] = Field(description="Component status")
    skills_available: int = Field(description="Number of available skills")
    timestamp: str = Field(description="Status timestamp")

# --- API Endpoints ---

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Enhanced AI-OS API Server",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=SystemStatusResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check if skills directory exists
        skills_dir = Path("skills")
        skills_count = len([d for d in skills_dir.iterdir() if d.is_dir()]) if skills_dir.exists() else 0
        
        return SystemStatusResponse(
            status="healthy",
            version="1.0.0",
            components={
                "executor": "active",
                "generator": "active", 
                "model_selector": "active"
            },
            skills_available=skills_count,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/skills", response_model=SkillListResponse)
async def list_skills():
    """List all available skills."""
    try:
        skills_dir = Path("skills")
        if not skills_dir.exists():
            return SkillListResponse(skills=[], total=0)
        
        skills = []
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    # Try to read basic info from skill file
                    try:
                        content = skill_file.read_text()
                        name = skill_dir.name
                        
                        # Extract basic info from frontmatter (simplified)
                        description = "No description available"
                        for line in content.split('\n'):
                            if line.startswith('description:'):
                                description = line.split(':', 1)[1].strip().strip('"')
                                break
                        
                        skills.append({
                            "name": name,
                            "description": description,
                            "path": str(skill_dir)
                        })
                    except Exception:
                        # Fallback for malformed skill files
                        skills.append({
                            "name": skill_dir.name,
                            "description": "Skill file unreadable",
                            "path": str(skill_dir)
                        })
        
        return SkillListResponse(skills=skills, total=len(skills))
        
    except Exception as e:
        logger.error(f"Failed to list skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute", response_model=ExecutionResponse)
async def execute_skill(request: SkillRequest, background_tasks: BackgroundTasks):
    """Execute a skill by name."""
    start_time = datetime.now()
    
    try:
        logger.info(f"Executing skill: {request.name}")
        
        # Execute the skill
        result = await executor.execute_skill(request.name, context=request.context)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return ExecutionResponse(
            status="success",
            skill=request.name,
            steps_completed=result.get("steps_completed", 0),
            final_context=result.get("final_context"),
            execution_time=execution_time
        )
        
    except FileNotFoundError as e:
        logger.error(f"Skill not found: {request.name}")
        raise HTTPException(status_code=404, detail=f"Skill '{request.name}' not found")
    except Exception as e:
        logger.error(f"Skill execution failed: {e}")
        execution_time = (datetime.now() - start_time).total_seconds()
        return ExecutionResponse(
            status="error",
            skill=request.name,
            steps_completed=0,
            execution_time=execution_time,
            error=str(e)
        )

@app.post("/generate", response_model=GenerationResponse)
async def generate_skill(request: GenerateRequest):
    """Generate a new skill from natural language description."""
    try:
        logger.info(f"Generating skill from prompt: {request.prompt[:100]}...")
        
        # Generate the skill
        skill = await generator.generate_skill(
            voice_input=request.prompt,
            author=request.author,
            context=request.context
        )
        
        # Save the skill
        skill_path = await generator.save_skill(skill)
        
        return GenerationResponse(
            status="created",
            skill_name=skill.metadata.name,
            path=str(skill_path),
            mode=skill.metadata.execution_config.mode.value,
            model=skill.metadata.execution_config.recommended_model,
            internet_required=skill.metadata.execution_config.requires_internet
        )
        
    except Exception as e:
        logger.error(f"Skill generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_task(request: SkillAnalysisRequest):
    """Analyze a task description to recommend execution mode and model."""
    try:
        logger.info(f"Analyzing task: {request.description[:100]}...")
        
        # Get model configuration
        config = model_selector.analyze_requirements(request.description, request.context or {})
        
        # Generate reasoning
        if config.mode.value == "local_only":
            reasoning = "Sensitive data detected - forcing local processing for privacy"
        elif config.mode.value == "cloud_first":
            reasoning = "Complex task requiring advanced AI capabilities"
        else:  # hybrid
            reasoning = "Standard automation with optional cloud enhancement"
        
        return AnalysisResponse(
            mode=config.mode.value,
            model=config.recommended_model,
            internet_required=config.requires_internet,
            fallback_model=config.fallback_model,
            reasoning=reasoning
        )
        
    except Exception as e:
        logger.error(f"Task analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/skill/{skill_name}/details")
async def get_skill_details(skill_name: str):
    """Get detailed information about a specific skill."""
    try:
        skill_path = Path(f"skills/{skill_name}")
        if not skill_path.exists():
            raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")
        
        skill_file = skill_path / "SKILL.md"
        workflow_file = skill_path / "workflow.yaml"
        
        details = {
            "name": skill_name,
            "path": str(skill_path),
            "skill_file_exists": skill_file.exists(),
            "workflow_file_exists": workflow_file.exists()
        }
        
        # Read skill file if it exists
        if skill_file.exists():
            try:
                content = skill_file.read_text()
                details["skill_content"] = content
                
                # Extract frontmatter (simplified parsing)
                if content.startswith("---"):
                    frontmatter_end = content.find("---", 3)
                    if frontmatter_end != -1:
                        frontmatter = content[3:frontmatter_end]
                        details["frontmatter"] = frontmatter
            except Exception as e:
                details["skill_read_error"] = str(e)
        
        # Read workflow file if it exists
        if workflow_file.exists():
            try:
                details["workflow_content"] = workflow_file.read_text()
            except Exception as e:
                details["workflow_read_error"] = str(e)
        
        return details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get skill details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/skill/{skill_name}")
async def delete_skill(skill_name: str):
    """Delete a skill and all its files."""
    try:
        skill_path = Path(f"skills/{skill_name}")
        if not skill_path.exists():
            raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")
        
        # Remove the skill directory
        import shutil
        shutil.rmtree(skill_path)
        
        logger.info(f"Deleted skill: {skill_name}")
        return {"status": "deleted", "skill": skill_name}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete skill: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Background Tasks ---

async def cleanup_old_logs():
    """Background task to clean up old log files."""
    try:
        logs_dir = Path(".aios/logs")
        if logs_dir.exists():
            # Clean up logs older than 7 days
            import time
            current_time = time.time()
            for log_file in logs_dir.glob("*.log"):
                if current_time - log_file.stat().st_mtime > 7 * 24 * 3600:  # 7 days
                    log_file.unlink()
                    logger.info(f"Cleaned up old log: {log_file}")
    except Exception as e:
        logger.error(f"Log cleanup failed: {e}")

# --- Server Startup ---

@app.on_event("startup")
async def startup_event():
    """Initialize server on startup."""
    logger.info("Enhanced AI-OS API Server starting up...")
    
    # Ensure required directories exist
    Path("skills").mkdir(exist_ok=True)
    Path(".aios/logs").mkdir(parents=True, exist_ok=True)
    
    # Start background cleanup task
    asyncio.create_task(cleanup_old_logs())
    
    logger.info("API Server ready at http://localhost:8000")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on server shutdown."""
    logger.info("Enhanced AI-OS API Server shutting down...")

# --- Main Entry Point ---

if __name__ == "__main__":
    print("🚀 Starting Enhanced AI-OS API Server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Alternative Docs: http://localhost:8000/redoc")
    print("💚 Health Check: http://localhost:8000/health")
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False  # Set to True for development
    )
