import pymysql
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# MySQL 연결 설정
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # 비밀번호가 없는 경우
    'database': 'kkr010128'
}

# 로그 테이블 생성 함수
def create_log_table():
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS license_log (
        id INT AUTO_INCREMENT PRIMARY KEY,
        api_name VARCHAR(50),
        access_time DATETIME
    )
    """)
    conn.commit()
    conn.close()

# log_down 함수
def log_down():
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    access_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO license_log (api_name, access_time) VALUES (%s, %s)", ('download', access_time))
    conn.commit()
    conn.close()

# log_check 함수
def log_check():
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    access_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO license_log (api_name, access_time) VALUES (%s, %s)", ('check_license', access_time))
    conn.commit()
    conn.close()

# 방사형 차트 생성 함수
def generate_radar_chart():
    conn = pymysql.connect(**db_config)
    df = pd.read_sql_query("SELECT api_name, access_time FROM license_log", conn)
    df['access_time'] = pd.to_datetime(df['access_time'])
    df['time_block'] = df['access_time'].dt.hour // 4

    # API별 접근 횟수 집계
    api_counts = df.groupby(['time_block', 'api_name']).size().unstack(fill_value=0)

    # 방사형 차트 생성
    labels = ['0-4', '4-8', '8-12', '12-16', '16-20', '20-24']
    num_vars = len(labels)

    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(12, 8), subplot_kw=dict(polar=True))

    for api in api_counts.columns:
        values = api_counts[api].reindex(range(6), fill_value=0).tolist()
        values += values[:1]
        ax.plot(angles, values, label=api)
        ax.fill(angles, values, alpha=0.25)

    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])  # 마지막 각도를 제외하여 길이를 맞춤
    ax.set_xticklabels(labels)

    plt.title('TEST')
    plt.legend(title='API Name')
    plt.savefig('test.png')  # 파일 저장 경로 변경
    conn.close()

# 테스트 데이터를 삽입하는 함수
def insert_test_data():
    test_data = [
        # 기존 테스트 데이터
        ('check_license', '2023-06-06 00:26:00'),
        ('download', '2023-06-06 00:26:00'),
        ('download', '2023-06-06 00:26:00'),
        ('download', '2023-06-06 00:26:00'),
        ('download', '2023-06-06 04:24:00'),
        ('check_license', '2023-06-06 04:24:00'),
        ('download', '2023-06-06 04:24:00'),
        ('download', '2023-06-06 04:24:00'),
        ('download', '2023-06-06 07:02:00'),
        ('check_license', '2023-06-06 07:02:00'),
        ('download', '2023-06-06 07:02:00'),
        ('download', '2023-06-06 07:02:00'),
        ('download', '2023-06-06 07:03:00'),
        ('download', '2023-06-06 07:04:00'),
        ('check_license', '2023-06-06 07:04:00'),
        ('download', '2023-06-06 07:04:00'),
        ('download', '2023-06-06 08:55:00'),
        ('check_license', '2023-06-06 08:55:00'),

        # 새로운 테스트 데이터
        ('check_license', '2024-05-30 16:12:00'),
        ('download', '2024-05-30 16:12:00'),
        ('download', '2024-05-30 16:12:00'),
        ('download', '2024-05-30 16:12:00'),
        ('download', '2024-05-30 16:13:00'),
        ('download', '2024-05-30 16:13:00'),
        ('download', '2024-05-30 16:13:00'),
        ('download', '2024-05-30 16:13:00'),
        ('download', '2024-05-30 16:13:00'),
        ('check_license', '2024-05-30 23:14:00'),
        ('download', '2024-05-30 23:14:00'),
        ('download', '2024-05-30 23:14:00'),
        ('check_license', '2024-05-30 23:44:00'),
        ('download', '2024-05-30 23:44:00'),
        ('download', '2024-05-30 23:44:00'),
        ('check_license', '2024-05-30 23:49:00'),
        ('download', '2024-05-30 23:49:00'),
        ('download', '2024-05-30 23:49:00'),
        ('check_license', '2024-05-31 00:04:00'),
        ('download', '2024-05-31 00:04:00'),
        ('download', '2024-05-31 00:04:00'),
        ('check_license', '2024-05-31 00:16:00'),
        ('download', '2024-05-31 00:16:00'),
        ('download', '2024-05-31 00:16:00'),
        ('check_license', '2024-05-31 01:56:00'),
        ('download', '2024-05-31 01:56:00'),
        ('download', '2024-05-31 01:56:00'),
        ('download', '2024-05-31 01:56:00'),
        ('download', '2024-05-31 01:56:00'),
        ('download', '2024-05-31 01:56:00'),
        ('download', '2024-05-31 01:57:00'),
        ('check_license', '2024-05-31 01:59:00'),
        ('download', '2024-05-31 01:59:00'),
        ('download', '2024-05-31 01:59:00'),
        ('download', '2024-05-31 01:59:00'),
        ('download', '2024-05-31 01:59:00'),
        ('download', '2024-05-31 02:00:00'),
        ('download', '2024-05-31 02:00:00'),
        ('download', '2024-05-31 02:00:00'),
        ('check_license', '2024-05-31 02:02:00'),
        ('download', '2024-05-31 02:02:00'),
        ('download', '2024-05-31 02:02:00'),
        ('download', '2024-05-31 02:02:00'),
        ('download', '2024-05-31 02:02:00'),
        ('download', '2024-05-31 02:02:00'),
        ('download', '2024-05-31 02:02:00'),
        ('check_license', '2024-05-31 02:05:00'),
        ('download', '2024-05-31 02:06:00'),
        ('download', '2024-05-31 02:06:00'),
        ('download', '2024-05-31 02:06:00'),
        ('download', '2024-05-31 02:06:00'),
        ('download', '2024-05-31 02:06:00'),
        ('download', '2024-05-31 02:06:00'),
        ('download', '2024-05-31 02:06:00'),
        ('check_license', '2024-05-31 16:39:00'),
        ('download', '2024-05-31 16:39:00'),
        ('download', '2024-05-31 16:39:00'),
        ('check_license', '2024-05-31 20:14:00'),
        ('download', '2024-05-31 20:14:00'),
        ('download', '2024-05-31 20:14:00'),
        ('check_license', '2024-05-31 20:18:00'),
        ('download', '2024-05-31 20:19:00'),
        ('download', '2024-05-31 20:19:00')
    ]

    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO license_log (api_name, access_time) VALUES (%s, %s)", test_data)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_log_table()
    log_down()  # 테스트를 위해 호출
    log_check()  # 테스트를 위해 호출
    # insert_test_data()
    generate_radar_chart()