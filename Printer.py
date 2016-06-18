def print_hex_string_nicely(hex_string):
    index = 0
    result = ''
    while hex_string:
        result += '{:08x}: '.format(index)
        index += 16
        line, hex_string = hex_string[:32], hex_string[32:]
        while line:
            two_bytes, line = line[:4], line[4:]
            if two_bytes:
                result += two_bytes + ' '
        result = result[:-1] + '\n' 
        print result    
def hex_dump_packet(packet_data):
    print_hex_string_nicely(binascii.hexlify(packet_data))  

def print_it(x):
    print x