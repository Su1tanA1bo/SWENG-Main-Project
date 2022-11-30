##*************************************************************************
#   scans one file and returns list containing:
#   [numberOfFunctionsInFile, TotalComplexityValueInFile, AverageComplexityValue,
#   FileComplexityRank]
#   Complexity Values and their Ranks
#   1 - 5 	    A (low risk - simple block)
#   6 - 10 	    B (low risk - well structured and stable block)
#   11 - 20 	C (moderate risk - slightly complex block)
#   21 - 30 	D (more than moderate risk - more complex block)
#   31 - 40     E (high risk - complex block, alarming)
#   41+ 	    F (very high risk - error-prone, unstable block)
#
#   @author	 Sultan Albogachiev
#   @Creation Date: 24/11/2022
##*************************************************************************

from radon.complexity import cc_rank, cc_visit

def run_Complexity_Checker(file):
    fileInfo = cc_visit(file.contents)
    numberOfFunctionsInFile = 0
    TotalComplexityValueInFile = 0
    for obj in fileInfo:
        if obj.__class__.__name__ == "Class":
            TotalComplexityValueInFile += obj.real_complexity
            numberOfFunctionsInFile += len(obj.methods)
        if obj.__class__.__name__ == "Function":
            if str(obj.classname) == "None":
                TotalComplexityValueInFile += obj.complexity               
                numberOfFunctionsInFile += 1
    AverageComplexityValue = 0
    FileComplexityRank = "A"
    if(numberOfFunctionsInFile > 0):
        AverageComplexityValue = TotalComplexityValueInFile/numberOfFunctionsInFile
        FileComplexityRank = cc_rank(AverageComplexityValue)

    print(f"{file.name} has a complexity value of {AverageComplexityValue}")
    print(f"Complexity Rank = {FileComplexityRank}\n")  
    list = [numberOfFunctionsInFile, TotalComplexityValueInFile, AverageComplexityValue, FileComplexityRank]
    return list