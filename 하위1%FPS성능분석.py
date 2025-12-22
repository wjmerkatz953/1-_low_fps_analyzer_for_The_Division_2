import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 파일 경로 설정
file_3080 = "benchmark_20251214_17h09m.csv"
file_9070 = "benchmark_20251220_22h34m.csv"

# 데이터 처리 함수
def process_benchmark(file_path):
    df = pd.read_csv(file_path, skiprows=2)
    df.columns = [c.strip() for c in df.columns]
    df['frametime_ms'] = df['Time 0.1mS'] * 0.1
    df['fps'] = 1000 / df['frametime_ms']
    return df

# 데이터 로드
df_3080 = process_benchmark(file_3080)
df_9070 = process_benchmark(file_9070)

# 주요 지표 계산 함수
def get_metrics(df):
    return {
        "Avg FPS": df['fps'].mean(),
        "1% Low": df['fps'].quantile(0.01),
        "0.1% Low": df['fps'].quantile(0.001),
        "GPU Load": df['GPU%'].mean(),
        "Frametime Std": df['frametime_ms'].std()
    }

m_3080 = get_metrics(df_3080)
m_9070 = get_metrics(df_9070)

print(f"=== RTX 3080 vs 9070 XT ===")
print(f"1% Low: {m_3080['1% Low']:.1f} vs {m_9070['1% Low']:.1f}")
print(f"Frametime Std: {m_3080['Frametime Std']:.2f}ms vs {m_9070['Frametime Std']:.2f}ms")

# 시각화 (막대 그래프)
labels = ['Avg FPS', '1% Low', '0.1% Low']
values_3080 = [m_3080['Avg FPS'], m_3080['1% Low'], m_3080['0.1% Low']]
values_9070 = [m_9070['Avg FPS'], m_9070['1% Low'], m_9070['0.1% Low']]

x = np.arange(len(labels))
width = 0.35

plt.figure(figsize=(10, 6))
plt.bar(x - width/2, values_3080, width, label='RTX 3080', alpha=0.8)
plt.bar(x + width/2, values_9070, width, label='9070 XT', alpha=0.8)

plt.ylabel('FPS')
plt.title('Performance Comparison')
plt.xticks(x, labels)
plt.legend()
plt.grid(axis='y', alpha=0.3)
plt.show()