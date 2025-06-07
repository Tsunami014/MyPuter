# My computer
This is some code for my computer.

Ensure you have `pip install parsimonious`

# Tsunami (the programming language) documentation
`.tn` files (TsuNami)
## Lines of code
All statements separated by `;`, all number values specified as `<num>` and are either decimal (e.g. `123`), hex (e.g. `0x8D`) or decimal (e.g. `0b00110100`)

Opcodes are written as `SSSS M C`; S being the instruction, M being the mode and C being the carry bit (**if left out, the carry bit is `1`**).

### Order of operations quick reference
This is when evaluating a function
- Expressions
- Invert
- Decrement/increment
- Operator

### Statements
Written as just variables, with operations between them.
#### Variables
##### How variables are used
When storing a variable, it's just allocating a point in RAM - so every time it sees that name, it's just using that point in RAM.
##### Defining a variable
- Place at start of function to be function-specific or at the start of files to have them globally accessible
- Name in square brackets (e.g. `[name]`)
- Can be set to a specific point in ram instead of added to the end of the list: e.g. `[name = @100]` (optional spacing)
- *Definitions* not separated by semicolons
- Must only include `[a-zA-Z0-9_]` in name
E.g.
```
func_name:
    [VarName]
    [Another_variable_name=@0x5F]
    VarName <- 0;
    Another_variable_name <- VarName;
END func_name

func_name2:
    [var1]
    [var2=@123] #> var2 is at address 123
    var2 <- 456;
    var1 <- @123; #> var1 gets set to var2 - the memory address at ram addr 123
END func_name2
```

Instead of a variable name, you can use these in place of it:
- `@<num>` (e.g. `@123`, `@0x7E`) to directly reference RAM values (instead of being hidden behind a name)
- Special variables:
    - `%NULL` - NOOP (only in certain cases)
    - `%OUT` / `%O` - out register (read only; also automatically used when assigning with `=`)

- Have stuff for the out register or dereferencing register

#### Statements list
- `[num]` = number
- `[var]` = variable
- `[exp]` = expression
- `[op]` = operation (see operations below)

Special flags:
- `ADDR`: can specify `#<num>` (e.g. `#0b01010101`) to set the address to that value
- `NULLABLE`: *can* use NULL in specified values

| Name | Command | Description | Example | What it equates to | Special flags |
| -- | -- | -- | -- | -- | -- |
| Noop | `NOOP` | Do nothing, just increment a CPU cycle | `NOOP;` | N/A |  |
| ReadWrite | `[var A]<-[num/var/exp B]` or `[num/var/exp B]->[var A]` | Read value of B and store it in A | `variable <- 1;` | N/A | Addr, NULLABLE: A/B |
| Assign | `[var A] = [num/var/exp B]` | Read variable B and store it in A | `variable = 1;` | `[var A]<-[num/var B]` |  |
| Operation | `[num/var A] [op] [num/var B]` | Read nums/vars A and B, store in registers A & B and perform ALU op on them (get output from `%OUT`) | `variable + 5;` | `%A<-[num/var A];%B<-[num/var B];%OUT<-%NULL#[opcode]` |  |
| Assign with operation | `[var A] = [num/var B] [op] [num/var C]` | Read nums/vars B and C, store in registers A & B and perform ALU op on them to store the result in var A | `variable = variable2 + 5;` |  |  |
| Increment | `[var]++` | Add 1 to var | `variable++;` | `%A<-[var];%OUT<-%NULL#[opcode for A plus 1; 0000 0 0]` |  |
| Decrement | `[var]--` | Decrease 1 from var | `variable--;` | `%A<-[var];%OUT<-%NULL#[opcode for A minus 1; 1111 1]` |  |
| Invert | `![var]` | Invert var | `!var;` | `%A<-[var];%OUT<-%NULL#[opcode for A plus 1; 0000 1]` |  |
TODO: Bit shifting

#### Expressions
An expression is contained within curly braces `{}`.
When used in place of a variable/number (expressions in expressions are handled separately), the out register is used.

Formats:
| Format | Description | What it equates to |
| -- | -- | -- |
| `{[num/var/exp A] [op] [num/var/exp B]}` | `%A<-[num/var/exp A];%B<-[num/var/exp B];%OUT<-%NULL#[opcode];` (if one is an expression; `[exp];%X<-%OUT` is used) |

#### Operators
##### Things to remember
- All spacing will be removed. So `A & !B` will be `A&!B`, using the `&!` operator.
- `!!` will be reduced to nothing, `!!!` to `!`, etc.
- Nots will be checked if they can be combined with the operator; e.g. `!A & B` will be converted to `A !& B`
##### Table
| Operator | Name | Selection & Mode |
| -- | -- | -- |
| `+` | A plus B | `1001 0` |
| `\|` | A or B | `1000 0` |
| `~\|` | A nor B | `0001 1` |
| `!\|` | not(A) or B | `1000 1` |
| `\|!` | A or not(B) | `1101 1` |
| `&` | A and B | `1101 1` |
| `~&` | A nand B | `1101 1` |
| `!&` | not(A) and B | `0010 1` |
| `&!` | A and not(B) | `0111 1` |
| `^` | A xor B | `0110 1` |
| `~^` | not(A xor B) | `1001 1` |

#### Substitutions
- Any equation using just numbers in brackets (e.g. `(0x32 + 123)`) will be converted before compiling.

## Various bits and bobs
- Comments: `#> inline comment <#` or `#> Comment to end of line` or `#>> Multiline inline comment <<#`
- Defining a function:
```
name:
    #> Code here
END
```
- Functions cannot be created inside other functions
- Functions ran are `init` and `tick` functions

## To come later
- Directly writing in RAM at the start of the code to have some things like tables ov values (which can be at set positions)
- Jump instructions to have only one necessary tag; `main`
