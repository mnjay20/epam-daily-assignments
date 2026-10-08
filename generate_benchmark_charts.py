import matplotlib.pyplot as plt
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont

# Set styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Segoe UI', 'DejaVu Sans', 'Arial'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

output_dir = r"c:\Users\dell\Downloads\assignment -1"

# ==========================================
# 1. FALSE SHARING BENCHMARK CHART
# ==========================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

configs = ['Adjacent Counters\n(Same 64B Line)', 'Cache Padded\n(64B Isolation)', 'Isolated Objects\n(Separate Heap)']
times_ms = [3248, 732, 3346]
throughput_mops = [61.58, 273.22, 59.77]
colors = ['#d9534f', '#2b7bba', '#f0ad4e']

# Subplot 1: Execution Time
bars1 = ax1.bar(configs, times_ms, color=colors, width=0.55, edgecolor='#333333', linewidth=1)
ax1.set_title("Execution Time (Lower is Better)\n200,000,000 Total Ops on Intel i5-12500H", fontsize=13, fontweight='bold', pad=15)
ax1.set_ylabel("Execution Time (milliseconds)", fontsize=11, fontweight='semibold')
ax1.set_ylim(0, 4000)

for bar in bars1:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 70, f"{int(yval)} ms", ha='center', va='bottom', fontsize=11, fontweight='bold')

# Annotate speedup
ax1.annotate("4.44x FASTER\n(-77.5% Time)", 
             xy=(1, 732), xytext=(1, 2000),
             arrowprops=dict(facecolor='#2b7bba', shrink=0.08, width=2, headwidth=8),
             ha='center', fontsize=11, fontweight='bold', color='#1d527d',
             bbox=dict(boxstyle="round,pad=0.4", fc="#e6f2ff", ec="#2b7bba", lw=1.5))

# Subplot 2: Throughput
bars2 = ax2.bar(configs, throughput_mops, color=colors, width=0.55, edgecolor='#333333', linewidth=1)
ax2.set_title("Throughput (Higher is Better)\nHardware Cache Line Scaling", fontsize=13, fontweight='bold', pad=15)
ax2.set_ylabel("Throughput (Million ops / sec)", fontsize=11, fontweight='semibold')
ax2.set_ylim(0, 330)

for bar in bars2:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 6, f"{yval:.1f} Mops/s", ha='center', va='bottom', fontsize=11, fontweight='bold')

ax2.annotate("+211.6 Mops/s Gain\nNo False Sharing", 
             xy=(1, 273.22), xytext=(1, 150),
             arrowprops=dict(facecolor='#2b7bba', shrink=0.08, width=2, headwidth=8),
             ha='center', fontsize=11, fontweight='bold', color='#1d527d',
             bbox=dict(boxstyle="round,pad=0.4", fc="#e6f2ff", ec="#2b7bba", lw=1.5))

