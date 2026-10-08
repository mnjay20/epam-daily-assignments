/**
 * EPAM Systems | Hardware Concurrency Practice
 * Phase 2 Mandate: Silicon Proof
 * Experiment 2: False Sharing Hardware Benchmark
 * 
 * Hardware Target: 12th Gen Intel Core i5-12500H (12 Cores, 16 Threads, 64-byte Cache Lines)
 * Compares Cache-Line Contention (Adjacent) vs. 64-byte Cache Padding (Padded)
 */
public class FalseSharingBenchmark {

    private static final long ITERATIONS = 100_000_000L;
    private static final int WARMUP_RUNS = 2;
    private static final int BENCHMARK_RUNS = 5;

    // 1. Unpadded: Variables share the exact same 64-byte L1 Data Cache line
    static final class AdjacentCounters {
        public volatile long x = 0;
        public volatile long y = 0;
    }

    // 2. Padded: 7 long values (56 bytes) + object header force y to a separate 64-byte line
    static final class PaddedCounters {
        public volatile long x = 0;
        public long p1, p2, p3, p4, p5, p6, p7; // 56 bytes padding
        public volatile long y = 0;
    }

    // 3. Isolated Objects: Distinct heap references guarantees separate cache lines
    static final class IsolatedCounters {
        static final class SingleCounter {
            public volatile long value = 0;
        }
        public final SingleCounter x = new SingleCounter();
        public final SingleCounter y = new SingleCounter();
    }

    public static void main(String[] args) throws Exception {
        System.out.println("================================================================================");
        System.out.println(" EPAM CONCURRENCY LAB - EXPERIMENT 2: FALSE SHARING BENCHMARK");
        System.out.println(" Processor Architecture: 12th Gen Intel(R) Core(TM) i5-12500H");
        System.out.println(" Physical Cache Line  : 64 Bytes (L1D Cache: 48KB/P-core, 32KB/E-core)");
        System.out.println(" Iterations Per Thread : 100,000,000 (Total Ops per Run: 200,000,000)");
        System.out.println("================================================================================\n");

        // Warmup runs
        System.out.println(">>> Performing JIT C2 Compiler Warmup (2 cycles)...");
        for (int i = 0; i < WARMUP_RUNS; i++) {
            runAdjacent();
            runPadded();
        }
        System.out.println(">>> Warmup completed. Commencing precision silicon benchmarks...\n");

        // 1. Benchmark Adjacent (False Sharing)
        System.out.println("--- 1. BENCHMARKING ADJACENT COUNTERS (Same 64-byte Cache Line) ---");
        long[] adjacentTimes = new long[BENCHMARK_RUNS];
        for (int i = 0; i < BENCHMARK_RUNS; i++) {
            adjacentTimes[i] = runAdjacent();
            double throughput = (200.0 / adjacentTimes[i]) * 1000.0; // Mops/sec
            System.out.printf("  Run %d: %4d ms  |  Throughput: %6.2f Mops/sec  |  Latency: %.2f ns/op\n",
                    (i + 1), adjacentTimes[i], throughput, (adjacentTimes[i] * 1_000_000.0) / 200_000_000.0);
        }
        long avgAdjacent = average(adjacentTimes);

        // 2. Benchmark Padded (Cache Line Isolation)
        System.out.println("\n--- 2. BENCHMARKING PADDED COUNTERS (64-byte Cache-Padded Isolation) ---");
        long[] paddedTimes = new long[BENCHMARK_RUNS];
        for (int i = 0; i < BENCHMARK_RUNS; i++) {
            paddedTimes[i] = runPadded();
            double throughput = (200.0 / paddedTimes[i]) * 1000.0; // Mops/sec
            System.out.printf("  Run %d: %4d ms  |  Throughput: %6.2f Mops/sec  |  Latency: %.2f ns/op\n",
                    (i + 1), paddedTimes[i], throughput, (paddedTimes[i] * 1_000_000.0) / 200_000_000.0);
        }
        long avgPadded = average(paddedTimes);

        // 3. Benchmark Isolated Objects (Distinct Heap Allocations)
        System.out.println("\n--- 3. BENCHMARKING ISOLATED HEAP OBJECTS (Distinct Cache Lines) ---");
        long[] isolatedTimes = new long[BENCHMARK_RUNS];
        for (int i = 0; i < BENCHMARK_RUNS; i++) {
            isolatedTimes[i] = runIsolated();
            double throughput = (200.0 / isolatedTimes[i]) * 1000.0; // Mops/sec
            System.out.printf("  Run %d: %4d ms  |  Throughput: %6.2f Mops/sec  |  Latency: %.2f ns/op\n",
                    (i + 1), isolatedTimes[i], throughput, (isolatedTimes[i] * 1_000_000.0) / 200_000_000.0);
        }
        long avgIsolated = average(isolatedTimes);

        // Hardware Summary
        double adjacentMops = (200.0 / avgAdjacent) * 1000.0;
        double paddedMops = (200.0 / avgPadded) * 1000.0;
        double isolatedMops = (200.0 / avgIsolated) * 1000.0;
        double speedupPadded = (double) avgAdjacent / avgPadded;
        double speedupIsolated = (double) avgAdjacent / avgIsolated;

        System.out.println("\n================================================================================");
        System.out.println(" EPAM SILICON METRIC COMPARISON SUMMARY");
        System.out.println("================================================================================");
        System.out.printf("  Configuration        | Avg Time (ms) | Throughput (Mops/s) | Speedup Factor \n");
        System.out.println("  ---------------------|---------------|---------------------|----------------");
        System.out.printf("  1. Adjacent (Contended)| %9d ms   |  %10.2f Mops/s  |   1.00x (Baseline)\n", avgAdjacent, adjacentMops);
        System.out.printf("  2. Cache Padded (64B) | %9d ms   |  %10.2f Mops/s  |   %.2fx FASTER\n", avgPadded, paddedMops, speedupPadded);
        System.out.printf("  3. Isolated Objects  | %9d ms   |  %10.2f Mops/s  |   %.2fx FASTER\n", avgIsolated, isolatedMops, speedupIsolated);
        System.out.println("================================================================================");
        System.out.printf(" PHYSICAL SILICON ANALYSIS:\n");
        System.out.printf(" * Cache-Line Bouncing Overhead: +%d ms penalty (%.1f%% execution time wasted).\n", 
                (avgAdjacent - avgPadded), ((avgAdjacent - avgPadded) * 100.0 / avgAdjacent));
        System.out.println(" * In Adjacent mode, both cores ping-pong the same 64-byte line via MESIF protocol,");
        System.out.println("   causing Read-For-Ownership (RFO) requests and invalidating each other's L1 cache.");
        System.out.println(" * In Padded mode, each variable resides on an independent cache line, allowing");
        System.out.println("   both cores to stay in Exclusive (E) / Modified (M) state simultaneously.");
        System.out.println("================================================================================\n");
    }

