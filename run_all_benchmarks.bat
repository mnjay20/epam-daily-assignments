@echo off
echo ================================================================================
echo  EPAM SYSTEMS CONCURRENCY LAB - SILICON PROOF RUNNER
echo  Processor: 12th Gen Intel(R) Core(TM) i5-12500H
echo ================================================================================
echo.

echo [1/3] Compiling and Running Experiment 1: Data Race Proof...
javac DataRaceProof.java
java DataRaceProof
echo.

echo [2/3] Compiling and Running Experiment 2: False Sharing Hardware Benchmark...
javac FalseSharingBenchmark.java
java FalseSharingBenchmark
echo.

echo [3/3] Compiling and Running Experiment 3: Lock-Free CAS & SPSC Ring Buffer...
javac LockFreeBenchmark.java
java LockFreeBenchmark
echo.

echo ================================================================================
echo  ALL SILICON BENCHMARKS COMPLETED SUCCESSFULLY!
echo ================================================================================
pause
