# EPAM Systems | High-Performance Concurrency CoE
## Hardware Concurrency, Memory Models & Lock-Free Design
### Deconstructing Multi-Core Silicon Down to the Wire

> **EPAM Center of Excellence (CoE) Research Assignment**  
> **Core Focus:** Memory Subsystem Architecture, Hardware Fences, Cache Coherence (MESI/MOESI), False Sharing, Lock-Free Ring Buffers & Atomic Primitives.  
> **Primary Deliverable (PDF):** [`EPAM_Hardware_Concurrency_Research_Report.pdf`](EPAM_Hardware_Concurrency_Research_Report.pdf)  
> **Technical Markdown Source:** [`EPAM_Concurrency_Research_Report.md`](EPAM_Concurrency_Research_Report.md)  
> **Interactive HTML Source:** [`EPAM_Hardware_Concurrency_Report.html`](EPAM_Hardware_Concurrency_Report.html)  

---

## 📌 Executive Overview: Today's Challenge Addressed

| Challenge Vector | Core Architectural Problem | Silicon / Microarchitectural Root | Production Solution |
| :--- | :--- | :--- | :--- |
| **1. Instruction Reordering** | Independent loads & stores execute out of sequence, producing subtle data races that pass unit tests on x86 but crash on ARM64. | • Compiler: Register allocation & code motion under "as-if" rule.<br>• CPU: Out-of-Order execution engines, speculative loads, and asynchronous **Store Buffers**. | Explicit memory ordering using **Acquire-Release semantics** (`std::memory_order_acquire` / `release`) to establish happens-before edges. |
| **2. Memory Fences Down to the Wire** | How fences enforce cross-core visibility at the physical gate level. | • **Store-Release**: Drains the local **Store Buffer** to L1 cache before the flag is published.<br>• **Load-Acquire**: Drains the **Invalidate Queue** and purges speculatively pre-fetched reads.<br>• **Seq-Cst**: Enforces a global total order via full store buffer stalls (`MFENCE` / `DMB SY`). | One-way fences (`LDAR` / `STLR` on ARM64; compiler barriers on x86-TSO) to eliminate pipeline serialization penalties. |
| **3. Cache Coherence & False Sharing** | Independent variables modified by different threads degrade throughput by 100x even with zero logical data sharing. | • Hardware transfers and invalidates data at **64-byte Cache Line granularity**.<br>• MESI/MOESI protocol transitions lines between Modified (`M`) and Invalid (`I`), triggering continuous **inter-core cache ping-pong** and Read-For-Ownership (`RFO`) bus broadcasts. | Cache-line padding (`alignas(64)` or `std::hardware_destructive_interference_size`) to guarantee independent cache lines. |
| **4. Lock-Free Scale vs. Kernel Contention** | Traditional mutexes choke under high contention due to OS context switches and thread rescheduling. | • `std::mutex` blocks via kernel syscalls (`futex`), causing thread descheduling, TLB flushes, and cache pollution (~1,500–5,000 ns latency). | **Atomic CAS (`Compare-And-Swap`)** retries entirely in user space (<20 ns); **LMAX Disruptor** preallocates ring buffers with power-of-2 bitmask indexing and padded sequence counters. |

---

## 🏛️ System Architecture: The 3 Concurrency Layers

