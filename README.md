# My computer
This is some code for my computer.

Ensure you have `pip install parsimonious`

# Tsunami (the programming language) documentation
`.tn` files (TsuNami)
## Lines of code
All statements separated by `;`, all number values specified as `<num>` and are either decimal (e.g. `123`), hex (e.g. `0x8D` or `$8D`) or binary (e.g. `0b00110100` or `&00110100`)

Opcodes are written as `SSSS M C`; S being the instruction, M being the mode and C being the carry bit (**if left out, the carry bit is `1`**).

### Order of operations quick reference
This is when evaluating a function
- Expressions without brackets (e.g. `!var` as opposed to `{var1 + var2}`)
- Other expressions
- Invert
- Decrement/increment
- Operator

### Statements
Written as just variables, with operations between them.
#### Variables
##### How variables are used
When storing a variable, it's just allocating a point in RAM - so every time it sees that name, it's just using that point in RAM.
##### Variable types
###### Named variables
- Place at start of function to be function-specific or at the start of files to have them globally accessible
- Name in square brackets (e.g. `[name]`)
- Can be set to a specific point in ram instead of added to the end of the list: e.g. `[name = @100]` (optional spacing)
- *Definitions* not separated by semicolons
- Must only include `[a-zA-Z0-9_]` in name
- The funny thing is, because I remove all spaces before processing you *can* have spaces in variable names. I would advise against it as it isn't common practice, but really you can do what you want.
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

You can also use instead:
`@<num>` (e.g. `@123`, `@0x7E`) to directly reference RAM values (instead of being hidden behind a name)
##### Specifying registers
**Both:**
- `%RAM` - the RAM. Requires an address, otherwise it'll be quite funky.
- `%DA` - the direct address register. Reads from the address (so set write device to `%NULL`), outputs to the data bus.
- `%A` / `%B` - the A or B registers (for the ALU). *These will be read using a 2-step instruction*, using the ALU to take the value and store it in O and use O as the read address.
- `%OUT` / `%O` - out register. When writing to, it uses the ALU output instead of whatever's on the data bus, so when writing to, use `%NULL` as read.
**For pros only:** (keep in mind this will harm readability of code, so only use when necessary)
- `%[num]` - the register at that read/write address

TODO:
- Have stuff for the out register or dereferencing register

#### Statements list
- `[null]` = don't need to specify
- `[num]` = number
- `[var]` = variable
- `[reg]` = register
- `[exp]` = expression without curly braces (just on outermost expression)
TODO: Read register but with address

| Name | Command | Description | Example |
| -- | -- | -- | -- |
| Noop | `NOOP` | Do nothing, just increment a CPU cycle | `NOOP;` |
| ReadWrite | `[reg A]<-[num/var/exp/reg/null B]` or `[num/var/exp/reg/null B]->[reg A]` with optional `#[num C]` on end | Read value of B and store it in A, using an address value of C | `%A <- %B;`, `->%O #000000` |
| Assign | `[var/reg A] = [num/var/exp/reg B]` | Read B and store it in A | `variable = 1;` |
| Expression | `[exp]` | Run an expression. Get the result using the `%OUT` register. | `variable + 5;variable2 = %OUT` |

**Notes for ReadWrite/Assign:**
reading from A or B takes an extra cycle 
TODO: It takes 3 instead of 2

#### Expressions
- `[num]` = number
- `[var]` = variable
- `[reg]` = register
- `[exp]` = expression
- `[op]` = operation (see operations below)

Note the curly brackets `{}` on the perform operations, but not on the others.
When used in place of a variable/number/register (expressions in expressions are handled separately), the out register is used.

Formats:
| Description | Format | What it equates to |
| -- | -- | -- |
| Perform operations | `{[num/var/reg/exp A] [op] [num/var/reg/exp B]}` | `%A<-[num/var/exp A];%B<-[num/var/exp B];%OUT<-%NULL#[opcode];` (if one is an expression; `[exp];%X<-%OUT` is used) |
| Increment | `[var/reg]++` | Add 1 to var | `variable++;` | `%A<-[var];%OUT<-%NULL#[opcode for A plus 1; 0000 0 0]` |
| Decrement | `[var/reg]--` | Decrease 1 from var | `variable--;` | `%A<-[var];%OUT<-%NULL#[opcode for A minus 1; 1111 1]` |
| Invert | `![var/reg]` | Invert var | `!var;` | `%A<-[var];%OUT<-%NULL#[opcode for not A; ]` |

#### Operators
##### Things to remember
- All spacing will be removed. So `A & !B` will be `A&!B`, using the `&!` operator.
- `!!` will be reduced to nothing, `!!!` to `!`, `!!!!` to nothing, etc.
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
TODO: Bit shifting

#### Substitutions
- Any equation using just numbers in regular brackets `()` (e.g. `(0x32 + 123)`) will be converted before compiling.

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
