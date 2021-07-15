# CEIScripts

## exp-scripts
This folder containt scripts to support a distributed planner experimentaiton framework
1. cmd-planning-problem-server.py - A shell command interface for interacting manually with the server.
2. create_ramdisk.sh - A script to create a ramdisk at /mnt/ramdisk. This is used by some planners.
3. PlanningProblemConstants.py - Common functions and constants that suppor the experimental framework.
5. PlanningProblemJob.py - A data structure that describes a job (planner / problem pair).
7. planning-problem-restriction-script.py - Script to restrict or remove restrictions on the number of workers acutally completing jobs.
8. planning-problem-server.py - The server daemon. Run only one of these. Creates a queue of planner / problem pairs (jobs) and then gives to workers.
9. planning-problem-worker.py - The worker daemon. Run as many of these as required (typically number of available cores / 3).
10. runExperiment.sh - Simple bash script to kick off the server and a specified number of workers.
11. StateTest.py

## Problem-Analysis
This folder contains scripts to assist with the analysis (and repair) of logs from experimentation
1. AnalysisCommon.py - Common functions to support other scripts.
2. ComputeExpStats.py - Computes planner statistics from experimentation logs to CSV files.
3. copy-solved-problem-set.py - Copies problem files from one location to another, if at least one planner solved the problem according to experimental logs.
4. ExtractDeadEnds.py - Extracts the number of deadends encountered from Colin-style planner execution logs.
5. ExtractEHCHistogram.py - Extracts the EHC Guidance Histogram from experimentation log files.
6. ExtractFailedProblems.py - Extracts the reasons for failue from experimenation log files.
7. ExtractRunningTime.py - Extracts the average runtime for each problem domain from experimenation log files.
8. ExtractStatesEval.py - Extracts the average states evaluated in search and by the heuristic, exporting to CSV file.
9. ExtractSuccess.py - Extracts the coverage of a problem domain from experimentation logs.
10. FindInvalidPlan.py - Extracts the planners that found sequences of actions they thought to be plans, but were found to be invalid.
11. FindMemFails.py - Extracts the planner / problems combinations that failed due to running out of memory.
12. FindSegFaults.py - Extracts the planner / problems combinations that failed due to a segmentation fault during execution.
13. FindTimeouts.py - Extracts the planner / problems combinations that failed due to running out of permitted time to solve.
14. FindUnsolvables.py - Extracts the planner / problems combinations that determined the problem was unsolvable.
15. FixMissingPlans.py - Goes through experimentation logs, extracts the plan found by the planner in the log, updates the corresponding plan file and updates the validation information.
16. GenerateCoverageCSV.py - Computes coverage for each planner / problem combination and outputs to CSV.
17. LPG-TD-PlanValidator.py - Deprecated. Tries to fix LPG-TD plans and revalidate them, then adding them to the log file.
18. PlannerStats.py - A data structure that holds the experimental coverage statistics of a planner over a set of problem data.
19. ProblemDomainStats.py - A data structure that holds the experimental average runtime statistics of a planner over a set of problem data.
