def get(id):
    p = open('passwords', 'r+')
    for line in p.read().split('\n'):
        fields = line.split(':')
        if fields[0] == id:
            return (fields[1], fields[2])
    return (None, None)

def user(id):
    return get(id)[0]

def pw(id):
    return get(id)[1]