```
                                  SYSTEM ARCHITECTURE
 ┌──────────────────────────────────────────────────────────────────────────────────┐
 │ LAYER 1: CORRECTNESS (Language Memory Models)                                    │
 │ • C++11 Memory Model: Relaxed, Acquire/Release, Sequential Consistency           │
 │ • Solves: "Can another thread legally observe this memory mutation in order?"   │
 └────────────────────────────────────────┬─────────────────────────────────────────┘
                                          │
                                          ▼
 ┌──────────────────────────────────────────────────────────────────────────────────┐
 │ LAYER 2: COHERENCE (Hardware Interconnect Protocols)                             │
 │ • Protocol: MESI (Modified, Exclusive, Shared, Invalid) / MOESI (Owner)          │
 │ • Unit: 64-Byte Cache Lines                                                      │
 │ • Solves: "How do private L1/L2 caches agree on a single value per address?"    │
 └────────────────────────────────────────┬─────────────────────────────────────────┘
                                          │
                                          ▼
 ┌──────────────────────────────────────────────────────────────────────────────────┐
 │ LAYER 3: PERFORMANCE & SCALE (Mechanical Sympathy & Lock-Free Design)            │
 │ • Techniques: 64-byte Cache Padding, Atomic CAS, Preallocated Ring Buffers      │
 │ • Solves: "How do we eliminate cache-line bouncing and kernel context switches?" │
 └──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🗺️ Visual Architecture Gallery (All 20 Technical Diagrams)

All architectural diagrams generated for this assignment are integrated into the primary research report and categorized below:

### Layer 1: Memory Models, Reordering & Fences
| Diagram Asset | Description & Technical Focus |
| :--- | :--- |
| ![inst reordering](inst%20reordering.png) | **Instruction Reordering Pipeline:** Producer store buffering and consumer speculative execution leading to unaligned observation. |
| ![inst reordering 2](inst%20reordering%202.png) | **Reordering Sequence Diagram:** Tracing store buffer delays between Core 0 and Core 1. |
| ![acquire and release](acquire%20and%20release.png) | **Acquire-Release Pipeline:** Visualizing the synchronizes-with hand-off that guarantees data visibility. |
| ![require and release](require%20and%20release.png) | **Happens-Before Sequence:** Producer release store synchronizing with Consumer acquire load. |
| ![AcquireRelease vs Sequential Consistency](AcquireRelease%20vs%20Sequential%20Consistency.png) | **Memory Ordering Hierarchy:** Relaxed vs Acquire-Release vs Sequential Consistency trade-offs. |

### Layer 2: Cache Coherence (MESI / MOESI) & False Sharing
| Diagram Asset | Description & Technical Focus |
| :--- | :--- |
| ![mesi meaning](mesi%20meaning.png) | **MESI Protocol States:** High-level relationships between Modified, Exclusive, Shared, and Invalid states. |
| ![mesi state diagrams](mesi%20state%20diagrams.png) | **Formal MESI State Machine:** Complete state transition matrix triggered by local reads/writes and bus snoops. |
| ![mesi cache line ownership](mesi%20cache%20line%20owner%20ship%20example.png) | **Cache Line Ownership Transfer:** Sequence diagram of Read-For-Ownership (RFO) and invalidations across the bus. |
| ![false sharing 2](false%20sharing%202.png) | **False Sharing Anatomy:** Independent variables co-located on a single 64-byte line triggering invalidations. |
| ![false sharing](false%20sharing.png) | **Cache-Line Ping-Pong:** Sequence diagram of throughput-destroying cross-core line bouncing. |
| ![cache padding solution](cache%20padding%20soltion%20of%20false%20sharing.png) | **Cache-Line Padding Remediation:** Splitting variables into independent cache lines via `alignas(64)`. |

### Layer 3: Lock-Free Scale, CAS, Ring Buffers & LMAX Disruptor
| Diagram Asset | Description & Technical Focus |
| :--- | :--- |
| ![lock based and lock free](lock%20based%20and%20lock%20free.png) | **Mutex vs Lock-Free Decision Tree:** OS scheduling context switch vs user-space atomic retry loop. |
| ![cas operation](cas%20operation.png) | **Compare-And-Swap (CAS) Logic:** Step-by-step flowchart of optimistic atomic mutation and retry loop. |
| ![two threads racing on cas](two%20threads%20racing%20on%20cas.png) | **CAS Contention Race:** Two threads racing on an atomic counter; one succeeds, the other retries. |
| ![aba problem](aba%20problem.png) | **The ABA Hazard:** Undetected pointer state mutation ($A \to B \to A$) tricking a naive CAS. |
| ![ring buffer flow](ring%20buffer%20flow.png) | **SPSC Ring Buffer Coordination:** Sequence counter synchronization between producer and consumer. |
| ![LMAX disruptor](LMX%20disruptor.png) | **LMAX Disruptor Architecture:** Preallocated ring buffer, bitmask slot indexing, and padded sequencers. |

### Full-Stack System Overviews
| Diagram Asset | Description & Technical Focus |
| :--- | :--- |
| ![divided in layers](divided%20in%20layers.png) | **3-Layer Concurrency Model:** Correctness $\to$ Coherence $\to$ Performance. |
| ![complete flow](complete%20flow.png) | **Complete Architectural Flow:** Holistic path from multithreaded code down to physical silicon. |
| ![mermaid-diagram](mermaid-diagram.png) | **Full Hardware Stack:** Application $\to$ Language Memory Model $\to$ CPU Pipelines $\to$ Caches $\to$ DRAM. |

---

## ⚡ The Quest: Silicon Wire-Level Trace of a Memory Race

The primary assignment quest requires looking "down to the wire" to deconstruct how an asymmetric race occurs across CPU pipelines, store buffers, and invalidate queues:

```
PRODUCER CORE 0                                                                CONSUMER CORE 1
┌───────────────────────────┐                                                  ┌───────────────────────────┐
│ 1. data = 42              │                                                  │                           │
│    Pushed into Store Buf  │                                                  │                           │
│                           │                                                  │                           │
│ 2. ready = true           │                                                  │                           │
│    Store Buf issues RFO   │────────── Coherence Bus / Invalidate ───────────►│ 3. while (!ready) {}      │
│    for 'ready' first!     │                                                  │    L1 miss on ready;      │
│                           │                                                  │    fetches ready = true   │
│                           │                                                  │    Loop terminates!       │
│                           │                                                  │                           │
│                           │                                                  │ 4. val = data             │
│                           │                                                  │    Reads stale data = 0   │
│                           │                                                  │    directly from L1!      │
│                           │                                                  │                           │
│ 5. Store Buf drains 42    │                                                  │ 5. assert(val == 42)      │
│    TOO LATE!              │                                                  │    *** CRASH / MISMATCH ***│
└───────────────────────────┘                                                  └───────────────────────────┘
```

### Microarchitectural Repair via Acquire-Release
- **Producer Store-Release (`STLR` / `DMB`):** Physically stalls publication of `ready` until all prior entries in the local Store Buffer (`data = 42`) have committed to the L1 cache.
- **Consumer Load-Acquire (`LDAR` / Invalidate Queue Flush):** Immediately forces the Invalidate Queue to process all pending invalidations, marking Core 1's copy of `data` as Invalid (`I`). Core 1 is forced to issue a `BusRd`, retrieving the updated `42` from Core 0.

---

## 📊 Core Engineering Comparison Tables

### 1. Hardware Memory Model Matrix
| Architecture | Store-Store Reordering? | Load-Load Reordering? | Store-Load Reordering? | Native Hardware Phenotype |
| :--- | :---: | :---: | :---: | :--- |
| **x86-64 (Intel / AMD)** | ❌ No | ❌ No | ✅ **Yes** | **Total Store Order (TSO)**. Strong memory model. Plain stores are releases; plain loads are acquires. |
| **ARM64 (v8 / Neoverse)** | ✅ **Yes** | ✅ **Yes** | ✅ **Yes** | **Weak Memory Ordering**. Reordering is aggressive. Explicit `LDAR`/`STLR` or `DMB` required. |
| **IBM POWER** | ✅ **Yes** | ✅ **Yes** | ✅ **Yes** | **Ultra-Weak**. Requires `lwsync` or heavy `sync` barriers. |
| **RISC-V (RVWMO)** | ✅ **Yes** | ✅ **Yes** | ✅ **Yes** | **Weak Memory Ordering**. Emits `fence` instructions. |

---

### 2. Synchronization Mechanisms: Performance & Cost
| Mechanism | Average Latency | Context Switch? | Cache Invalidation Scope | Ideal Workload |
| :--- | :--- | :---: | :--- | :--- |
| **`std::mutex`** | 1,500 – 5,000 ns | ✅ Yes (on contention) | Widespread (TCB swap, scheduler data) | Long critical sections (> 5 µs), I/O bound tasks. |
| **Spinlock** | 20 – 100 ns | ❌ No | High cache-line bouncing on lock word | Ultra-short critical sections; real-time OS kernels. |
| **Atomic CAS Loop** | 5 – 25 ns | ❌ No | Confined to targeted cache line | Fine-grained lock-free data structures (stacks, queues). |
| **Lock-Free SPSC Ring Buffer** | **< 3 ns** | ❌ No | **Zero** (padded sequencers eliminate ping-pong) | Inter-thread messaging, low-latency order routing, streaming. |

---

## 🛠️ Code Implementations & Reference Patterns

The full implementations are documented with comprehensive technical rationale in [`EPAM_Concurrency_Research_Report.md`](EPAM_Concurrency_Research_Report.md):

1. **Litmus Message Passing Test:** Flawed non-atomic pattern vs. zero-cost Acquire-Release synchronization.
2. **False Sharing Benchmark:** Concrete C++ test harness measuring the 50x–100x performance collapse and `alignas(64)` solution.
3. **High-Performance SPSC Lock-Free Ring Buffer:** LMAX Disruptor-style ring buffer featuring preallocation, bitwise index masking (`pos & (N - 1)`), and cache-line padded sequencers.
4. **Double-Word CAS (ABA Prevention):** 128-bit tagged pointer atomic exchange using `CMPXCHG16B`.

---

## 🔬 Hardware Observability & Profiling Toolkit

```bash
# 1. Profile Cache-to-Cache False Sharing using Linux perf
perf c2c record -F 60000 -- ./high_throughput_service
perf c2c report --stdio

