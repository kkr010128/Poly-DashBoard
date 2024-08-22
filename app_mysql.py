from flask import Flask, render_template, jsonify
import pymysql
import json
import os
import psutil
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)

previous_net_io = psutil.net_io_counters()

# 데이터베이스 연결 및 데이터 가져오기 함수
def get_data():
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            db='DATABASE_NAME',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM polygon_manager')
        rows = cursor.fetchall()
        conn.close()
        return rows
    except pymysql.MySQLError as e:
        print(f"Connection Failed: {e}")
        return []

def get_model_counts(data):
    all_models = []
    for row in data:
        models = json.loads(row['allowModels'])
        all_models.extend(models)
    model_counts = {model: all_models.count(model) for model in set(all_models)}
    return model_counts

def get_user_counts(data):
    discord_ids = set()
    for row in data:
        discord_ids.add(row['discordID'])
    return len(discord_ids)

def get_folder_count(directory):
    if not os.path.exists(directory):
        print(f"Directory does not exist: {directory}")
        return 0
    try:
        return len([name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))])
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 0
    
def get_dict_model_counts(data):
    all_models = []
    for row in data:
        models = json.loads(row['allowModels'])
        all_models.extend(models)
    dict_model_counts = {model: all_models.count(model) for model in set(all_models) if all_models.count(model) > 1}
    return dict_model_counts

def get_network_stats():
    global previous_net_io
    current_net_io = psutil.net_io_counters()
    bytes_sent_per_sec = current_net_io.bytes_sent - previous_net_io.bytes_sent
    bytes_recv_per_sec = current_net_io.bytes_recv - previous_net_io.bytes_recv
    previous_net_io = current_net_io

    # Convert to kbps
    bits_sent_kbps = (bytes_sent_per_sec * 8) / 1_000
    bits_recv_kbps = (bytes_recv_per_sec * 8) / 1_000

    return {
        'kbps_sent': f"{bits_sent_kbps:.2f}",
        'kbps_recv': f"{bits_recv_kbps:.2f}"
    }

def get_system_performance():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    return {
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage
    }

@app.route('/')
def index():
    data = get_data()
    model_counts = get_model_counts(data)
    model_counts_json = json.dumps(model_counts)
    user_counts = get_user_counts(data)
    dict_model_counts = get_dict_model_counts(data)
    
    
    # 웬만하면 절대 경로 사용
    model_directory_path = os.path.abspath("/Users/kkr010128/Desktop/Resource-Manager/models")
    dummy_directory_path = os.path.abspath("/Users/kkr010128/Desktop/Resource-Manager/models_dummy")

    # 현재 작업 디렉토리 로그로 출력
    print(f"Current working directory: {os.getcwd()}")
    print(f"Model directory path: {model_directory_path}")
    print(f"Dummy directory path: {dummy_directory_path}")

    uploaded_rsc_cnt = get_folder_count(model_directory_path) # 디렉토리 내 리소스 총 개수
    dummy_rsc_cnt = get_folder_count(dummy_directory_path) # 디렉토리 내 더미리소스 총 개수
    license_cnt = len(data) # 등록된 라이센스 개수
    license_rsc = len(model_counts) # 라이센스에 등록된 리소스 개수(중복 제외)
    assigned_rsc = sum(model_counts.values()) # 라이센스에 할당 된 리소스 총 개수(중복 허용)
    

    network_stats = get_network_stats()
    system_performance = get_system_performance()

    return render_template('index.html', 
                            model_counts=model_counts_json,
                            uploaded_rsc_cnt=uploaded_rsc_cnt,
                            dummy_rsc_cnt=dummy_rsc_cnt,
                            license_cnt=license_cnt, 
                            license_rsc=license_rsc,
                            assigned_rsc=assigned_rsc,
                            network_stats=network_stats,
                            system_performance=system_performance,
                            user_counts=user_counts,
                            dict_model_counts = json.dumps(dict_model_counts)
                            
                            )

@app.route('/api/stats')
def api_stats():
    network_stats = get_network_stats()
    system_performance = get_system_performance()
    return jsonify({
        'network_stats': network_stats,
        'system_performance': system_performance
    })


def get_db_engine():
    user = 'root'
    password = ''
    host = 'localhost'
    db = 'DATABASE_NAME'
    return create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db}', echo=True)

@app.route('/api/chart-data')
def get_chart_data():
    engine = get_db_engine()
    df = pd.read_sql_query("SELECT api_name, access_time FROM license_log", engine)
    df['access_time'] = pd.to_datetime(df['access_time'], errors='coerce')
    df = df.dropna(subset=['access_time'])
    df['time_block'] = df['access_time'].dt.hour // 4

    # API별 접근 횟수 집계
    api_counts = df.groupby(['time_block', 'api_name']).size().unstack(fill_value=0)

    # 데이터 형식 변경
    labels = ['0-4', '4-8', '8-12', '12-16', '16-20', '20-24']
    data = {api: api_counts[api].reindex(range(6), fill_value=0).tolist() for api in api_counts.columns}
    
    return jsonify({'labels': labels, 'data': data})

if __name__ == '__main__':
    app.run(debug=True, port=PORT_NUMBER)