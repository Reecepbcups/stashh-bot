import time

def epoch_to_human(epoch_seconds):
    # 2022-09-01 14:18:05    
    tz = time.tzname[time.daylight]
    return time.strftime('%Y-%m-%d %Hh %Mm', time.localtime(epoch_seconds)) + f" {tz}"