# 2. Inspect Hardware Performance Counters for Memory Stall Cycles
perf stat -e mem_load_retired.l1_miss,mem_load_retired.l3_miss,ocr.demand_data_rd.remote_hitm ./service

# 3. Detect Data Races with LLVM ThreadSanitizer
clang++ -O2 -g -fsanitize=thread -fno-omit-frame-pointer service.cpp -o service
./service
```

---

## 📁 Repository & Assignment Structure

- 📕 [`EPAM_Hardware_Concurrency_Research_Report.pdf`](EPAM_Hardware_Concurrency_Research_Report.pdf) — **Compiled Publication PDF (Complete with all 20 embedded diagrams, tables & code).**
- 📄 [`EPAM_Concurrency_Research_Report.md`](EPAM_Concurrency_Research_Report.md) — **Primary comprehensive technical whitepaper & submission report.**
- 🌐 [`EPAM_Hardware_Concurrency_Report.html`](EPAM_Hardware_Concurrency_Report.html) — **Interactive, beautifully formatted executive HTML report.**
- 📄 [`EPAM_Concurrency_on_Modern_Multi_Core_CPUs.pdf`](EPAM_Concurrency_on_Modern_Multi_Core_CPUs.pdf) — Source EPAM CoE research document.
- 📄 [`Deep Research_ Concurrency on Modern Multi-Core CPUs.pdf`](Deep%20Research_%20Concurrency%20on%20Modern%20Multi-Core%20CPUs.pdf) — Deep research foundational paper.
- 🖼️ `*.png` (20 diagram files) — Architectural flowcharts, sequence diagrams, and microarchitectural models.

---
**EPAM Systems Architecture & Concurrency CoE © 2026**
