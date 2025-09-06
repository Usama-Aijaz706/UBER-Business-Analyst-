# 🚀 Azure ML Workspace Deployment Guide
## Uber Ride Analytics 2024 - Professional Business Solution

This guide provides step-by-step instructions for deploying the Uber Ride Analytics solution to Azure ML workspace and running it in production.

---

## 📋 Prerequisites

### 1. Azure Account & Subscription
- Active Azure subscription
- Contributor or Owner access to Azure ML workspace
- Sufficient quota for compute resources

### 2. Azure ML Workspace Setup
- Azure ML workspace created
- Compute instance or cluster configured
- Storage account with blob container

### 3. Python Environment
- Python 3.8+ installed
- Azure ML SDK installed: `pip install azureml-core`
- Required packages from `requirements.txt`

---

## 🚀 Quick Start Deployment

### Step 1: Install Azure ML SDK
```bash
pip install azureml-core azureml-pipeline azureml-dataprep
```

### Step 2: Configure Azure ML Connection
```python
# Create config.py file
from azureml.core import Workspace

# Load workspace
ws = Workspace.from_config()

# Or create new workspace
ws = Workspace.create(
    name='uber-analytics-workspace',
    subscription_id='your-subscription-id',
    resource_group='your-resource-group',
    create_resource_group=True,
    location='eastus'
)
```

### Step 3: Upload Dataset to Azure ML
```python
# upload_dataset.py
from azureml.core import Workspace, Dataset
from azureml.core.datastore import Datastore

# Load workspace
ws = Workspace.from_config()

# Get default datastore
datastore = ws.get_default_datastore()

# Upload dataset
datastore.upload_files(
    files=['ncr_ride_bookings.csv'],
    target_path='uber-analytics/',
    overwrite=True
)

# Register dataset
dataset = Dataset.Tabular.from_delimited_files(
    path=datastore.path('uber-analytics/ncr_ride_bookings.csv')
)
dataset = dataset.register(
    workspace=ws,
    name='uber-ride-bookings-2024',
    description='Uber ride analytics dataset for 2024'
)
```

---

## 🔧 Detailed Deployment Steps

### 1. Environment Setup

#### Create Conda Environment
```bash
# Create environment file
conda env create -f environment.yml

# Activate environment
conda activate uber-analytics
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Azure ML Workspace Configuration

#### Create Workspace Configuration
```python
# config.py
from azureml.core import Workspace, Environment, Experiment
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.core.compute_target import ComputeTargetException

def setup_workspace():
    """Setup Azure ML workspace and compute resources."""
    
    # Load or create workspace
    try:
        ws = Workspace.from_config()
        print(f"✅ Workspace '{ws.name}' loaded successfully")
    except:
        print("⚠️ No workspace config found. Creating new workspace...")
        ws = Workspace.create(
            name='uber-analytics-workspace',
            subscription_id='your-subscription-id',
            resource_group='your-resource-group',
            create_resource_group=True,
            location='eastus'
        )
        ws.write_config()
        print(f"✅ Workspace '{ws.name}' created successfully")
    
    # Setup compute target
    compute_name = 'uber-analytics-cluster'
    
    try:
        compute_target = ws.compute_targets[compute_name]
        print(f"✅ Compute target '{compute_name}' found")
    except ComputeTargetException:
        print(f"⚠️ Creating compute target '{compute_name}'...")
        
        compute_config = AmlCompute.provisioning_configuration(
            vm_size='Standard_DS3_v2',
            max_nodes=4,
            min_nodes=0
        )
        
        compute_target = ComputeTarget.create(
            ws, 
            compute_name, 
            compute_config
        )
        compute_target.wait_for_completion(show_output=True)
        print(f"✅ Compute target '{compute_name}' created successfully")
    
    return ws, compute_target

if __name__ == "__main__":
    ws, compute = setup_workspace()
```

### 3. Data Pipeline Setup

#### Create Data Processing Pipeline
```python
# data_pipeline.py
from azureml.core import Workspace, Environment, Experiment
from azureml.pipeline.core import Pipeline, PipelineData
from azureml.pipeline.steps import PythonScriptStep
from azureml.core.runconfig import RunConfiguration

