<h1>CIE Pseudocode (9618, 2021 spec) to Python compiler</h1>

**By Opyu**

<h2>Usage:</h2>
Navigate to location of the folder (you should see a sub directory `/compiler`), 
and use `python3 compiler/main.py {file}` to compile. 
Compiled file should be outputted as out.py if it compiles successfully.

`test.txt` and `test2.txt` have been included as valid Pseudocode to test.

<h2>Currently supported:</h2>

Declaring Variables (Types are not supported yet):
```
DECLARE x = 1
x = 2  // X will be re-assigned to 2
```


Printing:
```
OUTPUT "Hello World"
OUTPUT var  // Printing vars 
```

Inputting:
```
INPUT var  // Var is assigned value of input
```
* Do note that inputting only works for floats right now

IF Selection (else not added yet):
```
IF <condition> THEN
    ...
ENDIF
```

Repeat until:
```
REPEAT
    ...
    ...
UNTIL <condition>
```