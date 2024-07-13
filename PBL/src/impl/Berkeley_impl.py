from Clock import Clock
import time

def colect_times(Clock: list[Clock]):
    list_times = []
    for i in range(len(Clock)):
        list_times.append(Clock[i].time)
    return list_times

def colect_drifts(Clock: list[Clock]):
    list_drifts = []
    for i in range(len(Clock)):
        list_drifts.append(Clock[i].drift)
    return list_drifts

def getAvarageClockTime(Clock: list[Clock]):
    list_times = colect_times(Clock)
    return sum(list_times)/len(list_times)


def seconds_to_hms(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    return hours, minutes, remaining_seconds

def hms_to_seconds(hours, minutes, seconds):
    return hours*3600 + minutes*60 + seconds
   
def syncronizeClocks(local_clock, average_time, sync_interval):
    time_difference = average_time - local_clock.time

    required_drift = time_difference/sync_interval

    original_drift = local_clock.drift
    local_clock.drift = required_drift

    for _ in range(sync_interval):
        local_clock.time.update_time(local_clock.drift)
        time.sleep(1)
    local_clock.drift = original_drift  # Restaurando o valor original do drift
