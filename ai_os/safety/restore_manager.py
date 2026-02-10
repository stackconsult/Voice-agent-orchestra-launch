"""
Restore Manager - System Snapshots and Rollback

Provides system snapshot creation and restoration capabilities for safe
workflow execution. Captures system state before execution and can
restore to previous state if errors occur.
"""

import asyncio
import json
import logging
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib
import os

logger = logging.getLogger(__name__)


class RestoreManager:
    """
    Manages system snapshots and restoration for safe workflow execution.
    
    Creates snapshots before skill execution and can restore system state
    if critical errors occur during execution.
    """
    
    def __init__(self, snapshot_dir: Optional[Path] = None):
        """
        Initialize restore manager.
        
        Args:
            snapshot_dir: Directory to store snapshots (default: ~/.aios/snapshots)
        """
        self.snapshot_dir = snapshot_dir or Path.home() / ".aios" / "snapshots"
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.snapshot_dir / "snapshots.json"
        self.snapshots = self._load_metadata()
        
    def _load_metadata(self) -> Dict[str, Any]:
        """Load snapshot metadata from file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load snapshot metadata: {e}")
                return {}
        return {}
    
    def _save_metadata(self) -> None:
        """Save snapshot metadata to file."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.snapshots, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save snapshot metadata: {e}")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash file {file_path}: {e}")
            return ""
    
    async def create_snapshot(
        self, 
        skill_name: str, 
        context: Dict[str, Any],
        directories: List[str],
        files: List[str]
    ) -> str:
        """
        Create a system snapshot.
        
        Args:
            skill_name: Name of the skill being executed
            context: Execution context information
            directories: List of directory paths to snapshot
            files: List of specific file paths to snapshot
            
        Returns:
            Snapshot ID for later restoration
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_id = f"{timestamp}_{skill_name}"
        snapshot_path = self.snapshot_dir / snapshot_id
        
        logger.info(f"Creating snapshot: {snapshot_id}")
        
        try:
            # Create snapshot directory
            snapshot_path.mkdir(parents=True, exist_ok=True)
            
            # Snapshot metadata
            snapshot_metadata = {
                "id": snapshot_id,
                "skill_name": skill_name,
                "timestamp": timestamp,
                "context": context,
                "directories": {},
                "files": {},
                "created_at": time.time()
            }
            
            # Snapshot directories
            for dir_path in directories:
                dir_path = Path(dir_path).expanduser().resolve()
                if dir_path.exists() and dir_path.is_dir():
                    await self._snapshot_directory(
                        dir_path, 
                        snapshot_path / "directories" / dir_path.name,
                        snapshot_metadata["directories"]
                    )
            
            # Snapshot specific files
            for file_path in files:
                file_path = Path(file_path).expanduser().resolve()
                if file_path.exists() and file_path.is_file():
                    await self._snapshot_file(
                        file_path,
                        snapshot_path / "files" / file_path.name,
                        snapshot_metadata["files"]
                    )
            
            # Save snapshot metadata
            snapshot_file = snapshot_path / "snapshot.json"
            with open(snapshot_file, 'w') as f:
                json.dump(snapshot_metadata, f, indent=2)
            
            # Update global metadata
            self.snapshots[snapshot_id] = snapshot_metadata
            self._save_metadata()
            
            logger.info(f"Snapshot created successfully: {snapshot_id}")
            return snapshot_id
            
        except Exception as e:
            logger.error(f"Failed to create snapshot: {e}")
            # Cleanup failed snapshot
            if snapshot_path.exists():
                shutil.rmtree(snapshot_path)
            raise
    
    async def _snapshot_directory(
        self, 
        source_dir: Path, 
        target_dir: Path, 
        metadata: Dict[str, Any]
    ) -> None:
        """Snapshot a directory recursively."""
        target_dir.mkdir(parents=True, exist_ok=True)
        
        dir_metadata = {
            "path": str(source_dir),
            "files": {}
        }
        
        for file_path in source_dir.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(source_dir)
                target_file = target_dir / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(file_path, target_file)
                
                # Record metadata
                file_hash = self._calculate_file_hash(file_path)
                dir_metadata["files"][str(relative_path)] = {
                    "hash": file_hash,
                    "size": file_path.stat().st_size,
                    "mtime": file_path.stat().st_mtime
                }
        
        metadata[source_dir.name] = dir_metadata
    
    async def _snapshot_file(
        self, 
        source_file: Path, 
        target_file: Path, 
        metadata: Dict[str, Any]
    ) -> None:
        """Snapshot a single file."""
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        shutil.copy2(source_file, target_file)
        
        # Record metadata
        file_hash = self._calculate_file_hash(source_file)
        metadata[source_file.name] = {
            "hash": file_hash,
            "size": source_file.stat().st_size,
            "mtime": source_file.stat().st_mtime,
            "path": str(source_file)
        }
    
    async def restore(self, snapshot_id: str, verify: bool = True) -> Dict[str, Any]:
        """
        Restore system from snapshot.
        
        Args:
            snapshot_id: ID of snapshot to restore from
            verify: Whether to verify file integrity after restore
            
        Returns:
            Restoration result with details
        """
        if snapshot_id not in self.snapshots:
            raise ValueError(f"Snapshot not found: {snapshot_id}")
        
        snapshot_path = self.snapshot_dir / snapshot_id
        if not snapshot_path.exists():
            raise ValueError(f"Snapshot directory not found: {snapshot_id}")
        
        logger.info(f"Restoring from snapshot: {snapshot_id}")
        
        try:
            # Load snapshot metadata
            snapshot_file = snapshot_path / "snapshot.json"
            with open(snapshot_file, 'r') as f:
                snapshot_metadata = json.load(f)
            
            result = {
                "snapshot_id": snapshot_id,
                "restored_directories": [],
                "restored_files": [],
                "errors": [],
                "verified": False
            }
            
            # Restore directories
            directories_dir = snapshot_path / "directories"
            if directories_dir.exists():
                for dir_name in snapshot_metadata.get("directories", {}):
                    source_dir = directories_dir / dir_name
                    target_dir = Path(snapshot_metadata["directories"][dir_name]["path"])
                    
                    if await self._restore_directory(source_dir, target_dir, verify):
                        result["restored_directories"].append(str(target_dir))
            
            # Restore files
            files_dir = snapshot_path / "files"
            if files_dir.exists():
                for file_name in snapshot_metadata.get("files", {}):
                    source_file = files_dir / file_name
                    target_file = Path(snapshot_metadata["files"][file_name]["path"])
                    
                    if await self._restore_file(
                        source_file, 
                        target_file, 
                        snapshot_metadata["files"][file_name],
                        verify
                    ):
                        result["restored_files"].append(str(target_file))
            
            result["verified"] = verify
            logger.info(f"Restore completed: {len(result['restored_directories'])} dirs, {len(result['restored_files'])} files")
            
            return result
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise
    
    async def _restore_directory(
        self, 
        source_dir: Path, 
        target_dir: Path, 
        verify: bool
    ) -> bool:
        """Restore a directory from snapshot."""
        try:
            if not source_dir.exists():
                return False
            
            target_dir.mkdir(parents=True, exist_ok=True)
            
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(source_dir)
                    target_file = target_dir / relative_path
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    shutil.copy2(file_path, target_file)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore directory {target_dir}: {e}")
            return False
    
    async def _restore_file(
        self, 
        source_file: Path, 
        target_file: Path, 
        metadata: Dict[str, Any],
        verify: bool
    ) -> bool:
        """Restore a single file from snapshot."""
        try:
            if not source_file.exists():
                return False
            
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, target_file)
            
            if verify:
                current_hash = self._calculate_file_hash(target_file)
                if current_hash != metadata.get("hash"):
                    logger.warning(f"File hash mismatch after restore: {target_file}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore file {target_file}: {e}")
            return False
    
    def list_snapshots(self) -> List[Dict[str, Any]]:
        """List all available snapshots."""
        snapshots = []
        for snapshot_id, metadata in self.snapshots.items():
            snapshot_path = self.snapshot_dir / snapshot_id
            snapshots.append({
                "id": snapshot_id,
                "skill_name": metadata.get("skill_name"),
                "timestamp": metadata.get("timestamp"),
                "created_at": metadata.get("created_at"),
                "exists": snapshot_path.exists(),
                "size": self._get_snapshot_size(snapshot_path) if snapshot_path.exists() else 0
            })
        
        return sorted(snapshots, key=lambda x: x.get("created_at", 0), reverse=True)
    
    def _get_snapshot_size(self, snapshot_path: Path) -> int:
        """Get total size of snapshot in bytes."""
        try:
            total_size = 0
            for file_path in snapshot_path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            return total_size
        except Exception:
            return 0
    
    async def cleanup_old_snapshots(self, days: int = 7) -> int:
        """
        Clean up snapshots older than specified days.
        
        Args:
            days: Number of days to keep snapshots
            
        Returns:
            Number of snapshots cleaned up
        """
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        cleaned_count = 0
        
        snapshots_to_remove = []
        for snapshot_id, metadata in self.snapshots.items():
            if metadata.get("created_at", 0) < cutoff_time:
                snapshots_to_remove.append(snapshot_id)
        
        for snapshot_id in snapshots_to_remove:
            try:
                snapshot_path = self.snapshot_dir / snapshot_id
                if snapshot_path.exists():
                    shutil.rmtree(snapshot_path)
                
                del self.snapshots[snapshot_id]
                cleaned_count += 1
                logger.info(f"Cleaned up old snapshot: {snapshot_id}")
                
            except Exception as e:
                logger.error(f"Failed to cleanup snapshot {snapshot_id}: {e}")
        
        if cleaned_count > 0:
            self._save_metadata()
        
        return cleaned_count
    
    async def verify_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """
        Verify snapshot integrity.
        
        Args:
            snapshot_id: ID of snapshot to verify
            
        Returns:
            Verification result
        """
        if snapshot_id not in self.snapshots:
            raise ValueError(f"Snapshot not found: {snapshot_id}")
        
        snapshot_path = self.snapshot_dir / snapshot_id
        if not snapshot_path.exists():
            raise ValueError(f"Snapshot directory not found: {snapshot_id}")
        
        result = {
            "snapshot_id": snapshot_id,
            "verified": False,
            "errors": [],
            "missing_files": [],
            "corrupted_files": []
        }
        
        try:
            # Load snapshot metadata
            snapshot_file = snapshot_path / "snapshot.json"
            with open(snapshot_file, 'r') as f:
                snapshot_metadata = json.load(f)
            
            # Verify files
            files_dir = snapshot_path / "files"
            if files_dir.exists():
                for file_name, file_metadata in snapshot_metadata.get("files", {}).items():
                    source_file = files_dir / file_name
                    
                    if not source_file.exists():
                        result["missing_files"].append(file_name)
                        continue
                    
                    current_hash = self._calculate_file_hash(source_file)
                    if current_hash != file_metadata.get("hash"):
                        result["corrupted_files"].append(file_name)
            
            result["verified"] = len(result["errors"]) == 0 and len(result["missing_files"]) == 0
            
        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"Snapshot verification failed: {e}")
        
        return result