def create_data_pipeline(ws, compute_target):
    """Create data processing pipeline."""
    
    # Create pipeline data references
    raw_data = PipelineData('raw_data', datastore=ws.get_default_datastore())
    cleaned_data = PipelineData('cleaned_data', datastore=ws.get_default_datastore())
    eda_results = PipelineData('eda_results', datastore=ws.get_default_datastore())
    
    # Create environment
    env = Environment.from_conda_specification(
        name='uber-analytics-env',
        file_path='environment.yml'
    )
    
    # Create run configuration
    run_config = RunConfiguration()
    run_config.environment = env
    
    # Step 1: Data Exploration and Cleaning
    cleaning_step = PythonScriptStep(
        name='data_cleaning',
        script_name='01_data_exploration_cleaning.py',
        compute_target=compute_target,
        runconfig=run_config,
        inputs=[raw_data],
        outputs=[cleaned_data],
        arguments=[
            '--input_data', raw_data,
            '--output_data', cleaned_data
        ]
    )
    
    # Step 2: Exploratory Data Analysis
    eda_step = PythonScriptStep(
        name='exploratory_analysis',
        script_name='02_exploratory_data_analysis.py',
        compute_target=compute_target,
        runconfig=run_config,
        inputs=[cleaned_data],
        outputs=[eda_results],
        arguments=[
            '--input_data', cleaned_data,
            '--output_data', eda_results
        ]
    )
    
    # Create pipeline
    pipeline = Pipeline(workspace=ws, steps=[cleaning_step, eda_step])
    
    return pipeline

if __name__ == "__main__":
    ws, compute = setup_workspace()
    pipeline = create_data_pipeline(ws, compute)
    
    # Submit pipeline
    experiment = Experiment(ws, 'uber-analytics-pipeline')
    run = experiment.submit(pipeline)
    run.wait_for_completion(show_output=True)
```

### 4. Model Training & Deployment

#### Create ML Pipeline
```python
# ml_pipeline.py
from azureml.core import Workspace, Environment, Model
from azureml.core.model import InferenceConfig
from azureml.core.webservice import AciWebservice, AksWebservice
from azureml.pipeline.core import Pipeline, PipelineData
from azureml.pipeline.steps import PythonScriptStep

def create_ml_pipeline(ws, compute_target):
    """Create machine learning pipeline."""
    
    # Create pipeline data references
    cleaned_data = PipelineData('cleaned_data', datastore=ws.get_default_datastore())
    model_data = PipelineData('model_data', datastore=ws.get_default_datastore())
    
    # Create environment
    env = Environment.from_conda_specification(
        name='uber-analytics-ml-env',
        file_path='environment.yml'
    )
    
    # Step: Model Training
    training_step = PythonScriptStep(
        name='model_training',
        script_name='04_advanced_analytics.py',
        compute_target=compute_target,
        runconfig=run_config,
        inputs=[cleaned_data],
        outputs=[model_data],
        arguments=[
            '--input_data', cleaned_data,
            '--output_data', model_data,
            '--task', 'train_models'
        ]
    )
    
    # Create pipeline
    pipeline = Pipeline(workspace=ws, steps=[training_step])
    
    return pipeline

def deploy_model(ws, model_path):
    """Deploy trained model as web service."""
    
    # Register model
    model = Model.register(
        workspace=ws,
        model_path=model_path,
        model_name='uber-analytics-model'
    )
    
    # Create inference config
    inference_config = InferenceConfig(
        entry_script='score.py',
        environment=ws.environments['uber-analytics-ml-env']
    )
    
    # Deploy to ACI (for testing)
    deployment_config = AciWebservice.deploy_configuration(
        cpu_cores=1,
        memory_gb=1
    )
    
    service = Model.deploy(
        ws,
        'uber-analytics-service',
        [model],
        inference_config,
        deployment_config
    )
    
    service.wait_for_deployment(show_output=True)
    print(f"✅ Service deployed at: {service.scoring_uri}")
    
    return service
```

### 5. Dashboard Deployment

#### Deploy Streamlit Dashboard
```python
# deploy_dashboard.py
from azureml.core import Workspace, Environment
from azureml.core.compute import ComputeTarget
import subprocess
import os

