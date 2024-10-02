aggregate = set("$*!=%~>")
simple = set("+-:_#,(")

# Return a tuple of (command, args), where command is a string and args is an array
async def handle_input(input):
    args = []
    message = input.decode()
    lst = message.split("\r\n")

    i = 0
    while i < len(lst):
        # Handle bulk strings properly
        if lst[i] and lst[i].startswith("$"):
            length = int(lst[i][1:]) 
            i += 1 
            if length > 0 and i < len(lst):
                args.append(lst[i])
        elif lst[i] and lst[i][0] not in aggregate and lst[i][0] not in simple:
            args.append(lst[i])
        i += 1

    return args

async def make_bulk_string(value):
    return b"$" + str(len(value)).encode() + b"\r\n" + value.encode() + b"\r\n"


