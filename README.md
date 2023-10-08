<h1>CIE Pseudocode (9618, 2021 spec) to Python compiler</h1>

**By Opyu**

<h2>Usage:</h2>
Navigate to location of the folder (you should see a sub directory ` /compiler`), 
and use `python3 compiler/main.py {file}` to compile. 
Compiled file should be outputted as out.py if it compiles successfully.

`test.txt` and `test2.txt` have been included as valid Pseudocode to test.

<h2>Currently supported:</h2>

**Declaring Variables**:
```
DECLARE x : INTEGER
x = 2

DECLARE y : BOOLEAN
y = TRUE
```
* INTEGERS can become floats because of how Python works...
```
DECLARE x : INTEGER
x = 1 / 2  // x == 0.5
```
\
**Printing**:
```
OUTPUT "Hello World"
OUTPUT var  // Printing vars 
```
\
**Inputting**:
```
INPUT var  // Var is assigned value of input
```
* Inputting to an int will automatically typecast the input.

```
DECLARE x : INTEGER
INPUT x  // Will be int(input(""))
```
* You cannot input with a BOOLEAN.
```
DECLARE y : BOOLEAN
INPUT y  // Error: Undefined type conversion from STRING to BOOLEAN
```

\
**IF Selection**:
```
IF <condition> THEN
    ...
ENDIF

IF <condition> THEN
    ...
ELSE
    ...
ENDIF
```
* ELSE IFs are not explicitly defined by CIE Pseudocode, but I've included them anyway.
```
IF <condition> THEN
    ...
ELSE IF <condition> THEN
    ...
ELSE
    ...
ENDIF
```
\
**REPEAT...UNTIL loops**:
```
REPEAT
    ...
    ...
UNTIL <condition>
```
\
**FOR loops**:
```
FOR <identifier> = 0 TO 10
    ...
NEXT <identifier>

FOR <identifier> = 0 TO 10 STEP 2  // Increase by 2 every step
    ...
NEXT <identifier>
```
* If \<identifier> isn't defined, then it will define it as INTEGER.

```
DECLARE sum : INTEGER
sum = 0
FOR i = 0 TO 10
    sum = sum + i
NEXT i
OUTPUT sum
```
* You cannot iterate using a non-INTEGER index.
```
DECLARE x : FLOAT
FOR x = 0 TO 10  // Unable to iterate using type FLOAT
    ...
NEXT x
```
\
**Scoping**
```
FOR i = 0 TO 10
    DECLARE x : INTEGER
    x = i
NEXT i

x = 2  // Unknown identifier: x
```
* Variables will carry over to inner blocks
```
DECLARE x : INTEGER
FOR i = 0 TO 10
    DECLARE x : INTEGER  // Re-declaration of identifier x
NEXT i
```

\
**Expressions**
```
DECLARE x : INTEGER
x = 2

if x == 2 THEN // True
    OUTPUT "Hello!"
ENDIF
```
* Brackets not supported yet.