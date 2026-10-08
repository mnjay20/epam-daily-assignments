# EPAM Systems | Hardware Concurrency Practice
## Phase 2: "From Theory to Silicon Proof" — Complete Walkthrough & Submission Guide

This directory contains the production-grade code, benchmarks, terminal execution screenshots, and the updated Word document satisfying the EPAM mentor mandate.

---

## 1. Quick File Reference

- **Updated Word Document**: [EPAM_Silicon_Proof_Report.docx](file:///c:/Users/dell/Downloads/assignment%20-1/EPAM_Silicon_Proof_Report.docx) *(also mirrored to `Task2 08oct26.docx`)*
- **One-Click Benchmark Runner**: `run_all_benchmarks.bat`
- **Experiment 1 Source**: [DataRaceProof.java](file:///c:/Users/dell/Downloads/assignment%20-1/DataRaceProof.java)
- **Experiment 2 Source**: [FalseSharingBenchmark.java](file:///c:/Users/dell/Downloads/assignment%20-1/FalseSharingBenchmark.java)
- **Experiment 3 Source**: [LockFreeBenchmark.java](file:///c:/Users/dell/Downloads/assignment%20-1/LockFreeBenchmark.java)

### Generated Charts & Silicon Screenshots
1. **Data Race Proof**:
   - Chart: `benchmark_data_race_proof.png`
   - Terminal Execution: `screenshot_terminal_datarace.png`
2. **False Sharing Benchmark**:
   - Chart: `benchmark_false_sharing_silicon.png`
   - Terminal Execution: `screenshot_terminal_falsesharing.png`
3. **Lock-Free Scalability & Ring Buffer**:
   - Chart: `benchmark_lock_free_scalability.png`
   - Chart: `benchmark_ring_buffer_disruptor.png`
   - Terminal Execution: `screenshot_terminal_lockfree.png`

---

## 2. Testbed Hardware Specs (Empirical Environment)
- **CPU**: 12th Gen Intel(R) Core(TM) i5-12500H (12 Cores: 4 P-cores + 8 E-cores, 16 Threads)
- **Caches**: L1D (48KB P-core / 32KB E-core), L2 (9.2 MB), L3 (18.0 MB Smart Cache)
- **Cache Line Granularity**: 64 Bytes physical
- **Coherence Protocol**: Intel MESIF (Modified, Exclusive, Shared, Invalid, Forward)
- **Memory Model**: x86-TSO (Total Store Order)
- **Runtime**: OpenJDK 17 (Temurin-17.0.12+7, 64-Bit Server VM)

---

## 3. Team KT & Live Walkthrough Cheat Sheet (For Mentor Defense)

### Task 1: Prove the Race in Code (`DataRaceProof.java`)
- **Key Question Mentors Will Ask**: *"Why did our unit tests pass if the code had a bug?"*
- **Engineering Answer**: 
  - Standard unit tests use small iteration loops (e.g., 500 iterations). Each thread runs for ~20-50 microseconds.
  - The OS scheduler's timeslice quantum is 10 to 15 milliseconds.
  - Thread 1 completes entirely before Thread 2 is even scheduled, creating a sequential execution illusion (100% false green bar).
- **The Silicon Proof**:
  - 4 threads x 2,000,000 increments on `counter++`.
  - Expected: 8,000,000 updates.
  - Actual: **4,589,247** updates (**42.63% data loss**, 3,410,753 lost updates!).
  - Bytecode: `getstatic -> iconst_1 -> iadd -> putstatic` without `LOCK` prefix allows cores to overwrite each other's L1 cache lines.

### Task 2: False Sharing Hardware Benchmark (`FalseSharingBenchmark.java`)
- **Key Question Mentors Will Ask**: *"Where are your CPU metrics proving false sharing hurts throughput?"*
- **Engineering Answer**:
  - Memory moves in **64-byte cache lines**, not individual variables.
  - Two adjacent 8-byte `volatile long` variables (`x` and `y`) fit inside the same 64-byte line.
  - When Core 0 writes `x`, MESIF invalidates Core 1's entire cache line via Read-For-Ownership (RFO). Core 1 stalls, invalidates Core 0, and reloads across the interconnect.
- **The Silicon Metrics**:
  - Adjacent Counters: **3,248 ms** avg | **61.58 Mops/sec** | 16.24 ns/op
  - Padded Counters (64B): **732 ms** avg | **273.22 Mops/sec** | 3.66 ns/op
  - **Speedup**: **4.44x FASTER** (**77.5% CPU stall time eliminated!**).

### Task 3: Lock-Free Construct (`LockFreeBenchmark.java`)
- **Key Question Mentors Will Ask**: *"Why build a lock-free CAS loop or ring buffer instead of synchronized?"*
- **Engineering Answer**:
  - `synchronized` forces kernel context switches (~1.5 to 3.0 μs / 1,500-3,000 ns).
  - Lock-free uses hardware user-space `LOCK CMPXCHG`.
  - At 1 thread: CAS is **2.06x faster** than synchronized (18 ms vs 37 ms).
- **The Advanced Craftsmanship Insight (CAS Contention Storm)**:
  - At 16 threads, single-variable CAS collapses due to bus lock contention: **51,357,835 failed retries**, taking 3,255 ms vs 350 ms for synchronized.
  - **The Fix**: High-performance systems use **SPSC Disruptor Ring Buffers** with 64-byte padded head/tail pointers and power-of-two bitwise masking (`index & mask`).
  - Ring Buffer Result: **10,000,000 messages streamed in 629 ms** (**15.90 Million msgs/sec** at **62.90 ns latency**, 100% data integrity).