def deploy_streamlit_dashboard(ws, compute_target):
    """Deploy Streamlit dashboard to Azure ML."""
    
    # Create scoring script
    scoring_script = '''
import streamlit as st
import pandas as pd
from azureml.core import Workspace, Dataset

# Load workspace and data
ws = Workspace.from_config()
dataset = Dataset.get_by_name(ws, 'uber-ride-bookings-2024')
df = dataset.to_pandas_dataframe()

# Run Streamlit app
if __name__ == "__main__":
    st.run("03_business_intelligence_dashboard.py")
'''
    
    with open('score.py', 'w') as f:
        f.write(scoring_script)
    
    # Deploy as web service
    from azureml.core.model import InferenceConfig
    from azureml.core.webservice import AciWebservice
    
    inference_config = InferenceConfig(
        entry_script='score.py',
        environment=ws.environments['uber-analytics-env']
    )
    
    deployment_config = AciWebservice.deploy_configuration(
        cpu_cores=2,
        memory_gb=4
    )
    
    service = Model.deploy(
        ws,
        'uber-analytics-dashboard',
        [model],
        inference_config,
        deployment_config
    )
    
    service.wait_for_deployment(show_output=True)
    print(f"✅ Dashboard deployed at: {service.scoring_uri}")
    
    return service
```

---

## 🚀 Production Deployment

### 1. Automated Pipeline

#### Create CI/CD Pipeline
```yaml
# azure-pipelines.yml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.8'
    addToPath: true

- script: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
  displayName: 'Install dependencies'

- script: |
    python config.py
    python data_pipeline.py
    python ml_pipeline.py
  displayName: 'Run ML pipeline'

- script: |
    python deploy_dashboard.py
  displayName: 'Deploy dashboard'
```

### 2. Monitoring & Logging

#### Add Monitoring
```python
# monitoring.py
from azureml.core import Workspace
from azureml.core.run import Run
import logging

def setup_monitoring(ws):
    """Setup monitoring and logging."""
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Setup Azure ML monitoring
    run = Run.get_context()
    
    # Log metrics
    run.log('total_records', len(df))
    run.log('success_rate', success_rate)
    run.log('total_revenue', total_revenue)
    
    # Log artifacts
    run.upload_file('cleaned_data.csv', 'output/uber_rides_cleaned.csv')
    run.upload_file('eda_report.txt', 'output/eda/eda_report.txt')
    
    logger.info("✅ Monitoring setup completed")
```

### 3. Performance Optimization

#### Optimize for Large Datasets
```python
# optimization.py
import pandas as pd
import dask.dataframe as dd

def optimize_data_processing(df):
    """Optimize data processing for large datasets."""
    
    # Use Dask for large datasets
    if len(df) > 100000:
        ddf = dd.from_pandas(df, npartitions=4)
        return ddf
    else:
        return df

def optimize_storage(df, output_path):
    """Optimize data storage."""
    
    # Save as parquet for better performance
    df.to_parquet(output_path, compression='snappy')
    
    # Save as partitioned parquet for very large datasets
    if len(df) > 1000000:
        df.to_parquet(
            output_path.replace('.parquet', '_partitioned'),
            partition_cols=['Month', 'Vehicle Type']
        )
```

---

## 📊 Running in Azure ML Workspace

### 1. Interactive Notebooks

#### Create Jupyter Notebook
```python
# In Azure ML Studio Notebook
from azureml.core import Workspace, Dataset
import pandas as pd

# Load workspace
ws = Workspace.from_config()

# Load dataset
dataset = Dataset.get_by_name(ws, 'uber-ride-bookings-2024')
df = dataset.to_pandas_dataframe()

