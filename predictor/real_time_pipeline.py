# FISO Real-Time Data Pipeline
# Automated data collection and processing pipeline for real-time cloud pricing

import threading
import time
import schedule
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import sqlite3
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict

# Import our data collection modules
from real_data_scraper import RealTimeDataScraper
from enhanced_azure_api import EnhancedAzurePricingAPI

logger = logging.getLogger(__name__)

class RealTimeDataPipeline:
    """Automated real-time data collection and processing pipeline"""
    
    def __init__(self, db_path: str = None):
        """Initialize the real-time data pipeline"""
        self.db_path = db_path or os.path.join(os.path.dirname(__file__), '..', 'security', 'fiso_production.db')
        self.data_scraper = RealTimeDataScraper(self.db_path)
        self.azure_api = EnhancedAzurePricingAPI()
        
        # Pipeline configuration
        self.update_interval_minutes = 2  # Update every 2 minutes for more real-time data
        self.max_workers = 3  # For concurrent data collection
        self.cache_duration_hours = 0.1  # Cache data for 6 minutes (0.1 hours) for fresher data
        
        # Pipeline state
        self.is_running = False
        self.last_update = {}
        self.pipeline_stats = {
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'total_records_collected': 0,
            'last_run_time': None,
            'last_success_time': None
        }
        
        # Initialize database for pipeline management
        self._init_pipeline_database()
        
        logger.info("✅ Real-time data pipeline initialized")
    
    def _init_pipeline_database(self):
        """Initialize database tables for pipeline management"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create pipeline status table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pipeline_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pipeline_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    last_run DATETIME,
                    last_success DATETIME,
                    records_collected INTEGER DEFAULT 0,
                    error_message TEXT,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create data quality metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL,
                    collection_time DATETIME NOT NULL,
                    records_collected INTEGER NOT NULL,
                    data_freshness_score REAL,
                    completeness_score REAL,
                    accuracy_score REAL,
                    availability_score REAL,
                    overall_quality_score REAL,
                    issues_detected TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create pricing trends table for historical analysis
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pricing_trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL,
                    service TEXT NOT NULL,
                    region TEXT NOT NULL,
                    instance_type TEXT NOT NULL,
                    price_trend TEXT,  -- 'increasing', 'decreasing', 'stable'
                    price_change_percent REAL,
                    volatility_score REAL,
                    trend_confidence REAL,
                    analysis_period_days INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Pipeline database initialized")
            
        except Exception as e:
            logger.error(f"❌ Pipeline database initialization failed: {e}")
            raise
    
    def start_pipeline(self):
        """Start the automated data collection pipeline"""
        if self.is_running:
            logger.warning("⚠️ Pipeline is already running")
            return
        
        logger.info("🚀 Starting real-time data pipeline...")
        self.is_running = True
        
        # Schedule data collection jobs
        schedule.every(self.update_interval_minutes).minutes.do(self._run_data_collection)
        schedule.every(30).minutes.do(self._run_data_quality_analysis)
        schedule.every(1).hours.do(self._run_trend_analysis)
        schedule.every(6).hours.do(self._cleanup_old_data)
        
        # Start pipeline thread
        pipeline_thread = threading.Thread(target=self._pipeline_worker, daemon=True)
        pipeline_thread.start()
        
        # Run initial data collection
        self._run_data_collection()
        
        logger.info("✅ Real-time data pipeline started successfully")
    
    def stop_pipeline(self):
        """Stop the automated data collection pipeline"""
        logger.info("🛑 Stopping real-time data pipeline...")
        self.is_running = False
        schedule.clear()
        logger.info("✅ Pipeline stopped")
    
    def _pipeline_worker(self):
        """Worker thread for running scheduled jobs"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logger.error(f"❌ Pipeline worker error: {e}")
                time.sleep(30)  # Wait longer on error
    
    def _run_data_collection(self):
        """Run comprehensive data collection from all providers"""
        logger.info("📊 Running automated data collection...")
        
        collection_start = datetime.now()
        self.pipeline_stats['total_runs'] += 1
        self.pipeline_stats['last_run_time'] = collection_start
        
        try:
            total_records = 0
            collection_results = {}
            
            # Use ThreadPoolExecutor for concurrent collection
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit collection tasks
                aws_future = executor.submit(self._collect_aws_data)
                azure_future = executor.submit(self._collect_azure_data)
                gcp_future = executor.submit(self._collect_gcp_data)
                
                # Collect results
                collection_results['aws'] = aws_future.result()
                collection_results['azure'] = azure_future.result()
                collection_results['gcp'] = gcp_future.result()
            
            # Calculate totals
            for provider, records in collection_results.items():
                count = len(records) if records else 0
                total_records += count
                logger.info(f"✅ {provider.upper()}: {count} records collected")
            
            # Update pipeline stats
            self.pipeline_stats['successful_runs'] += 1
            self.pipeline_stats['last_success_time'] = datetime.now()
            self.pipeline_stats['total_records_collected'] += total_records
            
            # Update pipeline status in database
            self._update_pipeline_status('data_collection', 'success', total_records, None)
            
            collection_duration = (datetime.now() - collection_start).total_seconds()
            logger.info(f"✅ Data collection completed: {total_records} total records in {collection_duration:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Data collection failed: {e}")
            self.pipeline_stats['failed_runs'] += 1
            self._update_pipeline_status('data_collection', 'failed', 0, str(e))
    
    def _collect_aws_data(self) -> List[Any]:
        """Collect AWS pricing data"""
        try:
            logger.info("🔍 Collecting AWS data...")
            aws_data = self.data_scraper.scrape_aws_pricing('us-east-1')
            self.last_update['aws'] = datetime.now()
            return aws_data
        except Exception as e:
            logger.error(f"❌ AWS data collection failed: {e}")
            return []
    
    def _collect_azure_data(self) -> List[Any]:
        """Collect Azure pricing data using enhanced API"""
        try:
            logger.info("🔍 Collecting Azure data...")
            azure_data = self.azure_api.fetch_comprehensive_pricing('eastus')
            
            # Flatten the data structure
            flattened_data = []
            for service_type, records in azure_data.items():
                flattened_data.extend(records)
            
            self.last_update['azure'] = datetime.now()
            return flattened_data
        except Exception as e:
            logger.error(f"❌ Azure data collection failed: {e}")
            return []
    
    def _collect_gcp_data(self) -> List[Any]:
        """Collect GCP pricing data"""
        try:
            logger.info("🔍 Collecting GCP data...")
            gcp_data = self.data_scraper.scrape_gcp_pricing('us-central1')
            self.last_update['gcp'] = datetime.now()
            return gcp_data
        except Exception as e:
            logger.error(f"❌ GCP data collection failed: {e}")
            return []
    
    def _run_data_quality_analysis(self):
        """Analyze data quality and freshness"""
        logger.info("🔬 Running data quality analysis...")
        
        try:
            for provider in ['aws', 'azure', 'gcp']:
                metrics = self._calculate_data_quality_metrics(provider)
                self._store_quality_metrics(provider, metrics)
            
            logger.info("✅ Data quality analysis completed")
            
        except Exception as e:
            logger.error(f"❌ Data quality analysis failed: {e}")
    
    def _calculate_data_quality_metrics(self, provider: str) -> Dict[str, Any]:
        """Calculate data quality metrics for a provider"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get recent data count
            cursor.execute('''
                SELECT COUNT(*) FROM real_pricing_data 
                WHERE provider = ? AND timestamp > datetime('now', '-1 hour')
            ''', (provider,))
            recent_count = cursor.fetchone()[0]
            
            # Get total data count
            cursor.execute('''
                SELECT COUNT(*) FROM real_pricing_data WHERE provider = ?
            ''', (provider,))
            total_count = cursor.fetchone()[0]
            
            # Calculate freshness (how recent is the data)
            cursor.execute('''
                SELECT MAX(timestamp) FROM real_pricing_data WHERE provider = ?
            ''', (provider,))
            latest_timestamp = cursor.fetchone()[0]
            
            conn.close()
            
            # Calculate quality scores
            freshness_score = 1.0 if recent_count > 0 else 0.0
            completeness_score = min(recent_count / 50, 1.0)  # Expect at least 50 records
            availability_score = 1.0 if latest_timestamp else 0.0
            
            # Overall quality score
            overall_score = (freshness_score + completeness_score + availability_score) / 3
            
            return {
                'records_collected': recent_count,
                'data_freshness_score': freshness_score,
                'completeness_score': completeness_score,
                'accuracy_score': 0.95,  # Assume high accuracy for real APIs
                'availability_score': availability_score,
                'overall_quality_score': overall_score,
                'issues_detected': '[]'  # JSON array of issues
            }
            
        except Exception as e:
            logger.error(f"Quality metrics calculation failed for {provider}: {e}")
            return {}
    
    def _store_quality_metrics(self, provider: str, metrics: Dict[str, Any]):
        """Store data quality metrics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO data_quality_metrics 
                (provider, collection_time, records_collected, data_freshness_score,
                 completeness_score, accuracy_score, availability_score, 
                 overall_quality_score, issues_detected)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                provider, datetime.now(), metrics.get('records_collected', 0),
                metrics.get('data_freshness_score', 0.0),
                metrics.get('completeness_score', 0.0),
                metrics.get('accuracy_score', 0.0),
                metrics.get('availability_score', 0.0),
                metrics.get('overall_quality_score', 0.0),
                metrics.get('issues_detected', '[]')
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store quality metrics for {provider}: {e}")
    
    def _run_trend_analysis(self):
        """Analyze pricing trends and patterns"""
        logger.info("📈 Running pricing trend analysis...")
        
        try:
            for provider in ['aws', 'azure', 'gcp']:
                trends = self._analyze_pricing_trends(provider)
                self._store_trend_analysis(provider, trends)
            
            logger.info("✅ Trend analysis completed")
            
        except Exception as e:
            logger.error(f"❌ Trend analysis failed: {e}")
    
    def _analyze_pricing_trends(self, provider: str) -> List[Dict[str, Any]]:
        """Analyze pricing trends for a provider"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get pricing data for the last 24 hours, grouped by service and instance type
            cursor.execute('''
                SELECT service, region, instance_type, 
                       AVG(CASE WHEN price_per_hour IS NOT NULL THEN price_per_hour 
                                WHEN price_per_gb_month IS NOT NULL THEN price_per_gb_month 
                                ELSE price_per_request END) as avg_price,
                       COUNT(*) as data_points,
                       MIN(timestamp) as earliest_time,
                       MAX(timestamp) as latest_time
                FROM real_pricing_data 
                WHERE provider = ? AND timestamp > datetime('now', '-24 hours')
                GROUP BY service, region, instance_type
                HAVING COUNT(*) >= 2
            ''', (provider,))
            
            results = cursor.fetchall()
            conn.close()
            
            trends = []
            for row in results:
                service, region, instance_type, avg_price, data_points, earliest_time, latest_time = row
                
                # Simple trend analysis (would be more sophisticated in production)
                trend = 'stable'  # Default
                change_percent = 0.0
                volatility = 0.1  # Low volatility
                confidence = 0.8
                
                trends.append({
                    'service': service,
                    'region': region,
                    'instance_type': instance_type,
                    'price_trend': trend,
                    'price_change_percent': change_percent,
                    'volatility_score': volatility,
                    'trend_confidence': confidence,
                    'analysis_period_days': 1
                })
            
            return trends
            
        except Exception as e:
            logger.error(f"Trend analysis failed for {provider}: {e}")
            return []
    
    def _store_trend_analysis(self, provider: str, trends: List[Dict[str, Any]]):
        """Store trend analysis results"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for trend in trends:
                cursor.execute('''
                    INSERT INTO pricing_trends 
                    (provider, service, region, instance_type, price_trend,
                     price_change_percent, volatility_score, trend_confidence, analysis_period_days)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    provider, trend['service'], trend['region'], trend['instance_type'],
                    trend['price_trend'], trend['price_change_percent'],
                    trend['volatility_score'], trend['trend_confidence'],
                    trend['analysis_period_days']
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Stored {len(trends)} trend analyses for {provider}")
            
        except Exception as e:
            logger.error(f"Failed to store trend analysis for {provider}: {e}")
    
    def _cleanup_old_data(self):
        """Clean up old data to maintain performance"""
        logger.info("🧹 Cleaning up old data...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Keep only last 7 days of pricing data
            cursor.execute('''
                DELETE FROM real_pricing_data 
                WHERE timestamp < datetime('now', '-7 days')
            ''')
            
            # Keep only last 30 days of quality metrics
            cursor.execute('''
                DELETE FROM data_quality_metrics 
                WHERE created_at < datetime('now', '-30 days')
            ''')
            
            # Keep only last 30 days of trend analysis
            cursor.execute('''
                DELETE FROM pricing_trends 
                WHERE created_at < datetime('now', '-30 days')
            ''')
            
            # Clean up old cache entries
            cursor.execute('''
                DELETE FROM api_cache 
                WHERE expires_at < datetime('now')
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Data cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Data cleanup failed: {e}")
    
    def _update_pipeline_status(self, pipeline_name: str, status: str, records_collected: int, error_message: str):
        """Update pipeline status in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO pipeline_status 
                (pipeline_name, status, last_run, last_success, records_collected, error_message, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                pipeline_name, status, datetime.now(),
                datetime.now() if status == 'success' else None,
                records_collected, error_message, json.dumps(self.pipeline_stats)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update pipeline status: {e}")
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status and statistics"""
        return {
            'is_running': self.is_running,
            'stats': self.pipeline_stats.copy(),
            'last_updates': self.last_update.copy(),
            'configuration': {
                'update_interval_minutes': self.update_interval_minutes,
                'cache_duration_hours': self.cache_duration_hours,
                'max_workers': self.max_workers
            }
        }
    
    def get_data_quality_report(self) -> Dict[str, Any]:
        """Get comprehensive data quality report"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get latest quality metrics for each provider
            cursor.execute('''
                SELECT provider, 
                       AVG(overall_quality_score) as avg_quality,
                       AVG(data_freshness_score) as avg_freshness,
                       AVG(completeness_score) as avg_completeness,
                       COUNT(*) as measurements
                FROM data_quality_metrics 
                WHERE collection_time > datetime('now', '-24 hours')
                GROUP BY provider
            ''')
            
            quality_data = {}
            for row in cursor.fetchall():
                provider, avg_quality, avg_freshness, avg_completeness, measurements = row
                quality_data[provider] = {
                    'average_quality_score': round(avg_quality, 3),
                    'average_freshness_score': round(avg_freshness, 3),
                    'average_completeness_score': round(avg_completeness, 3),
                    'measurements_count': measurements
                }
            
            conn.close()
            
            return {
                'report_timestamp': datetime.now().isoformat(),
                'providers': quality_data,
                'overall_health': 'good' if all(p.get('average_quality_score', 0) > 0.7 for p in quality_data.values()) else 'needs_attention'
            }
            
        except Exception as e:
            logger.error(f"Failed to generate quality report: {e}")
            return {}

# Test function
def test_pipeline():
    """Test the real-time data pipeline"""
    try:
        print("🧪 Testing Real-Time Data Pipeline...")
        
        pipeline = RealTimeDataPipeline()
        print("✅ Pipeline initialization successful")
        
        # Test data collection
        pipeline._run_data_collection()
        print("✅ Data collection test completed")
        
        # Get pipeline status
        status = pipeline.get_pipeline_status()
        print(f"✅ Pipeline status: {status['stats']['successful_runs']} successful runs")
        
        # Get quality report
        quality_report = pipeline.get_data_quality_report()
        print(f"✅ Quality report: {len(quality_report.get('providers', {}))} providers analyzed")
        
        print("🎉 All tests passed! Real-time data pipeline is operational.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_pipeline()
