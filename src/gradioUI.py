import gradio as gr
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Get the base directory where the script is located
BASE_DIR = Path(__file__).parent.absolute()
# Config is in parent directory (outside src/)
CONFIG_PATH = BASE_DIR.parent / 'config.json'

# Configuration management
def load_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
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
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)
    return f"✅ 設定已成功儲存至 {CONFIG_PATH}！"

# Check if file exists
def check_file_exists(filepath):
    full_path = BASE_DIR / filepath
    if not full_path.exists():
        return False, f"❌ 找不到檔案：{full_path}"
    return True, full_path

# Step execution functions
def run_get_data():
    script_path = "getData/getData.py"
    exists, full_path = check_file_exists(script_path)
    if not exists:
        return full_path
    
    try:
        # Run from parent directory so scripts can find ./config.json
        result = subprocess.run(
            [sys.executable, str(full_path)],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(BASE_DIR.parent)
        )
        if result.returncode == 0:
            return f"✅ 資料收集完成！\n\n{result.stdout}"
        else:
            return f"❌ 發生錯誤：\n\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "⏱️ 程序執行逾時（5分鐘）"
    except Exception as e:
        return f"❌ 錯誤：{str(e)}"

def run_combine_csv():
    script_path = "dataProcessing/combineCSV.py"
    exists, full_path = check_file_exists(script_path)
    if not exists:
        return full_path
    
    try:
        # Run from parent directory so scripts can find ./config.json
        result = subprocess.run(
            [sys.executable, str(full_path)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(BASE_DIR.parent)
        )
        if result.returncode == 0:
            return f"✅ CSV 檔案合併成功！\n\n{result.stdout}"
        else:
            return f"❌ 發生錯誤：\n\n{result.stderr}"
    except Exception as e:
        return f"❌ 錯誤：{str(e)}"

def run_standardize():
    script_path = "dataProcessing/standardize.py"
    exists, full_path = check_file_exists(script_path)
    if not exists:
        return full_path
    
    # Check if required input file exists
    try:
        config = load_config()
        station_num = config.get("getData", {}).get("station number", "")
        data_path = config.get("getData", {}).get("download path", "./data")
        expected_file = Path(BASE_DIR.parent) / data_path / f"data{station_num}.csv"
        
        if not expected_file.exists():
            # Check if dataFile exists instead
            alt_file = Path(BASE_DIR.parent) / data_path / f"dataFile{station_num}.csv"
            if alt_file.exists():
                return f"""❌ 檔案命名不匹配！

standardize.py 預期：data{station_num}.csv
但 combineCSV.py 建立：dataFile{station_num}.csv

另外，資料結構也不匹配：
- combineCSV.py 建立分開的檔案（dataFile + rainDataFile）
- standardize.py 預期一個包含所有欄位（包括 'Precp'）的檔案

您的團隊需要決定：
選項 1：修改 combineCSV.py 以建立包含所有欄位的合併檔案
選項 2：修改 standardize.py 以處理分開的檔案
選項 3：跳過 standardize.py，因為 combineCSV.py 已經建立 _std.csv 檔案

檢查您的 data 資料夾 - combineCSV.py 可能已經建立標準化檔案！
尋找：dataFile{station_num}_std.csv 和 rainDataFile{station_num}_std.csv"""
            else:
                return f"❌ 找不到所需的輸入檔案：{expected_file}\n\n請先執行「合併 CSV」步驟！"
    except Exception as e:
        pass  # Continue anyway
    
    try:
        # Run from parent directory so scripts can find ./config.json
        result = subprocess.run(
            [sys.executable, str(full_path)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(BASE_DIR.parent)
        )
        if result.returncode == 0:
            return f"✅ 資料標準化完成！\n\n{result.stdout}"
        else:
            error_msg = result.stderr
            if "KeyError: 'Precp'" in error_msg:
                return f"""❌ 欄位不匹配錯誤！

standardize.py 正在尋找 'Precp' 欄位，但 CSV 檔案中沒有。

這是因為：
- combineCSV.py 建立兩個分開的檔案：
  • dataFile{station_num}.csv（氣象資料，沒有 Precp）
  • rainDataFile{station_num}.csv（只有 Precp 欄位）
- standardize.py 預期一個包含所有欄位的檔案

好消息：combineCSV.py 已經建立標準化檔案！
檢查您的 data 資料夾中的這些檔案：
  • dataFile{station_num}_std.csv
  • rainDataFile{station_num}_std.csv

您可能根本不需要執行 standardize.py！🎉

原始錯誤：
{error_msg}"""
            return f"❌ 發生錯誤：\n\n{error_msg}"
    except Exception as e:
        return f"❌ 錯誤：{str(e)}"

def run_training(config_text):
    try:
        # Check if train.cpp exists
        cpp_path = BASE_DIR / "train" / "train.cpp"
        if not cpp_path.exists():
            return f"❌ 找不到檔案：{cpp_path}", None
        
        # Check if required input files exist
        config = load_config()
        station_num = config.get("getData", {}).get("station number", "")
        data_path = config.get("getData", {}).get("download path", "./data")
        
        train_data_file = Path(BASE_DIR.parent) / data_path / f"trainSetDataFile{station_num}_std.csv"
        train_rain_file = Path(BASE_DIR.parent) / data_path / f"trainSetRainDataFile{station_num}_std.csv"
        
        if not train_data_file.exists():
            return f"❌ 找不到訓練資料：{train_data_file}\n\n請先執行「合併 CSV」步驟！", None
        if not train_rain_file.exists():
            return f"❌ 找不到訓練降雨資料：{train_rain_file}\n\n請先執行「合併 CSV」步驟！", None
        
        # Create train directory if it doesn't exist
        train_dir = BASE_DIR / "train"
        train_dir.mkdir(exist_ok=True)
        
        # Compile C++ training
        train_exe = train_dir / "train.exe" if sys.platform == "win32" else train_dir / "train"
        compile_result = subprocess.run(
            ["g++", "-o", str(train_exe), str(cpp_path), "-std=c++17"],
            capture_output=True,
            text=True,
            cwd=str(train_dir)
        )
        
        if compile_result.returncode != 0:
            return f"❌ 編譯錯誤：\n\n{compile_result.stderr}", None
        
        # Run from train directory (so ../../data paths work correctly)
        run_result = subprocess.run(
            [str(train_exe.name)],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=str(train_dir)
        )
        
        weight_file = Path(BASE_DIR.parent) / data_path / "weight.csv"
        
        if run_result.returncode == 0:
            output = f"✅ 訓練完成！\n\n{run_result.stdout}"
            
            # Return the weight file for download
            if weight_file.exists():
                output += f"\n\n📁 權重檔案建立成功！"
                return output, str(weight_file)
            else:
                output += f"\n\n⚠️ 在預期位置找不到權重檔案：{weight_file}"
                return output, None
        else:
            return f"❌ 訓練錯誤：\n\n{run_result.stderr}\n\n標準輸出：\n{run_result.stdout}", None
    except subprocess.TimeoutExpired:
        return "⏱️ 訓練逾時（10分鐘）", None
    except Exception as e:
        return f"❌ 錯誤：{str(e)}", None

def run_full_pipeline(station_num, start_year, start_month, end_year, end_month, download_path, test_ratio, train_config, skip_data_collection, skip_training):
    outputs = []
    weight_file = None
    
    # Step 1: Save config
    outputs.append("📝 步驟 1：儲存設定...")
    save_result = save_config(station_num, start_year, start_month, end_year, end_month, download_path, test_ratio)
    outputs.append(save_result)
    
    # Step 2: Get data (optional)
    if not skip_data_collection:
        outputs.append("\n📊 步驟 2：收集資料...")
        data_result = run_get_data()
        outputs.append(data_result)
        if "❌" in data_result:
            outputs.append("\n⚠️ 資料收集失敗。如果有現有資料，將繼續執行...")
    else:
        outputs.append("\n⏭️ 步驟 2：跳過資料收集（使用現有資料）")
    
    # Step 3: Combine CSV (includes standardization)
    outputs.append("\n🔗 步驟 3：合併 CSV 檔案並標準化...")
    combine_result = run_combine_csv()
    outputs.append(combine_result)
    if "❌" in combine_result:
        outputs.append("\n❌ 流程中斷：CSV 合併失敗")
        return "\n".join(outputs), None
    
    outputs.append("\n✅ 資料處理完成！已建立檔案：")
    outputs.append(f"   • dataFile{station_num}_std.csv")
    outputs.append(f"   • rainDataFile{station_num}_std.csv")
    outputs.append(f"   • trainSetDataFile{station_num}_std.csv")
    outputs.append(f"   • testSetDataFile{station_num}_std.csv")
    
    # Step 4: Train (optional)
    if not skip_training:
        outputs.append("\n🎯 步驟 4：訓練模型...")
        train_result, weight_file = run_training(train_config)
        outputs.append(train_result)
    else:
        outputs.append("\n⏭️ 步驟 4：跳過訓練（依要求）")
    
    outputs.append("\n🎉 流程完成！")
    return "\n".join(outputs), weight_file

# Create Gradio interface
with gr.Blocks(theme=gr.themes.Soft(), title="資料流程管理系統") as demo:
    gr.Markdown("""
    # 🚀 資料流程管理系統
    ### 自動化資料收集、處理與模型訓練介面
    """)
    
    # Load initial config
    config = load_config()
    
    with gr.Tabs():
        # Configuration Tab
        with gr.Tab("⚙️ 設定"):
            gr.Markdown("### 設定您的資料收集參數")
            with gr.Row():
                with gr.Column():
                    station_input = gr.Textbox(
                        label="測站編號",
                        value=config.get("getData", {}).get("station number", "466880")
                    )
                    download_path_input = gr.Textbox(
                        label="下載路徑",
                        value=config.get("getData", {}).get("download path", "./data")
                    )
                with gr.Column():
                    test_ratio_input = gr.Number(
                        label="測試集比例 (0-1)",
                        value=config.get("getData", {}).get("test set ratio", 0.2),
                        minimum=0,
                        maximum=1,
                        step=0.05
                    )
            
            gr.Markdown("#### 日期範圍")
            with gr.Row():
                with gr.Column():
                    start_year_input = gr.Number(
                        label="開始年份",
                        value=config.get("getData", {}).get("start year", 2020),
                        precision=0
                    )
                    start_month_input = gr.Number(
                        label="開始月份",
                        value=config.get("getData", {}).get("start month", 1),
                        precision=0,
                        minimum=1,
                        maximum=12
                    )
                with gr.Column():
                    end_year_input = gr.Number(
                        label="結束年份",
                        value=config.get("getData", {}).get("end year", 2023),
                        precision=0
                    )
                    end_month_input = gr.Number(
                        label="結束月份",
                        value=config.get("getData", {}).get("end month", 12),
                        precision=0,
                        minimum=1,
                        maximum=12
                    )
            
            save_config_btn = gr.Button("💾 儲存設定", variant="primary")
            config_output = gr.Textbox(label="狀態", lines=2)
            
            save_config_btn.click(
                save_config,
                inputs=[station_input, start_year_input, start_month_input, end_year_input, end_month_input, download_path_input, test_ratio_input],
                outputs=config_output
            )
        
        # Individual Steps Tab
        with gr.Tab("🔧 執行個別步驟"):
            gr.Markdown("### 個別執行流程步驟")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### 步驟 1：取得資料")
                    gr.Markdown("*使用 Selenium 從中央氣象署網站下載氣象資料*")
                    get_data_btn = gr.Button("📊 收集資料", variant="secondary")
                    get_data_output = gr.Textbox(label="輸出", lines=8)
                    
                    gr.Markdown("#### 步驟 2：合併 CSV 與標準化")
                    gr.Markdown("*合併每月 CSV 並建立標準化版本*")
                    combine_btn = gr.Button("🔗 合併與標準化", variant="secondary")
                    combine_output = gr.Textbox(label="輸出", lines=8)
                
                with gr.Column():
                    gr.Markdown("#### 步驟 3：訓練模型（選用）")
                    gr.Markdown("*編譯並執行 train.cpp*")
                    train_config_input = gr.Textbox(
                        label="訓練設定（未使用）",
                        lines=2,
                        placeholder="留空 - train.cpp 使用硬編碼設定",
                        visible=False
                    )
                    train_btn = gr.Button("🎯 訓練模型", variant="secondary")
                    train_output = gr.Textbox(label="輸出", lines=8)
                    train_download = gr.File(label="下載 weight.csv", visible=True)
                    
                    gr.Markdown("#### ℹ️ 注意")
                    gr.Markdown("*不需要 standardize.py - combineCSV.py 已建立 _std.csv 檔案*")
            
            get_data_btn.click(run_get_data, outputs=get_data_output)
            combine_btn.click(run_combine_csv, outputs=combine_output)
            train_btn.click(run_training, inputs=train_config_input, outputs=[train_output, train_download])
        
        # Full Pipeline Tab
        with gr.Tab("🚀 執行完整流程"):
            gr.Markdown("### 一鍵執行完整流程")
            gr.Markdown("""
            將依序執行所有步驟：
            1. 儲存設定
            2. 收集資料（選用 - 使用 Selenium 與 ChromeDriver）
            3. 合併 CSV 檔案與標準化資料
            4. 訓練模型（選用）
            
            **注意：** combineCSV.py 已經建立標準化檔案（_std.csv），因此不需要 standardize.py！
            """)
            
            with gr.Column():
                pipeline_station = gr.Textbox(label="測站編號", value=config.get("getData", {}).get("station number", "466880"))
                
                gr.Markdown("#### 日期範圍")
                with gr.Row():
                    pipeline_start_year = gr.Number(label="開始年份", value=config.get("getData", {}).get("start year", 2020), precision=0)
                    pipeline_start_month = gr.Number(label="開始月份", value=config.get("getData", {}).get("start month", 1), precision=0, minimum=1, maximum=12)
                with gr.Row():
                    pipeline_end_year = gr.Number(label="結束年份", value=config.get("getData", {}).get("end year", 2023), precision=0)
                    pipeline_end_month = gr.Number(label="結束月份", value=config.get("getData", {}).get("end month", 12), precision=0, minimum=1, maximum=12)
                
                pipeline_path = gr.Textbox(label="下載路徑", value=config.get("getData", {}).get("download path", "./data"))
                pipeline_test_ratio = gr.Number(label="測試集比例", value=config.get("getData", {}).get("test set ratio", 0.2), minimum=0, maximum=1, step=0.05)
                
                with gr.Row():
                    skip_data_collection = gr.Checkbox(
                        label="跳過資料收集",
                        value=False,
                        info="如果您已有原始 CSV 檔案請勾選"
                    )
                    skip_training = gr.Checkbox(
                        label="跳過訓練",
                        value=True,
                        info="如果您只需要資料處理請勾選"
                    )
                
                pipeline_train_config = gr.Textbox(
                    label="訓練設定",
                    lines=2,
                    placeholder="未使用 - train.cpp 使用硬編碼設定",
                    visible=False
                )
                
                run_pipeline_btn = gr.Button("🚀 執行流程", variant="primary", size="lg")
                pipeline_output = gr.Textbox(label="流程輸出", lines=20)
                pipeline_weight_download = gr.File(label="下載 weight.csv", visible=True)
            
            run_pipeline_btn.click(
                run_full_pipeline,
                inputs=[pipeline_station, pipeline_start_year, pipeline_start_month, pipeline_end_year, pipeline_end_month, pipeline_path, pipeline_test_ratio, pipeline_train_config, skip_data_collection, skip_training],
                outputs=[pipeline_output, pipeline_weight_download]
            )
        
        # Help Tab
        with gr.Tab("❓ 說明"):
            gr.Markdown("""
            ## 📖 使用指南
            
            ### 安裝步驟
            1. **安裝 ChromeDriver**：從 https://chromedriver.chromium.org/ 下載並放置在系統 PATH 中
            2. **安裝相依套件**：`pip install selenium pandas gradio`
            3. **設定參數**：前往「設定」分頁設定您的參數
            4. **選擇工作流程**：
               - 使用「執行個別步驟」進行測試或除錯特定部分
               - 使用「執行完整流程」自動執行所有步驟
            
            ### 設定參數
            - **測站編號**：氣象測站識別碼（例如："466880"）
            - **開始年份/月份**：資料收集期間的開始
            - **結束年份/月份**：資料收集期間的結束
            - **下載路徑**：原始 CSV 檔案儲存的目錄
            - **測試集比例**：保留用於測試的資料比例（0-1，通常為 0.2）
            
            ### 流程步驟（實際工作流程）
            1. **取得資料**：使用 Selenium 從中央氣象署網站下載氣象資料
            2. **合併 CSV**：合併每月 CSV 檔案、建立訓練/測試分割，並標準化資料
               - 建立：dataFile_std.csv、trainSetDataFile_std.csv、testSetDataFile_std.csv 等
               - ✅ 標準化已在此處完成！
            3. **訓練模型**（選用）：編譯並執行 C++ 訓練程式
            
            ### 台灣氣象測站
            常用測站編號：
            - 466880：台北
            - 466900：桃園
            - 467050：新竹
            - 467410：台中
            - 467440：台南
            - 467590：高雄
            
            ### 提示
            - 如果您已有原始的每月 CSV 檔案，請勾選「跳過資料收集」
            - 如果您只需要資料處理，請勾選「跳過訓練」
            - 資料收集可能需要幾分鐘，取決於日期範圍
            - 確保 ChromeDriver 版本與您的 Chrome 瀏覽器版本相符
            - 執行 combineCSV 後，檢查您的 data 資料夾中的 _std.csv 檔案
            """)

if __name__ == "__main__":
    demo.launch(share=False, server_name="127.0.0.1", server_port=7860, inbrowser=True)