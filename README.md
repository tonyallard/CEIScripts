# CEIScripts

## Problem-Analysis
AnalysisCommon.py - Common functions to support other scripts.
ComputeExpStats.py - Computes planner statistics from experimentation logs to CSV files.
copy-solved-problem-set.py - Copies problem files from one location to another, if at least one planner solved the problem according to experimental logs.
ExtractDeadEnds.py - Extracts the number of deadends encountered from Colin-style planner execution logs.
ExtractEHCHistogram.py - Extracts the EHC Guidance Histogram from experimentation log files.
ExtractFailedProblems.py - Extracts the reasons for failue from experimenation log files.
ExtractRunningTime.py - Extracts the average runtime for each problem domain from experimenation log files.
ExtractStatesEval.py - Extracts the average states evaluated in search and by the heuristic, exporting to CSV file.
ExtractSuccess.py - Extracts the coverage of a problem domain from experimentation logs.
FindInvalidPlan.py - Extracts the planners that found sequences of actions they thought to be plans, but were found to be invalid.
FindMemFails.py - Extracts the planner / problems combinations that failed due to running out of memory.
FindSegFaults.py - Extracts the planner / problems combinations that failed due to a segmentation fault during execution.
FindTimeouts.py - Extracts the planner / problems combinations that failed due to running out of permitted time to solve.
FindUnsolvables.py - Extracts the planner / problems combinations that determined the problem was unsolvable.
FixMissingPlans.py - Goes through experimentation logs, extracts the plan found by the planner in the log, updates the corresponding plan file and updates the validation information.
GenerateCoverageCSV.py - Computes coverage for each planner / problem combination and outputs to CSV.
LPG-TD-PlanValidator.py - Deprecated. Tries to fix LPG-TD plans and revalidate them, then adding them to the log file.
PlannerStats.py - A data structure that holds the experimental coverage statistics of a planner over a set of problem data.
ProblemDomainStats.py - A data structure that holds the experimental average runtime statistics of a planner over a set of problem data.