# Run analysis
print(f"Dataset shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
```

### 2. Automated Runs

#### Schedule Pipeline
```python
# schedule_pipeline.py
from azureml.pipeline.core import ScheduleRecurrence, Schedule

def schedule_pipeline(ws, pipeline):
    """Schedule pipeline to run automatically."""
    
    # Create schedule
    schedule = Schedule.create(
        ws,
        name='uber-analytics-schedule',
        pipeline_id=pipeline.id,
        experiment_name='uber-analytics-pipeline',
        recurrence=ScheduleRecurrence.frequency(
            frequency='Week',
            interval=1
        )
    )
    
    print(f"✅ Pipeline scheduled: {schedule.name}")
    return schedule
```

### 3. Real-time Dashboard

#### Access Dashboard
```python
# access_dashboard.py
from azureml.core import Workspace
from azureml.core.webservice import Webservice

def access_dashboard(ws):
    """Access deployed dashboard."""
    
    # Get service
    service = Webservice(ws, 'uber-analytics-dashboard')
    
    # Get scoring URI
    scoring_uri = service.scoring_uri
    print(f"Dashboard URL: {scoring_uri}")
    
    # Test service
    response = service.run({'test': 'data'})
    print(f"Service response: {response}")
    
    return service
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Authentication Errors
```bash
# Solution: Login to Azure
az login
az account set --subscription <subscription-id>
```

#### 2. Compute Target Issues
```python
# Solution: Check compute status
compute_target = ws.compute_targets['compute-name']
print(f"Status: {compute_target.get_status()}")
print(f"Provisioning state: {compute_target.provisioning_state}")
```

#### 3. Environment Issues
```python
# Solution: Rebuild environment
env = Environment.from_conda_specification(
    name='uber-analytics-env',
    file_path='environment.yml'
)
env.register(ws)
```

#### 4. Memory Issues
```python
# Solution: Increase compute resources
compute_config = AmlCompute.provisioning_configuration(
    vm_size='Standard_DS4_v2',  # More memory
    max_nodes=8,
    min_nodes=1
)
```

---

## 📈 Performance Monitoring

### 1. Metrics Dashboard

#### Create Monitoring Dashboard
```python
# monitoring_dashboard.py
from azureml.core import Workspace
import plotly.graph_objects as go
import plotly.express as px

def create_monitoring_dashboard(ws):
    """Create monitoring dashboard."""
    
    # Get recent runs
    experiment = ws.experiments['uber-analytics-pipeline']
    runs = experiment.get_runs()
    
    # Extract metrics
    metrics = []
    for run in runs:
        metrics.append({
            'run_id': run.id,
            'success_rate': run.get_metrics()['success_rate'],
            'total_revenue': run.get_metrics()['total_revenue'],
            'timestamp': run.start_time
        })
    
    # Create dashboard
    df_metrics = pd.DataFrame(metrics)
    
    # Success rate trend
    fig1 = px.line(df_metrics, x='timestamp', y='success_rate')
    fig1.update_layout(title='Success Rate Trend')
    
    # Revenue trend
    fig2 = px.line(df_metrics, x='timestamp', y='total_revenue')
    fig2.update_layout(title='Revenue Trend')
    
    return fig1, fig2
```

### 2. Alerting

#### Setup Alerts
```python
# alerts.py
from azureml.core import Workspace
from azureml.core.run import Run

def setup_alerts(ws):
    """Setup performance alerts."""
    
    # Define thresholds
    SUCCESS_RATE_THRESHOLD = 0.65
    REVENUE_THRESHOLD = 1000000
    
    # Monitor metrics
    run = Run.get_context()
    
    success_rate = run.get_metrics()['success_rate']
    total_revenue = run.get_metrics()['total_revenue']
    
    # Check thresholds
    if success_rate < SUCCESS_RATE_THRESHOLD:
        print(f"⚠️ ALERT: Success rate {success_rate:.2%} below threshold {SUCCESS_RATE_THRESHOLD:.2%}")
    
    if total_revenue < REVENUE_THRESHOLD:
        print(f"⚠️ ALERT: Revenue ₹{total_revenue:,.0f} below threshold ₹{REVENUE_THRESHOLD:,.0f}")
```

---

## 🎯 Next Steps

### 1. Scale Up
- Deploy to AKS for production workloads
- Implement auto-scaling based on demand
- Add more advanced ML models

### 2. Integration
- Connect to real-time data sources
- Integrate with Power BI for executive dashboards
- Add API endpoints for external systems

### 3. Advanced Analytics
- Implement predictive analytics
- Add anomaly detection
- Create recommendation engines

---

## 📞 Support & Resources

### Documentation
- [Azure ML Documentation](https://docs.microsoft.com/en-us/azure/machine-learning/)
- [Azure ML Python SDK](https://docs.microsoft.com/en-us/python/api/overview/azure/ml/)
- [Streamlit Documentation](https://docs.streamlit.io/)

### Community
- [Azure ML Community](https://techcommunity.microsoft.com/t5/azure-machine-learning/bd-p/AzureMachineLearning)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/azure-machine-learning)

### Training
- [Azure ML Learning Path](https://docs.microsoft.com/en-us/learn/paths/build-ai-solutions-with-azure-ml-service/)
- [Microsoft Learn](https://docs.microsoft.com/en-us/learn/)

---

**🎉 Congratulations! You've successfully deployed a professional Uber Ride Analytics solution to Azure ML workspace.**

This solution provides:
- ✅ Automated data processing pipelines
- ✅ Interactive business intelligence dashboard
- ✅ Machine learning models and predictions
- ✅ Production-ready deployment
- ✅ Monitoring and alerting
- ✅ Scalable architecture

**Ready to transform your ride-sharing business with data-driven insights! 🚗📊**
