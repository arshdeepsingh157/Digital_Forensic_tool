"""
Forensic Analysis DAG
Apache Airflow DAG for orchestrating forensic file analysis pipeline
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pipeline.ingestion import IngestionService
from pipeline.processing import ProcessingService
from pipeline.storage import StorageService
from models.database import SessionLocal

# Default arguments
default_args = {
    'owner': 'forensic_system',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    'forensic_file_analysis',
    default_args=default_args,
    description='End-to-end forensic file analysis pipeline',
    schedule_interval=None,  # Triggered manually or via API
    start_date=days_ago(1),
    catchup=False,
    tags=['forensics', 'analysis', 'security'],
)


def ingest_file_task(**context):
    """Task 1: Ingest and validate file"""
    file_path = context['dag_run'].conf.get('file_path')
    
    if not file_path:
        raise ValueError("file_path not provided in DAG configuration")
    
    # Validate and ingest file
    result = IngestionService.ingest_file(file_path)
    
    if not result.get('success'):
        raise Exception(f"File ingestion failed: {result.get('error')}")
    
    # Push file_id and path to XCom for next tasks
    context['task_instance'].xcom_push(key='file_id', value=result['file_id'])
    context['task_instance'].xcom_push(key='file_path', value=result['file_path'])
    
    return result


def process_file_task(**context):
    """Task 2: Process file through forensic pipeline"""
    ti = context['task_instance']
    file_id = ti.xcom_pull(key='file_id', task_ids='ingest_file')
    file_path = ti.xcom_pull(key='file_path', task_ids='ingest_file')
    
    # Process file
    result = ProcessingService.process_file(file_path, file_id)
    
    if result.get('status') != 'completed':
        raise Exception(f"Processing failed: {result.get('error')}")
    
    # Push processing result to XCom
    ti.xcom_push(key='processing_result', value=result)
    
    return result


def store_results_task(**context):
    """Task 3: Store results in database"""
    ti = context['task_instance']
    processing_result = ti.xcom_pull(key='processing_result', task_ids='process_file')
    
    # Get DB session
    db = SessionLocal()
    
    try:
        # Save to PostgreSQL
        forensic_record = StorageService.save_forensic_result(db, processing_result)
        
        # Save to MongoDB
        mongo_id = StorageService.save_to_mongodb(processing_result)
        
        return {
            'postgres_id': forensic_record.id,
            'mongo_id': mongo_id,
            'file_id': forensic_record.file_id
        }
    finally:
        db.close()


def generate_report_task(**context):
    """Task 4: Generate forensic report"""
    ti = context['task_instance']
    processing_result = ti.xcom_pull(key='processing_result', task_ids='process_file')
    
    comprehensive = processing_result.get('comprehensive_analysis', {})
    
    report_summary = {
        'file_id': processing_result.get('file_id'),
        'file_name': processing_result.get('file_name'),
        'overall_score': comprehensive.get('overall_score'),
        'verdict': comprehensive.get('verdict'),
        'confidence': comprehensive.get('confidence'),
        'recommendations': comprehensive.get('recommendations'),
        'generated_at': datetime.utcnow().isoformat()
    }
    
    ti.xcom_push(key='report_summary', value=report_summary)
    
    return report_summary


def log_completion_task(**context):
    """Task 5: Log pipeline completion"""
    ti = context['task_instance']
    file_id = ti.xcom_pull(key='file_id', task_ids='ingest_file')
    report = ti.xcom_pull(key='report_summary', task_ids='generate_report')
    
    # Get DB session
    db = SessionLocal()
    
    try:
        # Log completion
        StorageService.save_processing_log(
            db=db,
            file_id=file_id,
            stage='pipeline_complete',
            status='completed',
            message=f"Analysis complete: {report['verdict']} (Score: {report['overall_score']})"
        )
        
        return {
            'status': 'success',
            'file_id': file_id,
            'verdict': report['verdict']
        }
    finally:
        db.close()


# Define tasks
ingest_file = PythonOperator(
    task_id='ingest_file',
    python_callable=ingest_file_task,
    dag=dag,
    provide_context=True,
)

process_file = PythonOperator(
    task_id='process_file',
    python_callable=process_file_task,
    dag=dag,
    provide_context=True,
)

store_results = PythonOperator(
    task_id='store_results',
    python_callable=store_results_task,
    dag=dag,
    provide_context=True,
)

generate_report = PythonOperator(
    task_id='generate_report',
    python_callable=generate_report_task,
    dag=dag,
    provide_context=True,
)

log_completion = PythonOperator(
    task_id='log_completion',
    python_callable=log_completion_task,
    dag=dag,
    provide_context=True,
)

# Define task dependencies
ingest_file >> process_file >> store_results >> generate_report >> log_completion

# To trigger this DAG with a file:
# airflow dags trigger forensic_file_analysis --conf '{"file_path": "/path/to/file.jpg"}'
