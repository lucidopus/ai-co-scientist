"""
Data Migration Script for AI Co-Scientist Memory System
Migrates data from file-based SimpleMemoryService to MongoDB-based EnhancedMemoryService
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from utils.memory_service import SimpleMemoryService, EnhancedMemoryService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryMigrationService:
    """Service to migrate data from file-based storage to MongoDB"""
    
    def __init__(self, storage_dir: str = "memory_storage"):
        self.storage_dir = storage_dir
        self.simple_memory = SimpleMemoryService(storage_dir)
        
        # Initialize enhanced memory service
        try:
            self.enhanced_memory = EnhancedMemoryService()
            logger.info("Enhanced memory service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize enhanced memory service: {str(e)}")
            raise
    
    def migrate_all_data(self) -> Dict[str, Any]:
        """Migrate all data from file-based storage to MongoDB"""
        logger.info("Starting full data migration...")
        
        migration_results = {
            "start_time": datetime.now(),
            "sessions_migrated": 0,
            "hypotheses_migrated": 0,
            "concepts_migrated": 0,
            "errors": [],
            "success": False
        }
        
        try:
            # Migrate sessions
            sessions_result = self.migrate_sessions()
            migration_results.update(sessions_result)
            
            # Migrate knowledge base (hypotheses and concepts)
            knowledge_result = self.migrate_knowledge_base()
            migration_results.update(knowledge_result)
            
            migration_results["success"] = True
            migration_results["end_time"] = datetime.now()
            migration_results["duration"] = str(migration_results["end_time"] - migration_results["start_time"])
            
            logger.info(f"Migration completed successfully in {migration_results['duration']}")
            self._log_migration_summary(migration_results)
            
        except Exception as e:
            migration_results["errors"].append(f"Critical migration error: {str(e)}")
            migration_results["success"] = False
            logger.error(f"Migration failed: {str(e)}")
        
        return migration_results
    
    def migrate_sessions(self) -> Dict[str, Any]:
        """Migrate session data to MongoDB"""
        logger.info("Migrating research sessions...")
        
        result = {"sessions_migrated": 0, "session_errors": []}
        
        try:
            sessions_file = os.path.join(self.storage_dir, "sessions.json")
            
            if not os.path.exists(sessions_file):
                logger.warning(f"Sessions file not found: {sessions_file}")
                return result
            
            with open(sessions_file, 'r') as f:
                sessions_data = json.load(f)
            
            for session_id, session_data in sessions_data.items():
                try:
                    # Transform session data for enhanced memory service
                    enhanced_session = self._transform_session_data(session_data)
                    
                    # Store in MongoDB
                    stored_id = self.enhanced_memory.store_research_session(enhanced_session)
                    
                    if stored_id:
                        result["sessions_migrated"] += 1
                        logger.info(f"Migrated session: {session_id}")
                    else:
                        result["session_errors"].append(f"Failed to store session: {session_id}")
                        
                except Exception as e:
                    error_msg = f"Error migrating session {session_id}: {str(e)}"
                    result["session_errors"].append(error_msg)
                    logger.error(error_msg)
            
            logger.info(f"Session migration completed: {result['sessions_migrated']} sessions migrated")
            
        except Exception as e:
            error_msg = f"Error reading sessions file: {str(e)}"
            result["session_errors"].append(error_msg)
            logger.error(error_msg)
        
        return result
    
    def migrate_knowledge_base(self) -> Dict[str, Any]:
        """Migrate knowledge base (hypotheses and concepts) to MongoDB"""
        logger.info("Migrating knowledge base...")
        
        result = {
            "hypotheses_migrated": 0,
            "concepts_migrated": 0,
            "hypothesis_errors": [],
            "concept_errors": []
        }
        
        try:
            knowledge_file = os.path.join(self.storage_dir, "knowledge_base.json")
            
            if not os.path.exists(knowledge_file):
                logger.warning(f"Knowledge base file not found: {knowledge_file}")
                return result
            
            with open(knowledge_file, 'r') as f:
                knowledge_data = json.load(f)
            
            # Migrate hypotheses
            hypotheses = knowledge_data.get("hypotheses", [])
            for hypothesis in hypotheses:
                try:
                    # Transform hypothesis data
                    enhanced_hypothesis = self._transform_hypothesis_data(hypothesis)
                    
                    # Store in MongoDB
                    stored_id = self.enhanced_memory.store_hypothesis(enhanced_hypothesis)
                    
                    if stored_id:
                        result["hypotheses_migrated"] += 1
                        logger.info(f"Migrated hypothesis: {hypothesis.get('id', 'unknown')}")
                    else:
                        result["hypothesis_errors"].append(f"Failed to store hypothesis: {hypothesis.get('id', 'unknown')}")
                        
                except Exception as e:
                    error_msg = f"Error migrating hypothesis {hypothesis.get('id', 'unknown')}: {str(e)}"
                    result["hypothesis_errors"].append(error_msg)
                    logger.error(error_msg)
            
            # Migrate concepts to knowledge base
            concepts = knowledge_data.get("concepts", [])
            for concept in concepts:
                try:
                    # Transform concept data
                    enhanced_concept = self._transform_concept_data(concept)
                    
                    # Store in MongoDB knowledge base
                    stored_id = self.enhanced_memory.store_knowledge_item(enhanced_concept)
                    
                    if stored_id:
                        result["concepts_migrated"] += 1
                        logger.info(f"Migrated concept: {concept.get('concept', 'unknown')}")
                    else:
                        result["concept_errors"].append(f"Failed to store concept: {concept.get('concept', 'unknown')}")
                        
                except Exception as e:
                    error_msg = f"Error migrating concept {concept.get('concept', 'unknown')}: {str(e)}"
                    result["concept_errors"].append(error_msg)
                    logger.error(error_msg)
            
            logger.info(f"Knowledge base migration completed: {result['hypotheses_migrated']} hypotheses, {result['concepts_migrated']} concepts migrated")
            
        except Exception as e:
            error_msg = f"Error reading knowledge base file: {str(e)}"
            result["hypothesis_errors"].append(error_msg)
            result["concept_errors"].append(error_msg)
            logger.error(error_msg)
        
        return result
    
    def _transform_session_data(self, session_data: Dict) -> Dict:
        """Transform session data for enhanced memory service"""
        return {
            "session_id": session_data.get("session_id", ""),
            "research_query": session_data.get("query", ""),
            "status": session_data.get("status", "unknown"),
            "created_at": self._parse_datetime(session_data.get("created_at")),
            "hypotheses": session_data.get("hypotheses", []),
            "processing_steps": session_data.get("processing_steps", []),
            "metadata": session_data.get("metadata", {}),
            "current_round": 1,
            "max_rounds": 3,
            "total_processing_time": 0.0,
            "quality_score": 0.7  # Default score for migrated data
        }
    
    def _transform_hypothesis_data(self, hypothesis_data: Dict) -> Dict:
        """Transform hypothesis data for enhanced memory service"""
        return {
            "id": hypothesis_data.get("id", ""),
            "title": hypothesis_data.get("title", ""),
            "description": hypothesis_data.get("description", ""),
            "reasoning": hypothesis_data.get("reasoning", ""),
            "novelty_assessment": hypothesis_data.get("novelty_assessment", ""),
            "research_approach": hypothesis_data.get("research_approach", ""),
            "domain": hypothesis_data.get("domain", "general"),
            "research_query": hypothesis_data.get("research_query", ""),
            "generation_method": "file_migration",
            "confidence_score": hypothesis_data.get("confidence_score", 0.7),
            "tags": hypothesis_data.get("tags", ["migrated"]),
            "source_session": hypothesis_data.get("source_session", ""),
            "parent_hypotheses": hypothesis_data.get("parent_hypotheses", [])
        }
    
    def _transform_concept_data(self, concept_data: Dict) -> Dict:
        """Transform concept data for enhanced memory service"""
        return {
            "concept": concept_data.get("concept", ""),
            "domain": "general",
            "description": f"Migrated concept with frequency: {concept_data.get('frequency', 1)}",
            "source": "file_migration",
            "relevance_score": min(concept_data.get("frequency", 1) / 10.0, 1.0),  # Normalize frequency to score
            "related_hypotheses": [],
            "metadata": {
                "original_frequency": concept_data.get("frequency", 1),
                "original_stored_at": concept_data.get("stored_at", ""),
                "last_seen": concept_data.get("last_seen", ""),
                "migration_date": datetime.now().isoformat()
            },
            "tags": ["migrated", "concept"]
        }
    
    def _parse_datetime(self, date_string: str) -> datetime:
        """Parse datetime string from file-based storage"""
        try:
            if date_string:
                return datetime.fromisoformat(date_string)
            else:
                return datetime.now()
        except (ValueError, TypeError):
            logger.warning(f"Invalid date format: {date_string}, using current time")
            return datetime.now()
    
    def _log_migration_summary(self, results: Dict):
        """Log comprehensive migration summary"""
        logger.info("=" * 60)
        logger.info("MIGRATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Duration: {results.get('duration', 'Unknown')}")
        logger.info(f"Sessions migrated: {results.get('sessions_migrated', 0)}")
        logger.info(f"Hypotheses migrated: {results.get('hypotheses_migrated', 0)}")
        logger.info(f"Concepts migrated: {results.get('concepts_migrated', 0)}")
        
        # Log errors if any
        all_errors = []
        all_errors.extend(results.get("errors", []))
        all_errors.extend(results.get("session_errors", []))
        all_errors.extend(results.get("hypothesis_errors", []))
        all_errors.extend(results.get("concept_errors", []))
        
        if all_errors:
            logger.warning(f"Total errors encountered: {len(all_errors)}")
            for error in all_errors[:5]:  # Show first 5 errors
                logger.warning(f"  - {error}")
            if len(all_errors) > 5:
                logger.warning(f"  ... and {len(all_errors) - 5} more errors")
        else:
            logger.info("No errors encountered during migration")
        
        logger.info("=" * 60)
    
    def verify_migration(self) -> Dict[str, Any]:
        """Verify that migration was successful by comparing counts"""
        logger.info("Verifying migration...")
        
        verification_results = {
            "verification_passed": False,
            "file_counts": {},
            "mongodb_counts": {},
            "discrepancies": []
        }
        
        try:
            # Count items in file-based storage
            sessions_file = os.path.join(self.storage_dir, "sessions.json")
            knowledge_file = os.path.join(self.storage_dir, "knowledge_base.json")
            
            file_sessions = 0
            file_hypotheses = 0
            file_concepts = 0
            
            if os.path.exists(sessions_file):
                with open(sessions_file, 'r') as f:
                    sessions_data = json.load(f)
                    file_sessions = len(sessions_data)
            
            if os.path.exists(knowledge_file):
                with open(knowledge_file, 'r') as f:
                    knowledge_data = json.load(f)
                    file_hypotheses = len(knowledge_data.get("hypotheses", []))
                    file_concepts = len(knowledge_data.get("concepts", []))
            
            verification_results["file_counts"] = {
                "sessions": file_sessions,
                "hypotheses": file_hypotheses,
                "concepts": file_concepts
            }
            
            # Count items in MongoDB
            mongodb_sessions = self.enhanced_memory.db.research_sessions.count_documents({})
            mongodb_hypotheses = self.enhanced_memory.db.hypotheses.count_documents({})
            mongodb_concepts = self.enhanced_memory.db.knowledge_base.count_documents({})
            
            verification_results["mongodb_counts"] = {
                "sessions": mongodb_sessions,
                "hypotheses": mongodb_hypotheses,
                "concepts": mongodb_concepts
            }
            
            # Check for discrepancies
            if file_sessions != mongodb_sessions:
                verification_results["discrepancies"].append(f"Sessions: File={file_sessions}, MongoDB={mongodb_sessions}")
            
            if file_hypotheses != mongodb_hypotheses:
                verification_results["discrepancies"].append(f"Hypotheses: File={file_hypotheses}, MongoDB={mongodb_hypotheses}")
            
            if file_concepts != mongodb_concepts:
                verification_results["discrepancies"].append(f"Concepts: File={file_concepts}, MongoDB={mongodb_concepts}")
            
            verification_results["verification_passed"] = len(verification_results["discrepancies"]) == 0
            
            if verification_results["verification_passed"]:
                logger.info("✅ Migration verification passed - all counts match")
            else:
                logger.warning(f"⚠️  Migration verification found discrepancies: {verification_results['discrepancies']}")
            
        except Exception as e:
            verification_results["discrepancies"].append(f"Verification error: {str(e)}")
            logger.error(f"Error during verification: {str(e)}")
        
        return verification_results
    
    def create_backup(self) -> str:
        """Create backup of existing file-based data before migration"""
        logger.info("Creating backup of existing data...")
        
        backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = os.path.join(os.path.dirname(self.storage_dir), backup_dir)
        
        try:
            os.makedirs(backup_path, exist_ok=True)
            
            # Copy sessions file
            sessions_file = os.path.join(self.storage_dir, "sessions.json")
            if os.path.exists(sessions_file):
                backup_sessions = os.path.join(backup_path, "sessions.json")
                with open(sessions_file, 'r') as src, open(backup_sessions, 'w') as dst:
                    dst.write(src.read())
            
            # Copy knowledge base file
            knowledge_file = os.path.join(self.storage_dir, "knowledge_base.json")
            if os.path.exists(knowledge_file):
                backup_knowledge = os.path.join(backup_path, "knowledge_base.json")
                with open(knowledge_file, 'r') as src, open(backup_knowledge, 'w') as dst:
                    dst.write(src.read())
            
            logger.info(f"Backup created successfully at: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
            return ""


def run_migration():
    """Main function to run the migration process"""
    print("AI Co-Scientist Memory Migration Tool")
    print("=" * 50)
    
    migration_service = MemoryMigrationService()
    
    # Create backup
    backup_path = migration_service.create_backup()
    if backup_path:
        print(f"✅ Backup created at: {backup_path}")
    else:
        print("⚠️  Warning: Could not create backup")
        response = input("Continue with migration anyway? (y/N): ")
        if response.lower() != 'y':
            print("Migration cancelled")
            return
    
    # Run migration
    print("\n🚀 Starting migration...")
    results = migration_service.migrate_all_data()
    
    if results["success"]:
        print("\n✅ Migration completed successfully!")
        
        # Verify migration
        print("\n🔍 Verifying migration...")
        verification = migration_service.verify_migration()
        
        if verification["verification_passed"]:
            print("✅ Verification passed - migration successful!")
        else:
            print("⚠️  Verification found some discrepancies:")
            for discrepancy in verification["discrepancies"]:
                print(f"   - {discrepancy}")
    else:
        print("\n❌ Migration failed!")
        print("Errors encountered:")
        for error in results.get("errors", []):
            print(f"   - {error}")
    
    # Close connections
    migration_service.enhanced_memory.close()
    
    print("\nMigration process completed.")


if __name__ == "__main__":
    run_migration()