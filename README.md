# FENCE

FENCE is a tool for identifying length fields in unknown binary protocols. It supports identification of both fixed-length and variable-length fields.

## Usage

Enter the `code` directory and run:

```bash
cd code
python main.py --protocol pcapfilename
```

## Output

The program prints the length field identification result.

### Fixed-Length Length Field

If a fixed-length length field is identified, the program outputs:

```text
this protocol exists fixed-length length field
```

It also reports:

- `offset of length field`: the offset of the length field;
- `field length`: the length of the field.

### Variable-Length Length Field

If a variable-length length field is identified, the program outputs:

```text
this protocol exists variable-length length field
```

It also reports:

- `offset of length field`: the offset of the length field;
- `field length`: the length of the field.

### No Length Field

If no length field is identified, the program outputs:

```text
This protocol doesn't exist length field!
```

In this case, no length field offset or field length is reported.
