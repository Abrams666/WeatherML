import gradio as gr
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Get the base directory where the script is located
BASE_DIR = Path(__file__).parent.absolute()

# Configuration management
def load_config():
    config_path = BASE_DIR / 'config.json'
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "getData": {
                "station number": "466880",
                "start year": 2020,
                "start month": 1,
                "end year": 2023,
                "end month": 12,
                "download path": "./data",
                "year of today": "auto",
                "month of today": "auto",
                "test set ratio": 0.2
            }
        }

def save_config(station_num, start_year, start_month, end_year, end_month, download_path, test_ratio):
    config = {
        "getData": {
            "station number": str(station_num),
            "start year": int(start_year),
            "start month": int(start_month),
            "end year": int(end_year),
            "end month": int(end_month),
            "download path": download_path,
            "year of today": "auto",
            "month of today": "auto",
            "test set ratio": float(test_ratio)
        }
    }
    config_path = BASE_DIR / 'config.json'
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    return "✅ Configuration saved successfully!"

# Check if file exists
def check_file_exists(filepath):
    full_path = BASE_DIR / filepath
    if not full_path.exists():
        return False, f"❌ File not found: {full_path}"
    return True, str(full_path)

# Step execution functions
def run_get_data():
    script_path = "getData/getData.py"
    exists, full_path = check_file_exists(script_path)
    if not exists:
        return full_path
    
    try:
        result = subprocess.run(
            [sys.executable, full_path],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(BASE_DIR)
        )
        if result.returncode == 0:
            return f"✅ Data collection completed!\n\n{result.stdout}"
        else:
            return f"❌ Error occurred:\n\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "⏱️ Process timed out after 5 minutes"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def run_combine_csv():
    script_path = "dataProcessing/combineCSV.py"
    exists, full_path = check_file_exists(script_path)
    if not exists:
        return full_path
    
    try:
        result = subprocess.run(
            [sys.executable, full_path],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(BASE_DIR)
        )
        if result.returncode == 0:
            return f"✅ CSV files combined successfully!\n\n{result.stdout}"
        else:
            return f"❌ Error occurred:\n\n{result.stderr}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def run_standardize():
    script_path = "dataProcessing/standardize.py"
    exists, full_path = check_file_exists(script_path)
    if not exists:
        return full_path
    
    try:
        result = subprocess.run(
            [sys.executable, full_path],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(BASE_DIR)
        )
        if result.returncode == 0:
            return f"✅ Data standardization completed!\n\n{result.stdout}"
        else:
            return f"❌ Error occurred:\n\n{result.stderr}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def run_training(config_text):
    try:
        # Check if train.cpp exists
        cpp_path = BASE_DIR / "train" / "train.cpp"
        if not cpp_path.exists():
            return f"❌ File not found: {cpp_path}"
        
        # Create train directory if it doesn't exist
        train_dir = BASE_DIR / "train"
        train_dir.mkdir(exist_ok=True)
        
        # Save train config
        config_file = train_dir / "train_config.txt"
        with open(config_file, 'w') as f:
            f.write(config_text)
        
        # Compile C++ training
        train_exe = train_dir / "train.exe" if sys.platform == "win32" else train_dir / "train"
        compile_result = subprocess.run(
            ["g++", "-o", str(train_exe), str(cpp_path), "-std=c++17"],
            capture_output=True,
            text=True,
            cwd=str(BASE_DIR)
        )
        
        if compile_result.returncode != 0:
            return f"❌ Compilation error:\n\n{compile_result.stderr}"
        
        run_result = subprocess.run(
            [str(train_exe)],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=str(BASE_DIR)
        )
        
        if run_result.returncode == 0:
            return f"✅ Training completed!\n\n{run_result.stdout}"
        else:
            return f"❌ Training error:\n\n{run_result.stderr}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def run_full_pipeline(station_num, start_year, start_month, end_year, end_month, download_path, test_ratio, train_config, skip_data_collection):
    outputs = []
    
    # Step 1: Save config
    outputs.append("📝 Step 1: Saving configuration...")
    save_result = save_config(station_num, start_year, start_month, end_year, end_month, download_path, test_ratio)
    outputs.append(save_result)
    
    # Step 2: Get data (optional)
    if not skip_data_collection:
        outputs.append("\n📊 Step 2: Collecting data...")
        data_result = run_get_data()
        outputs.append(data_result)
        if "❌" in data_result:
            outputs.append("\n⚠️ Data collection failed. Continuing with existing data if available...")
    else:
        outputs.append("\n⏭️ Step 2: Skipping data collection (using existing data)")
    
    # Step 3: Combine CSV
    outputs.append("\n🔗 Step 3: Combining CSV files...")
    combine_result = run_combine_csv()
    outputs.append(combine_result)
    if "❌" in combine_result:
        outputs.append("\n❌ Pipeline stopped: CSV combination failed")
        return "\n".join(outputs)
    
    # Step 4: Standardize
    outputs.append("\n📐 Step 4: Standardizing data...")
    std_result = run_standardize()
    outputs.append(std_result)
    if "❌" in std_result:
        outputs.append("\n❌ Pipeline stopped: Standardization failed")
        return "\n".join(outputs)
    
    # Step 5: Train
    if train_config.strip():
        outputs.append("\n🎯 Step 5: Training model...")
        train_result = run_training(train_config)
        outputs.append(train_result)
    else:
        outputs.append("\n⏭️ Step 5: Skipping training (no configuration provided)")
    
    outputs.append("\n🎉 Full pipeline completed!")
    return "\n".join(outputs)

