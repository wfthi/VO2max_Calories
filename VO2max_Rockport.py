"""
I've seen some sports watches measure VO2 max. How do they do this? Do they create their own formula, 
or do they use a preexisting one?

They tend to use the Firstbeat method, which was patented in 2012. It uses segments of the GPS tracking data 
and/or power data from the sports watch along with HR measure to estimate VO2 max. It's been shown to be 
~95% accurate compared to lab testing using inhaled/exhaled gas analysis.
"""


def VO2max_Rockport(age, weight_kg, time_min, HR, gender):
    """
    Rockport VO2max walk test

    Start your stopwatch and walk the entire distance of a 1 mile (1.6 km). 

    https://www.wikihow.com/Measure-VO2-Max

    gender: woman = 0
              man = 1

    10/11/2020 Wing-Fai Thi
    """
    weight_lbs = weight_kg / 2.2
    VO2max = 132.853 - (0.0769 * weight_lbs) - (0.3877 * age)+\
            (6.315 * gender) - (3.2648 * time_min) - (0.156 * HR)
    return VO2max


if __name__ == "__main__":
    age = 48. # yrs
    time_min = 20. # minutes
    weight_kg = 61.0
    HRmax = 184.
    HR = 0.75 * HRmax
    gender = 1
    print('VO2max:',VO2max_Rockport(age, weight_kg, time_min, HR, gender))
    pass