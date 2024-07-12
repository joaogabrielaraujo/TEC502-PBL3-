from Clock import Clock


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