# Create Gradio interface
with gr.Blocks(theme=gr.themes.Soft(), title="Data Pipeline Manager") as demo:
    gr.Markdown("""
    # 🚀 Data Pipeline Manager
    ### Automated data collection, processing, and model training interface
    """)
    
    # Load initial config
    config = load_config()
    
    with gr.Tabs():
        # Configuration Tab
        with gr.Tab("⚙️ Configuration"):
            gr.Markdown("### Configure your data collection parameters")
            with gr.Row():
                with gr.Column():
                    station_input = gr.Textbox(
                        label="Station Number",
                        value=config.get("getData", {}).get("station number", "466880")
                    )
                    download_path_input = gr.Textbox(
                        label="Download Path",
                        value=config.get("getData", {}).get("download path", "./data")
                    )
                with gr.Column():
                    test_ratio_input = gr.Number(
                        label="Test Set Ratio (0-1)",
                        value=config.get("getData", {}).get("test set ratio", 0.2),
                        minimum=0,
                        maximum=1,
                        step=0.05
                    )
            
            gr.Markdown("#### Date Range")
            with gr.Row():
                with gr.Column():
                    start_year_input = gr.Number(
                        label="Start Year",
                        value=config.get("getData", {}).get("start year", 2020),
                        precision=0
                    )
                    start_month_input = gr.Number(
                        label="Start Month",
                        value=config.get("getData", {}).get("start month", 1),
                        precision=0,
                        minimum=1,
                        maximum=12
                    )
                with gr.Column():
                    end_year_input = gr.Number(
                        label="End Year",
                        value=config.get("getData", {}).get("end year", 2023),
                        precision=0
                    )
                    end_month_input = gr.Number(
                        label="End Month",
                        value=config.get("getData", {}).get("end month", 12),
                        precision=0,
                        minimum=1,
                        maximum=12
                    )
            
            save_config_btn = gr.Button("💾 Save Configuration", variant="primary")
            config_output = gr.Textbox(label="Status", lines=2)
            
            save_config_btn.click(
                save_config,
                inputs=[station_input, start_year_input, start_month_input, end_year_input, end_month_input, download_path_input, test_ratio_input],
                outputs=config_output
            )
        
        # Individual Steps Tab
        with gr.Tab("🔧 Run Individual Steps"):
            gr.Markdown("### Execute pipeline steps individually")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### Step 1: Get Data")
                    get_data_btn = gr.Button("📊 Collect Data", variant="secondary")
                    get_data_output = gr.Textbox(label="Output", lines=8)
                    
                    gr.Markdown("#### Step 2: Combine CSV")
                    combine_btn = gr.Button("🔗 Combine CSV Files", variant="secondary")
                    combine_output = gr.Textbox(label="Output", lines=8)
                
                with gr.Column():
                    gr.Markdown("#### Step 3: Standardize")
                    standardize_btn = gr.Button("📐 Standardize Data", variant="secondary")
                    standardize_output = gr.Textbox(label="Output", lines=8)
                    
                    gr.Markdown("#### Step 4: Train Model")
                    train_config_input = gr.Textbox(
                        label="Training Configuration",
                        lines=6,
                        placeholder="Enter training parameters here..."
                    )
                    train_btn = gr.Button("🎯 Train Model", variant="secondary")
                    train_output = gr.Textbox(label="Output", lines=8)
            
            get_data_btn.click(run_get_data, outputs=get_data_output)
            combine_btn.click(run_combine_csv, outputs=combine_output)
            standardize_btn.click(run_standardize, outputs=standardize_output)
            train_btn.click(run_training, inputs=train_config_input, outputs=train_output)
        
        # Full Pipeline Tab
        with gr.Tab("🚀 Run Full Pipeline"):
            gr.Markdown("### Execute the complete pipeline in one click")
            gr.Markdown("""
            This will run all steps sequentially:
            1. Save configuration
            2. Collect data (using Selenium & ChromeDriver)
            3. Combine CSV files
            4. Standardize data
            5. Train model
            """)
            
            with gr.Column():
                pipeline_station = gr.Textbox(label="Station Number", value=config.get("getData", {}).get("station number", "466880"))
                
                gr.Markdown("#### Date Range")
                with gr.Row():
                    pipeline_start_year = gr.Number(label="Start Year", value=config.get("getData", {}).get("start year", 2020), precision=0)
                    pipeline_start_month = gr.Number(label="Start Month", value=config.get("getData", {}).get("start month", 1), precision=0, minimum=1, maximum=12)
                with gr.Row():
                    pipeline_end_year = gr.Number(label="End Year", value=config.get("getData", {}).get("end year", 2023), precision=0)
                    pipeline_end_month = gr.Number(label="End Month", value=config.get("getData", {}).get("end month", 12), precision=0, minimum=1, maximum=12)
                
                pipeline_path = gr.Textbox(label="Download Path", value=config.get("getData", {}).get("download path", "./data"))
                pipeline_test_ratio = gr.Number(label="Test Set Ratio", value=config.get("getData", {}).get("test set ratio", 0.2), minimum=0, maximum=1, step=0.05)
                
                skip_data_collection = gr.Checkbox(
                    label="Skip Data Collection (use existing CSV files)",
                    value=False,
                    info="Check this if you already have the raw CSV files downloaded"
                )
                pipeline_train_config = gr.Textbox(
                    label="Training Configuration",
                    lines=6,
                    placeholder="Enter training parameters..."
                )
                
                run_pipeline_btn = gr.Button("🚀 Run Complete Pipeline", variant="primary", size="lg")
                pipeline_output = gr.Textbox(label="Pipeline Output", lines=20)
            
            run_pipeline_btn.click(
                run_full_pipeline,
                inputs=[pipeline_station, pipeline_start_year, pipeline_start_month, pipeline_end_year, pipeline_end_month, pipeline_path, pipeline_test_ratio, pipeline_train_config, skip_data_collection],
                outputs=pipeline_output
            )
        
        # Help Tab
        with gr.Tab("❓ Help"):
            gr.Markdown("""
            ## 📖 User Guide
            
            ### Setup Instructions
            1. **Install ChromeDriver**: Download from https://chromedriver.chromium.org/ and place in your system PATH
            2. **Install Dependencies**: `pip install selenium pandas gradio`
            3. **Configure Settings**: Go to Configuration tab and set your parameters
            4. **Choose Workflow**:
               - Use **Individual Steps** for testing or debugging specific parts
               - Use **Full Pipeline** to run everything automatically
            
            ### Configuration Parameters
            - **Station Number**: Weather station identifier (e.g., "466880")
            - **Start Year/Month**: Beginning of data collection period
            - **End Year/Month**: End of data collection period
            - **Download Path**: Directory where raw CSV files will be stored
            - **Test Set Ratio**: Proportion of data reserved for testing (0-1, typically 0.2)
            
            ### Pipeline Steps
            1. **Get Data**: Uses Selenium to automatically download weather data from CWA website
            2. **Combine CSV**: Merges monthly CSV files and splits into train/test sets
            3. **Standardize**: Normalizes data using z-score standardization
            4. **Train Model**: Compiles and runs the C++ training program
            
            ### Taiwan Weather Stations
            Common station numbers:
            - 466880: Taipei
            - 466900: Taoyuan
            - 467410: Taichung
            - 467440: Tainan
            - 467590: Kaohsiung
            
            ### Tips
            - Always save configuration before running data collection
            - Data collection can take several minutes depending on date range
            - Check outputs for error messages if a step fails
            - Ensure ChromeDriver version matches your Chrome browser version
            - You can run individual steps multiple times if needed
            """)

if __name__ == "__main__":
    demo.launch(share=False, server_name="127.0.0.1", server_port=7860)