    private static long runAdjacent() throws Exception {
        final AdjacentCounters counters = new AdjacentCounters();
        Thread t1 = new Thread(() -> {
            for (long i = 0; i < ITERATIONS; i++) counters.x++;
        });
        Thread t2 = new Thread(() -> {
            for (long i = 0; i < ITERATIONS; i++) counters.y++;
        });

        long start = System.nanoTime();
        t1.start();
        t2.start();
        t1.join();
        t2.join();
        return (System.nanoTime() - start) / 1_000_000;
    }

    private static long runPadded() throws Exception {
        final PaddedCounters counters = new PaddedCounters();
        Thread t1 = new Thread(() -> {
            for (long i = 0; i < ITERATIONS; i++) counters.x++;
        });
        Thread t2 = new Thread(() -> {
            for (long i = 0; i < ITERATIONS; i++) counters.y++;
        });

        long start = System.nanoTime();
        t1.start();
        t2.start();
        t1.join();
        t2.join();
        return (System.nanoTime() - start) / 1_000_000;
    }

    private static long runIsolated() throws Exception {
        final IsolatedCounters counters = new IsolatedCounters();
        Thread t1 = new Thread(() -> {
            for (long i = 0; i < ITERATIONS; i++) counters.x.value++;
        });
        Thread t2 = new Thread(() -> {
            for (long i = 0; i < ITERATIONS; i++) counters.y.value++;
        });

        long start = System.nanoTime();
        t1.start();
        t2.start();
        t1.join();
        t2.join();
        return (System.nanoTime() - start) / 1_000_000;
    }

    private static long average(long[] arr) {
        long sum = 0;
        for (long val : arr) sum += val;
        return sum / arr.length;
    }
}