fig.suptitle("EPAM Hardware Benchmark: Silicon False Sharing Impact\nIntel® Core™ i5-12500H (12 Cores, 16 Threads, 64-Byte Cache Lines)", fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
chart1_path = os.path.join(output_dir, "benchmark_false_sharing_silicon.png")
plt.savefig(chart1_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved: {chart1_path}")

# ==========================================
# 2. LOCK-FREE SCALABILITY & CONTENTION CHART
# ==========================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=300)

threads = [1, 2, 4, 8, 16]
sync_time = [37, 122, 111, 176, 350]
cas_time = [18, 95, 304, 1553, 3255]
cas_retries = [0, 581702, 3866691, 21415052, 51357835]

ax1.plot(threads, sync_time, marker='o', linewidth=2.5, markersize=8, color='#d9534f', label='Synchronized Lock (OS Monitor)')
ax1.plot(threads, cas_time, marker='s', linewidth=2.5, markersize=8, color='#2b7bba', label='Lock-Free CAS Loop (AtomicLong)')
ax1.set_title("Execution Time vs Thread Contention\n(2,000,000 operations per thread)", fontsize=12, fontweight='bold')
ax1.set_xlabel("Hardware Threads", fontsize=11, fontweight='semibold')
ax1.set_ylabel("Execution Time (milliseconds)", fontsize=11, fontweight='semibold')
ax1.set_xticks(threads)
ax1.legend(loc='upper left', frameon=True)
ax1.grid(True, linestyle='--', alpha=0.6)

# Annotate crossover
ax1.annotate("CAS Outperforms at Low Threads\n(1.28x - 2.06x faster)", 
             xy=(1, 18), xytext=(2.5, 600),
             arrowprops=dict(facecolor='#2b7bba', shrink=0.08, width=1.5, headwidth=6),
             fontsize=9.5, fontweight='semibold', color='#1d527d',
             bbox=dict(boxstyle="round,pad=0.3", fc="#e6f2ff", ec="#2b7bba"))

ax1.annotate("CAS Contention Storm\n(Cache-line bouncing)", 
             xy=(16, 3255), xytext=(9, 2800),
             arrowprops=dict(facecolor='#d9534f', shrink=0.08, width=1.5, headwidth=6),
             fontsize=9.5, fontweight='semibold', color='#a94442',
             bbox=dict(boxstyle="round,pad=0.3", fc="#fdf7f7", ec="#d9534f"))

# Subplot 2: CAS Retries under Contention
retries_millions = [r / 1_000_000.0 for r in cas_retries]
bars = ax2.bar([str(t) for t in threads], retries_millions, color='#6f42c1', width=0.55, edgecolor='#333333', linewidth=1)
ax2.set_title("Silicon Contention: CAS Retry Storm\nFailed compareAndSet() Iterations", fontsize=12, fontweight='bold')
ax2.set_xlabel("Hardware Threads", fontsize=11, fontweight='semibold')
ax2.set_ylabel("Failed CAS Retries (Millions)", fontsize=11, fontweight='semibold')
ax2.grid(True, linestyle='--', alpha=0.6)

for bar in bars:
    yval = bar.get_height()
    if yval > 0.05:
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 1.0, f"{yval:.1f}M", ha='center', va='bottom', fontsize=10, fontweight='bold')

fig.suptitle("EPAM Lock-Free Benchmark: Scalability & Contention Analysis\nEmpirical Silicon Data on 12th Gen Intel Core i5-12500H", fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
chart2_path = os.path.join(output_dir, "benchmark_lock_free_scalability.png")
plt.savefig(chart2_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved: {chart2_path}")

# ==========================================
# 3. DATA RACE PROOF & UNIT TEST ILLUSION
# ==========================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

# Subplot 1: Unit Test Illusion
test_categories = ['Passing Runs\n(False Green Bar)', 'Failing Runs\n(Detected)']
test_counts = [100, 0]
ax1.bar(test_categories, test_counts, color=['#28a745', '#dc3545'], width=0.45, edgecolor='#333333', linewidth=1)
ax1.set_title("Naive Unit Test Results (100 Executions)\n500 Iterations/Thread (Zero Races Caught!)", fontsize=12, fontweight='bold')
ax1.set_ylabel("Number of Test Runs", fontsize=11, fontweight='semibold')
ax1.set_ylim(0, 120)
ax1.text(0, 103, "100 / 100 PASS (100% FALSE CONFIDENCE)", ha='center', fontsize=10.5, fontweight='bold', color='#1e7e34')
ax1.text(1, 5, "0 / 100 FAIL (0% Caught)", ha='center', fontsize=10.5, fontweight='bold', color='#bd2130')

# Subplot 2: Multi-threaded Silicon Stress
race_categories = ['Actual Final Count\n(Silicon Result)', 'Lost Updates\n(Silently Dropped)']
race_values = [4589247 / 1_000_000.0, 3410753 / 1_000_000.0]
bars_race = ax2.bar(race_categories, race_values, color=['#17a2b8', '#dc3545'], width=0.45, edgecolor='#333333', linewidth=1)
ax2.set_title("Silicon Stress Test (4 Threads x 2M Iterations)\nExpected: 8,000,000 Total Updates", fontsize=12, fontweight='bold')
ax2.set_ylabel("Counter Value (Millions)", fontsize=11, fontweight='semibold')
ax2.set_ylim(0, 6)

ax2.text(0, race_values[0] + 0.15, f"{race_values[0]:.2f}M (57.4%)", ha='center', fontsize=10.5, fontweight='bold', color='#117a8b')
ax2.text(1, race_values[1] + 0.15, f"{race_values[1]:.2f}M (42.6% LOST!)", ha='center', fontsize=10.5, fontweight='bold', color='#bd2130')

fig.suptitle("EPAM Mandate 1: Proving Data Race in Code & Unit Test Failure\nDirect Verification on 12th Gen Intel Core i5-12500H", fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
chart3_path = os.path.join(output_dir, "benchmark_data_race_proof.png")
plt.savefig(chart3_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved: {chart3_path}")

# ==========================================
# 4. SPSC RING BUFFER THROUGHPUT CHART
# ==========================================
fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
architectures = ['Synchronized Queue\n(Blocking Lock)', 'Lock-Free CAS Loop\n(High Contention)', 'SPSC Ring Buffer\n(LMAX Disruptor Pattern)']
throughput_vals = [2.85, 4.91, 15.90] # Million msgs/sec
colors_arch = ['#6c757d', '#fd7e14', '#28a745']

bars_arch = ax.bar(architectures, throughput_vals, color=colors_arch, width=0.5, edgecolor='#333333', linewidth=1)
ax.set_title("Inter-Thread Messaging Throughput Comparison\n10,000,000 Streamed Events on Intel Core i5-12500H", fontsize=12, fontweight='bold', pad=15)
ax.set_ylabel("Throughput (Million messages / sec)", fontsize=11, fontweight='semibold')
ax.set_ylim(0, 20)

for bar in bars_arch:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.4, f"{yval:.2f} M/sec", ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.annotate("5.57x Higher Throughput\nLatency: 62.9 ns / msg", 
            xy=(2, 15.90), xytext=(1.4, 11),
            arrowprops=dict(facecolor='#28a745', shrink=0.08, width=2, headwidth=8),
            ha='center', fontsize=10.5, fontweight='bold', color='#155724',
            bbox=dict(boxstyle="round,pad=0.4", fc="#d4edda", ec="#28a745", lw=1.5))

plt.tight_layout()
chart4_path = os.path.join(output_dir, "benchmark_ring_buffer_disruptor.png")
plt.savefig(chart4_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved: {chart4_path}")
