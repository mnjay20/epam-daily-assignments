/**
 * EPAM Systems | Hardware Concurrency Practice
 * Phase 2 Mandate: Silicon Proof
 * Experiment 1: Proving Data Race & Instruction Reordering in Code
 * 
 * Hardware Target: 12th Gen Intel Core i5-12500H (12 Cores, 16 Threads, x86-64 Alder Lake)
 */
public class DataRaceProof {

    // Unsynchronized shared state for data race proof
    static int sharedCounter = 0;

    // Litmus variables for instruction reordering & visibility race
    static int litmusData = 0;
    static boolean litmusReady = false;

    // Volatile counterpart for comparison
    static volatile boolean volatileReady = false;

    public static void main(String[] args) throws Exception {
        System.out.println("================================================================================");
        System.out.println(" EPAM CONCURRENCY LAB - EXPERIMENT 1: SILICON PROOF OF DATA RACES");
        System.out.println(" Target Architecture: 12th Gen Intel(R) Core(TM) i5-12500H (16 HW Threads)");
        System.out.println(" OS: Windows 64-bit | JVM: OpenJDK 17 (Temurin-17.0.12+7)");
        System.out.println("================================================================================\n");

        runUnitTestIllusionTest();
        runMultiThreadedDataRaceStressTest();
        runInstructionReorderingLitmusTest();
    }

    /**
     * Proves why standard unit tests miss concurrency bugs.
     * When iteration count is low or threads don't overlap in execution slots,
     * the test passes 100% of the time, creating a dangerous false confidence.
     */
    private static void runUnitTestIllusionTest() throws Exception {
        System.out.println(">>> 1. UNIT TEST ILLUSION DEMONSTRATION");
        System.out.println("Running 100 consecutive 'naive unit tests' (low iterations: 500 per thread)...");
        
        int passes = 0;
        int fails = 0;
        int testRuns = 100;
        int smallIterations = 500;

        for (int run = 0; run < testRuns; run++) {
            sharedCounter = 0;
            Thread t1 = new Thread(() -> {
                for (int i = 0; i < smallIterations; i++) sharedCounter++;
            });
            Thread t2 = new Thread(() -> {
                for (int i = 0; i < smallIterations; i++) sharedCounter++;
            });

            t1.start();
            t2.start();
            t1.join();
            t2.join();

            int expected = 2 * smallIterations;
            if (sharedCounter == expected) {
                passes++;
            } else {
                fails++;
            }
        }

        System.out.printf("Results over %d unit test executions:\n", testRuns);
        System.out.printf("  [PASS] %d / %d runs (%.1f%% PASS RATE - FALSE GREEN BAR)\n", passes, testRuns, (passes * 100.0 / testRuns));
        System.out.printf("  [FAIL] %d / %d runs (%.1f%% FAILURE RATE)\n", fails, testRuns, (fails * 100.0 / testRuns));
        System.out.println("Conclusion: Unit tests with low sample sizes or sequential scheduling mask races completely.\n");
    }

    /**
     * Proves the data race under silicon stress.
     * Multi-threaded execution across 4 threads with 2,000,000 iterations each.
     * Demonstrates massive lost updates due to non-atomic read-modify-write (iload -> iadd -> istore).
     */
    private static void runMultiThreadedDataRaceStressTest() throws Exception {
        System.out.println(">>> 2. SILICON STRESS TEST: MASSIVE DATA RACE (4 Threads x 2,000,000 iterations)");
        sharedCounter = 0;
        int numThreads = 4;
        int iterationsPerThread = 2_000_000;
        int expectedTotal = numThreads * iterationsPerThread;

        Thread[] threads = new Thread[numThreads];
        long startTime = System.nanoTime();

        for (int i = 0; i < numThreads; i++) {
            threads[i] = new Thread(() -> {
                for (int j = 0; j < iterationsPerThread; j++) {
                    sharedCounter++;
                }
            }, "Worker-" + i);
            threads[i].start();
        }

        for (Thread t : threads) {
            t.join();
        }

        long elapsedMs = (System.nanoTime() - startTime) / 1_000_000;
        int actual = sharedCounter;
        int lostUpdates = expectedTotal - actual;
        double lossPercent = (lostUpdates * 100.0) / expectedTotal;

        System.out.println("--------------------------------------------------");
        System.out.printf(" Expected Total Updates : %,d\n", expectedTotal);
        System.out.printf(" Actual Final Value     : %,d\n", actual);
        System.out.printf(" Lost Updates (Missing) : %,d\n", lostUpdates);
        System.out.printf(" Data Loss Ratio        : %.2f%%\n", lossPercent);
        System.out.printf(" Execution Duration     : %d ms\n", elapsedMs);
        System.out.println("--------------------------------------------------");
        System.out.println("Root Cause: Bytecode 'getstatic -> iconst_1 -> iadd -> putstatic' interrupted");
        System.out.println("across CPU L1 caches without hardware bus lock or MESI invalidation lock.\n");
    }

    /**
     * Proves instruction reordering & visibility race (Litmus test).
     * Demonstrates that without volatile or memory barriers,
     * memory visibility delays and out-of-order pipeline execution cause stale reads.
     */
    private static void runInstructionReorderingLitmusTest() throws Exception {
        System.out.println(">>> 3. LITMUS TEST: INSTRUCTION REORDERING & VISIBILITY HAZARD");
        System.out.println("Running high-frequency message passing litmus test (50,000 runs)...");

        int staleReadViolations = 0;
        int trials = 50_000;

        for (int i = 0; i < trials; i++) {
            litmusData = 0;
            litmusReady = false;

            final int[] observed = new int[]{-1};

            Thread writer = new Thread(() -> {
                litmusData = 42;
                litmusReady = true;
            });

            Thread reader = new Thread(() -> {
                if (litmusReady) {
                    observed[0] = litmusData;
                }
            });

            writer.start();
            reader.start();
            writer.join();
            reader.join();

            // If reader saw ready==true, but observed data was 0, memory order was violated
            if (observed[0] == 0) {
                staleReadViolations++;
            }
        }

        System.out.println("--------------------------------------------------");
        System.out.printf(" Total Trials Tested      : %,d\n", trials);
        System.out.printf(" Stale Read Violations    : %d (observed ready=true with data=0)\n", staleReadViolations);
        System.out.println(" Hardware Explanation: On Intel x86 (TSO), Stores are ordered with Stores,");
        System.out.println(" but Store Buffer drain delay & L1 cache invalidation latency can cause");
        System.out.println(" reader cores to read stale L1 cache lines unless memory fences/volatile are enforced.");
        System.out.println("--------------------------------------------------\n");
    }
}
