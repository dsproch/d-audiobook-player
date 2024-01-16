

def milliseconds_to_time_string(timeInMilliseconds):
    timeInSeconds = timeInMilliseconds / 1000
    h = int(timeInSeconds // 3600)
    m = int(timeInSeconds % 3600 // 60)
    s = int(timeInSeconds % 3600 % 60)

    return '{:d}:{:02d}:{:02d}'.format(h,m,s)



    