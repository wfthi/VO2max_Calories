import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

"""
Various extimates of VO2max

https://www.verywellfit.com/what-is-vo2-max-3120097

VO2max in mL/kg/min

VO2 Max Norms for Men
Age	Very Poor	Poor	Fair	Good	Excellent	Superior
13-19	Under 35.0	35.0-38.3	38.4-45.1	45.2-50.9	51.0-55.9	Over 55.9
20-29	Under 33.0	33.0-36.4	36.5-42.4	42.5-46.4	46.5-52.4	Over 52.4
30-39	Under 31.5	31.5-35.4	35.5-40.9	41.0-44.9	45.0-49.4	Over 49.4
40-49	Under 30.2	30.2-33.5	33.6-38.9	39.0-43.7	43.8-48.0	Over 48.0
50-59	Under 26.1	26.1-30.9	31.0-35.7	35.8-40.9	41.0-45.3	Over 45.3
60+	Under 20.5	20.5-26.0	26.1-32.2	32.3-36.4	36.5-44.2	Over 44.2

VO2 Max Norms for Women
Age	Very Poor	Poor	Fair	Good	Excellent	Superior
13-19	Under 25.0	25.0-30.9	31.0-34.9	35.0-38.9	39.0-41.9	Over 41.9
20-29	Under 23.6	23.6-28.9	29.0-32.9	33.0-36.9	37.0-41.0	Over 41.0
30-39	Under 22.8	22.8-26.9	27.0-31.4	31.5-35.6	35.7-40.0	Over 40.0
40-49	Under 21.0	21.0-24.4	24.5-28.9	29.0-32.8	32.9-36.9	Over 36.9
50-59	Under 20.2	20.2-22.7	22.8-26.9	27.0-31.4	31.5-35.7	Over 35.7
60+	Under 17.5	17.5-20.1	20.2-24.4	24.5-30.2	30.3-31.4	    Over 31.4

Some definition

anaerobic threshold:
- lactate starts to increase
- lactate accomodation zone
Entirely glycolisis at VT2: VCO2 increases faster than VO2,
lactate exponential growth
VT2 ventilatory threshold aka anadrobic threshold

Lactate threshold: 85% HRmax, 75% VO2max
- exercise intensity at which lactate concentration begins to
increase exponentially
"""

colo = ['blue', 'silver', 'darkgoldenrod', 'darkgreen',
        'darkmagenta', 'red', 'darkorange', 'gold', 'darkorchid',
        'aqua', 'cadetblue', 'darkolivegreen', 'burlywood', 'chartreuse',
        'chocolate', 'coral', 'cornflowerblue', 'black', 'darkkhaki', 'pink',
        'moccasin', 'limegreen']


def Cal_min_from_MET(MET, weight_kg):
    """
    Example
    -------
    >>> from calories_VO2max import Cal_min_from_MET
    >>> MET = 8.0
    >>> weight_kg = 65.
    >>> Cal_min_from_MET(MET, weight_kg)
    9.1
    """
    Cal_min = MET * weight_kg * 3.5 / 200.
    return Cal_min


def MET_bicycle(speed_kmh, weight_kg):
    """
    Compute the MET by kg of body weight given the cycling speed

    km/h  METS  Watts(weight=70kg)
    10     4.8     84
    15     5.9    103
    20     7.1    124
    25     8.4    147
    30     9.8    172

    Example
    -------
    >>> from calories_VO2max import *
    >>> speed_kmh = 25.
    >>> weight_kg = 50.
    >>> METs_bicycle, Watt_bicycle = MET_bicycle(speed_kmh, weight_kg)
    >>> print('Bicycle speed:',speed_kmh,'weight:',
    ...       weight_kg,'Cal/min:', Cal_min_from_MET(METs_bicycle,
    ...       weight_kg))
    Bicycle speed: 25.0 weight: 50.0 Cal/min: 7.393750000000001
    """
    speed = np.array([10., 15., 20., 25., 30.])
    METs = np.array([4.8, 5.9, 7.1, 8.4, 9.8])
    Watts_per_kg = np.array([84., 103., 124., 147., 172.])
    Watts_per_kg = Watts_per_kg / weight_kg
    coeff1 = np.polyfit(speed, METs, 1.)
    coeff2 = np.polyfit(speed, Watts_per_kg, 1.)
    return coeff1[0] * speed_kmh + coeff1[1], coeff2[0] * speed_kmh + coeff2[1]


def VO2_bicycle(Power_Watts, weight_kg):
    """
    Compute the VO2 while cycling

    Input Power in Watts, weight of the person in kg

    Return cycling VO2

    Most pro cyclists produce about 200 to 300 watts on average during a
    four-hour tour stage. The recreational rider, on the other hand, might
    be only able to sustain this wattage during a 45-minute or hour-long
    spin class.
    https://furthermore.equinox.com/articles/2015/06/how-to-train-with-watts

    http://forms.acsm.org/16tpc/PDFs/34b%20Moriarity.pdf

    analyticcycling.com

    https://sites.google.com/site/compendiumofphysicalactivities/help/unit-conversions

    Leg Ergometry

    for power outputs of 300–1,200 kgm/min, or 50-200 watts,
    and speeds of 50–60 rpm

    VO2 = [1.8 (work rate) ÷ body mass in kg] + 7

    *You may need to convert watts to kgm/min (1 watt = 6 kgm/min).
    The numbers 1.8 and 7 are constants that refer to the following:
    1.8 = oxygen cost of producing 1 kgm/min of power output
    7 = oxygen cost of unloaded cycling plus resting oxygen consumption
    1.8 x 6 = 10.8

    Example
    -------
    >>> from calories_VO2max import *
    >>> Power_Watts = 100.
    >>> weight_kg = 63.
    >>> VO2_bicycle(Power_Watts, weight_kg)
    24.142857142857142
    """
    return 10.8 * (Power_Watts / weight_kg) + 7.


def BMR(W, H, A, F, gender, Katch_McArdle=False):
    """
    Estimate the Basal Metabolic Rate (BMR)

    BMR Definition: The Basal Metabolic Rate (BMR) is the number of
    calories burned as the body performs basic (basal) life-sustaining
    function.
    Commonly also termed as Resting Metabolic Rate (RMR), which is the calories
    burned if stayed in bed all day.

    https://www.calculator.net/bmr-calculator.html
    The three equations used by the calculator are listed below:

    Mifflin-St Jeor Equation:
    For men: BMR = 10W + 6.25H - 5A + 5
    For women: BMR = 10W + 6.25H - 5A - 161

    The code uses by default the revised Harris-Benedict Equation

    Revised Harris-Benedict Equation:
    For men: BMR = 13.397W + 4.799H - 5.677A + 88.362
    For women: BMR = 9.247W + 3.098H - 4.330A + 447.593

    Katch-McArdle Formula:
    BMR = 370 + 21.6(1 - F)W
    where:

    W is body weight in kg
    H is body height in cm
    A is age
    F is body fat in percentage

    gender = 1 female
           = 0 male

    Example
    -------
    >>> from calories_VO2max import *
    >>> W = 63.
    >>> H = 169.
    >>> A = 51.
    >>> F = 19.
    >>> BMR(W, H, A, F, 0)  # kcal aka Cal per day
    1436.25
    """
    if Katch_McArdle:
        BMR = 370 + 21.6 * (1. - F) * W
    else:  # Revised Harris-Benedict Equation
        BMR = (1. - gender) * (10 * W + 6.25 * H - 5 * A + 5) +\
            gender * (10 * W + 6.25 * H - 5 * A - 161)
    return BMR


def calories_per_hr_from_MET(BMR, MET):
    """
    The METS values are provided by "The Compendium of
    Physical Activities 2011".
    Calorie(Kcal) ＝ BMR x Mets / 24 x hour
    https://keisan.casio.com/exec/system/1350891527

    Example
    -------
    >>> BMR = 1500.
    >>> MET = 8.
    >>> calories_per_hr_from_MET(BMR, MET)
    500.0
    """
    return BMR * MET / 24.


def MET_waking(speed_kmh, grade_percent):
    walking_VO2, _ = VO2_walking(speed_kmh, grade_percent)
    return walking_VO2 / 3.5


def VO2_walking(speed_kmh, grade_percent):
    """
    VO2 when walking on a treadmill with inclination

    American College of Sports Medicine, (2000)
    ACSM's Guidelines for Exercise Testing and Prescription, 6.
    (See Latest Edition)
    https://www.slideshare.net/hunchxx/met-calnew

    Bubb WJ, Martin AD, Howley ET (1985)
    Predicting oxygen uptake during level walking at speeds of 80
    to 130 meters per minute. Journal of Cardiac Rehabilitation, 5(10),
    462-465.

    https://exrx.net/Calculators/WalkRunMETs

    """
    rest = 3.5  # 1 MET -= 3.5 VO2
    s = speed_kmh * 1e3 / 60.
    horizontal = 0.1 * s
    vertical = 1.8 * s * grade_percent/100.
    walking_VO2 = horizontal + vertical + rest
    net_walking_VO2 = horizontal + vertical
    return walking_VO2, net_walking_VO2


def energy_expenditure_kg(gender, age, weight, VO2max, heart_rate):
    """
    Compute the energy expenditure given some morphological data and data
    from the sensors unist of kcal (Cal)

    Prediction of energy expenditure from heart rate monitoring during
    submaximal exercise
    April 2005 Journal of Sports Sciences 23(3):289-97
    DOI: 10.1080/02640410470001730089

    Quotation from the article above:
    The calorie calculation is of course based on a number of factors and
    takes into account gender,age, weight and HR. We have discussed this
    with various international bodies including the Chief Science Officer at
    ACE (American College of Exercise) who's feedback was as follows;

    The equation that we are using is the most accurate given the variables
    that we know about the user (age, weight, gender & HR).

    The equation proves to be very accurate and maintains a linear relationship
    in the range in which  most users exercise (95 bpm – 150 bpm).

    There is inherent variability the with the regression equation to perfect
    the relationship between HR and o2 uptake at higher HR’s. This is most
    notable for users who exercise above 150 bpm and have a high max HR. This
    may cause the equation to report a higher than actual caloric expenditure
    of up to 10-15% for the time over 150 bpm for this specific user.

    Since our equation uses 75% of the input variables, it is far
    superior to any calculation that a user would see on a cardiovascular piece
    of equipment, which uses the inputs of an average human and does not
    personalize the feedback to the extent that our equation does.

    The actual numbers in the formula are from the most accurate and
    accredited white paper journal in sports science for this calculation.
    To explain where they get those numbers from is a thesis from tests done
    Here is the white paper if you wanted to have a look:
    http://www.braydenwm.com/cal_vs_hr_ref_paper.pdf

    gender male = 1.0, female = 0.0

    This is the formula used by the MyZone belt

    Example
    -------
    >>> import numpy as np
    >>> from calories_VO2max import *
    >>> gender = 1.0
    >>> age = 48.
    >>> weight = 63.
    >>> VO2max = 48.
    >>> heart_rate = [110., 120., 130., 140., 150.]
    >>> EE_VO2max, EE = energy_expenditure_kg(gender, age, weight,
    ...                 VO2max, heart_rate)
    >>> EE_VO2max[0]
    7.454238630999999
    """
    if isinstance(heart_rate, list):
        heart_rate = np.array(heart_rate)
    if isinstance(VO2max, list):
        VO2max = np.array(VO2max)
    EE_VO2max = -59.3954 + gender * (-36.3781 + 0.271 * age + 0.394 * weight +
                                     0.404 * VO2max + 0.634 * heart_rate)\
        + (1. - gender) * (0.274 * age + 0.103 * weight + 0.380 * VO2max +
                           0.450 * heart_rate)
    EE = gender * (-55.0969 + 0.6309 * heart_rate + 0.1988 * weight +
                   0.2017 * age)\
        + (1. - gender) * (-20.4022 + 0.4472 * heart_rate -
                           0.1263 * weight + 0.074 * age)
    KJ_to_kcal = 0.239006
    return EE_VO2max * KJ_to_kcal, EE * KJ_to_kcal


def invert_Swain(percentage_VO2max):
    """
    Inverse of the Swain formula to get %HRmax given %VO2max
    """
    percentage_HRmax = 0.6463 * percentage_VO2max + 37.182
    return percentage_HRmax


def Swain(percentage_HRmax):
    """
    Swain DP, Abernathy KS, Smith CS, Lee SJ, Bunn SA.
    Target heart rates for the development of cardiorespiratory
    fitness. Med Sci Sports Exerc. January 1994. 26(1): 112–116.
    http://www.shapesense.com/fitness-exercise/calculators/heart-rate-and-percent-vo2max-conversion-calculator.aspx

    Example
    -------
    >>> from calories_VO2max import Swain
    >>> Swain(80.)
    66.2509670431688
    """
    percentage_VO2max = (percentage_HRmax - 37.182)/0.6463
    return percentage_VO2max


def VO2max_from_HR(HRmax, HRrest):
    """
    Basic formula to estimate VO2max based on the
    maximum heart rate HRmax in beats/min and the resting hear rate
    HRrest

    The result is a very crude estimate

    Example
    -------
    >>> from calories_VO2max import VO2max_from_HR
    >>> VO2max_from_HR(185., 65.)
    42.69230769230769
    """
    return 15. * (HRmax / HRrest)


def aerobic_threshold_from_lactate(HRmax, lactate_threshold_pcHR):
    """
    The heart rate at the aerobic threshold

    lactate_threshold_pcHR) = LTHR : lactate threshold heart rate ~ 85% HRmax
    https://www.podiumrunner.com/training/do-it-yourself-lactate-threshold-testing/

    Example
    -------
    >>> from calories_VO2max import aerobic_threshold_from_lactate
    >>> HRmax = 185.
    >>> lactate_threshold_pcHR = HRmax * 0.85  # 85%
    >>> aerobic_threshold_from_lactate(HRmax, lactate_threshold_pcHR)
    141.0337837837838
    """
    from_lactate_to_anabolic = 30.  # 25-35
    return (lactate_threshold_pcHR * 1e-2 *
            HRmax - from_lactate_to_anabolic) / HRmax * 100.  # in percentage


def anabolic_threshold_Fair(age, level):
    """
    Estimate the anabolic threshold

    https://experiencelife.com/article/the-at-factor/

    Fair Method: Formula
    Most people experience the best results by gauging their AT from
    the methods above (see website)
    But in the absence of any testing protocol, you can estimate your
    AT using the following method  developed by Phil Maffetone, a widely
    respected coach and sports physician. Just keep in mind that
    any method that relies on a formula introduces a larger margin for error.

    1. Subtract your age from 180

    2. Adjust this number by selecting one of the following categories:

    level 0) If you have not exercised for more than one year or are recovering
    from a major illness (heart disease, any operation or hospital stay, etc.),
    or if you are age 65 or older, subtract 10.
    level 1) If you have been exercising for up to two years at least four
            times a week, subtract zero.
    level 2) If you have been exercising for more than two years, at least
             four times a week, add five.
    level 3) If you are a competitive athlete, add 10.

    For example, if you are 30 years old and began exercising moderately
    four times a week three years back, your number would be 155 beats per
    minute (180 – 30 = 150, then 150 + 5 = 155). This number represents your
    estimated maximum aerobic-exercise heart rate, or the rate at which you
    remain just below your AT. Once you have this number, consider trying one
    of the observed exertion tests described above to see how those AT results
    correspond to the formula-estimated figure.

    level from 0 to 4
    """
    adjustement = [-10., 0., 5., 10.]
    return 180. - age + adjustement[level]  # in bpm


def RER():
    """
    RER Respiratory exchange ratio = VCO2 / VO2 measured from expired air

    Used by cal_VO2_RER
    """
    RQ_tab = np.arange(0.71, 1.001, 0.01)
    RQ_tab = np.append(0.707, RQ_tab)
    RERcal_CHOpc = np.array([0.0, 1.1, 4.76, 8.40, 12., 15.6, 19.2, 22.3, 26.3,
                             29.9, 33.4, 36.9, 40.3, 43.8, 47.2,
                             50.7, 54.1, 57.5, 60.8, 64.2, 67.5, 70.8, 74.1,
                             77.4, 80.7, 84., 87.2,
                             90.4, 93.6, 96.8, 100.])
    RERcal_Fatpc = 100. - RERcal_CHOpc
    RERcal = np.array([4.686, 4.690, 4.702, 4.714, 4.727, 4.739,
                       4.751, 4.764, 4.776, 4.788, 4.801, 4.813, 4.825,
                       4.838, 4.850, 4.862, 4.875, 4.887, 4.899, 4.911,
                       4.924, 4.936, 4.948, 4.961, 4.973, 4.985, 4.998,
                       5.010, 5.022, 5.035, 5.047])
    return RQ_tab, RERcal, RERcal_Fatpc, RERcal_CHOpc


def cal_VO2_RER(VO2_input, RQ_input):
    """
    VO2 in mL/min/kg

    Kcal = VO2 (L/min) x RER caloric equivalent x time (min))
    RQ : Respiratory quotient = VCO2 / VO2 for the cell
    VO2 absolute : Oxygen consumption
    VCO2 Carbon dioxide production
    RER Respiratory exchange ratio = VCO2 / VO2 measured from expired air
    Kcal/L The energy release from metabolism for each L of VO2

    The RQ and RER are the same measurement, yet as the
    components of the measure are obtained differently (cell respiration vs
    exhaled air from the lung),
    under certain circumstances the values can differ.

    The maximal range of RQ is from 0.7 to 1.0 The range of RER may
    vary from <0.7 to >1.2

    Assume RQ = RER
    Fat_caloric_density = 4 kcal/g
    CHO_caloric_density = 9 kcal/g

    Used by cal_RER
    """
    RQ_tab, RERcal, RERcal_Fatpc, RERcal_CHOpc = RER()
    f = interp1d(RQ_tab, RERcal, fill_value='extrapolate')
    if isinstance(RQ_input, float):
        RQ_input = [RQ_input]
    if isinstance(VO2_input, float):
        VO2_input = [VO2_input]
    cal_min_kg = []
    for VO2, RQ in zip(VO2_input, RQ_input):
        VO2_L_min = VO2 * 1e-3
        cal_min_kg.append(VO2_L_min * f(RQ))
    # return float if there is only one value
    if len(VO2_input) == 1:
        return cal_min_kg[0], RERcal, RERcal_CHOpc[0], RERcal_Fatpc[0]
    else:
        return cal_min_kg, RERcal, RERcal_CHOpc, RERcal_Fatpc  # Kcal/kg/min


def cal_RER(percentage_HR, HRmax, HRrest, VO2max):
    """
    Estimate the RER Respiratory exchange ratio

    HRmax in bpm
    HRest in bpm
    anabolic_threshold in percentage of HRmax
    VO2max relative in ml/kg/min

    With precise RER calculation

    Example
    -------
    >>> from calories_VO2max import *
    >>> HRmax = 185.
    >>> HRrest = 65.
    >>> percentage_HR = 75.  # % during the exercise
    >>> VO2max = VO2max_from_HR(HRmax, HRrest)
    >>> cal_RER(percentage_HR, HRmax, HRrest, VO2max)
    0.12434179086538462
    """
    frac_VO2max = (percentage_HR * 1e-2 * HRmax - HRrest) / (HRmax - HRrest)
    VO2work = VO2max * frac_VO2max
    cal_min_kg, _, _, _ = cal_VO2_RER(VO2work, percentage_HR / 100.)
    return cal_min_kg


def calories_kg_HR_HRr(percentage_HR, HRmax, HRrest, VO2max):
    """
    From %Max Hear Rate to kcal/min/kg (Cal/min/kg) when ones
    knows her.his VO2max value using the Swain formula knowing VO2max

    This funciton does not use the Swain formula

    results in Cal/min

    %MaxHR = 0.6464 %VO2max + 37.182
    Swain DP, Abernathy KS, Smith CS, Lee SJ, Bunn SA
    Target heart rates for the development of cardiorespiratory
    fitness. Med Sci Sports Exerc. January 1994. 26(1): 112–116.
    http://www.shapesense.com/fitness-exercise/calculators/heart-rate-and-percent-vo2max-conversion-calculator.aspx

    https://sites.google.com/site/compendiumofphysicalactivities/help/unit-conversions
    1 MET = 3.5 ml/kg/min -> 1 VO2work = 3.5 MET
    1 MET = 1 kcal/kg/hr
    -> VO2 = 3.5 kcal/kg/hr

    VO2work = %VO2max x VO2max : VO2 during the exercise

    Kcal = VO2 (L/min) x RER caloric equivalent x time (min)

    RQ = REspiratory quotient
    RER = Respiratory Exchange Ratio = VCO2/VO2
    RER can be higher than 1
    RER 0.7 to 1 : 0.7 mostly Fat, 1.0 moslt carbo-hydrates light
    exercise anabolic threshold
    1.0 rough estimate of the anabolic threshold
    1.1 to 1.15: maximum

    Michael Scarlett
    Matty Graham Q_dot: cardiac output
    VO2 = Q_dot * (CpO2 - CvO2 )
    CpO2 pulmonary concentration
    CvO2 muscular
    anabolic threshold or lactitc threshold: sustain around the
    lactic threshold. Lactitc acid is the product of effort but does
    not produce fatigue
    The anabolioc threshold is the fraction of the VO2max where one can
    sustain the effort.
    Difficult to improve VO2max. It is mostly determined by genetics although
    not everyone has reached the genetic limits. For example the HRmin can
    decrease.
    Interval training:
    VO2max 1:1 work/rest 1-4 min work reach zone 5 Glycolisis
    AT     2:1 work/rest 4-15 min work  zone 4
    ventilatory  Physiology Made Easy with Dr Aamer Sandoo
    ventilatory threshold ~ anaerobic threshold ~ lactate threshold
    low intensity : oxidative phosphorylation -> ATP aerobic

    Oxidative phosphorylation takes place in the inner
    mitochondrial membrane, in contrast with most of the reactions
    of the citric acid cycle
    and fatty acid oxidation, which take place in the matrix.

    https://www.ntnu.edu/cerg
    """
    frac_VO2max = (percentage_HR*1e-2*HRmax-HRrest)/(HRmax-HRrest)
    Cal_min_kg = frac_VO2max * VO2max / 3.5 / 60.
    return Cal_min_kg


def calories_kg_HR(percentage_HR, VO2max):
    """
    From %Max Hear Rate to kcal/min (Cal/min) when ones knows
    her/his VO2max value using the Swain formula knowing VO2max

    results in Cal/min

    %MaxHR = 0.6464 %VO2max + 37.182
    Swain DP, Abernathy KS, Smith CS, Lee SJ, Bunn SA.
    Target heart rates for the development of cardiorespiratoryfitness.
    Med Sci Sports Exerc. January 1994. 26(1): 112–116.
    http://www.shapesense.com/fitness-exercise/calculators/heart-rate-and-percent-vo2max-conversion-calculator.aspx

    https://sites.google.com/site/compendiumofphysicalactivities/help/unit-conversions
    1 MET = 3.5 ml/kg/min -> 1 VO2work = 3.5 MET
    1 MET = 1 kcal/kg/hr
    -> VO2 = 3.5 kcal/kg/hr

    VO2work = %VO2max x VO2max : VO2 during the exercise

    Kcal = VO2 (L/min) x RER caloric equivalent x time (min)
    """
    Cal_min_kg = (percentage_HR-37.182) / 0.6463 / 100. * VO2max / 200.
    return Cal_min_kg  # per weight in kg


def MyZone_VO2_plot(VO2max_range, HRmax, HRrest,
                    age, weight_kg, gender, MyZoneVO2max=False):
    """
    Make plots using MyZone heart rate monitor formula

    gender : male = 1., femal = 0.

    Example
    -------
    >>> from calories_VO2max import *
    >>> weight_kg = 61.5
    >>> VO2max_range = np.arange(30.,71.,10.)
    >>> age = 48.
    >>> HRmax = 185.
    >>> HRrest = 60.
    >>> MyZone_VO2_plot(VO2max_range, HRmax, HRrest,
    ...                 age, weight_kg, 1, MyZoneVO2max=True)
    >>> MyZone_VO2_plot(VO2max_range, HRmax, HRrest,
    ...                 age, weight_kg, 1, MyZoneVO2max=False)
    >>> # ------------
    >>> weight_kg = 50.0
    >>> VO2max_range = np.arange(30.,61.,10.)
    >>> MyZone_VO2_plot(VO2max_range, HRmax, HRrest,
    ...                 age, weight_kg, 0, MyZoneVO2max=True)
    >>> MyZone_VO2_plot(VO2max_range, HRmax, HRrest,
    ...                 age, weight_kg, 0, MyZoneVO2max=False)
    """
    gender_name = ['Female', 'Male']
    percentage_HR = np.arange(50., 101., 1.)
    heart_rate = HRmax * percentage_HR / 100.
    for count, V2 in enumerate(VO2max_range):
        Cal_min = calories_kg_HR(percentage_HR, V2)
        Cal_min2 = calories_kg_HR_HRr(percentage_HR, HRmax, HRrest, V2)
        plt.plot(percentage_HR, Cal_min, c=colo[count],
                 label='VO2max 1:' + str(V2), ls='-')
        plt.plot(percentage_HR, Cal_min2, c=colo[count],
                 label='VO2max 2:' + str(V2), ls='--')
        EEVO2max, EE = energy_expenditure_kg(gender, age, weight_kg,
                                             V2, heart_rate)
        if (MyZoneVO2max):
            Eplot = EEVO2max / weight_kg
            label = 'FirstBeat MyZone VO2max'+str(V2)
            plt.plot(percentage_HR, Eplot, c=colo[count],
                     linewidth=1, ls='-.', label=label)
    if (not MyZoneVO2max):
        Eplot = EE / weight_kg
        label = 'FirstBeat MyZone'
        plt.plot(percentage_HR, Eplot,
                 c='black', linewidth=3, ls='-.', label=label)
    plt.title(gender_name[gender] + ' weight ' + str(weight_kg))
    plt.xlabel('% HRmax')
    plt.ylabel('Cal/min/kg')
    plt.legend(frameon=False, fontsize=8)
    plt.grid(True)
    plt.show()

    for count, V2 in enumerate(VO2max_range):
        Cal_min = calories_kg_HR(percentage_HR, V2)
        Cal_min2 = calories_kg_HR_HRr(percentage_HR, HRmax, HRrest, V2)
        EEVO2max, EE = energy_expenditure_kg(gender, age, weight_kg, V2,
                                             heart_rate)
        if (MyZoneVO2max):
            Eplot = EEVO2max/weight_kg
            tit = 'MyZone VO2max ' + gender_name[gender] +\
                  '  weight ' + str(weight_kg)
        else:
            Eplot = EE/weight_kg
            tit = 'Myzone ' + gender_name[gender] + ' weight ' + str(weight_kg)
        plt.plot(percentage_HR, Eplot/Cal_min, c=colo[count],
                 label='VO2max 1:' + str(V2), ls='-')
        plt.plot(percentage_HR, Eplot/Cal_min2, c=colo[count],
                 label='VO2max 2:' + str(V2), ls='--')
    plt.title(tit)
    plt.xlabel('% HRmax')
    plt.ylabel('MyZone/VO2max method')
    plt.legend(frameon=False, fontsize=8)
    plt.grid(True)
    plt.show()


def Heart_rate_reserve(HRmax, HRrest):
    """
    Compute the heart rate reserve

    ¹The Surprising History of the "HRmax=220-age" Equation,
    Robert A. Robergs and Roberto Landwehr, Journal of Exercise
    Physiology Volume 5 Number 2 May 2002.
    https://experiencelife.com/article/the-at-factor/
    """
    return HRmax-HRrest


def aerobic_training(HRmax, HRrest):
    """
    https://www.concept2.com/indoor-rowers/training/tips-and-general-info/training-heart-rate-range
    aerobic training, take 50–75% of your HRR and add it to your RHR
    anaerobic threshold training, take 80–85% of your HRR and add
    it to your RHR
    """
    aerobic_level1 = 50.  # to 50%
    aerobic_level2 = 75.  # to 75%
    HRreserve = Heart_rate_reserve(HRmax, HRrest)
    return (HRreserve * (aerobic_level1 / 100.) + HRrest) / HRmax * 100., \
        (HRreserve * (aerobic_level2 / 100.) + HRrest) / HRmax * 100.


def anaerobic_training(HRmax, HRrest, anaerobic_level=80.):
    # anaerobic_level = 80., up to 85% for top athtelic
    HRreserve = Heart_rate_reserve(HRmax, HRrest)
    return (HRreserve * (anaerobic_level / 100.) + HRrest) / HRmax * 100.


def energy_expenditure(percentage_HR, weight_range_kg, age, VO2max,
                       HRmax, HRrest, gender):
    """
    Calculate the energy expenditure given the effort and various
    physiological data

    Inputs
    ------
    percentage_HR: float
        the percentage of HRmax during the exercise

    weight_range_kg: array of floats
        weight range considered kg

    age: float
        age in years

    VO2max: float
        estimate VO2max

    HRmax: float
        maximum Heart rate in beats/min

    HRrest: float
        Heart rate beats/min at rest

    gender: float
        gender male = 1.0, female = 0.0

    Returns
    -------
    : plot

    Example
    -------
    >>> from calories_VO2max import *
    >>> HRmax = 184.
    >>> HRrest = 55.
    >>> VO2max = 45.
    >>> weight_range_kg = [60.,70.] # kg
    >>> gender = 1.  # male = 1., female = 0.
    >>> age = 48.
    >>> percentage_HR = np.arange(50.,101.,1.)
    >>> energy_expenditure(percentage_HR, weight_range_kg,
    ...                    age, VO2max, HRmax, HRrest, gender)
    """
    heart_rate = HRmax * percentage_HR / 100.
    for count, kg in enumerate(weight_range_kg):
        Cal_min = calories_kg_HR_HRr(percentage_HR,
                                     HRmax, HRrest, VO2max)*kg
        EEVO2max, EE = energy_expenditure_kg(gender, age,
                                             kg, VO2max, heart_rate)
        plt.plot(percentage_HR, Cal_min,
                 c=colo[count], label='METs ' + str(kg) + ' kg')
        plt.plot(percentage_HR, EEVO2max,
                 c=colo[count], ls='--', label='FirstBeat VO2max')
        plt.plot(percentage_HR, EE, c=colo[count], ls='-.', label='Myzone')
    plt.title('VO2max:' + str(VO2max))
    plt.xlabel('% HR')
    plt.ylabel('Cal/min')
    plt.legend(frameon=False, fontsize=9)
    plt.grid(True)
    plt.show()


def VO2max_from_VO2_HR(VO2exercise, HR, HRmax, HRrest):
    """
    Return an estimate of the VO2max

    Input: VO2exercise, the VO2 value of the exercise
           HR  The Heart Rate
           HRmax The maximum Heart Rate
           HRrest The rest Heart Rate
    """
    if ((HR > HRmax) or (HR < HRrest)):
        return 0.
    fraction_VO2max = (HR-HRrest) / (HRmax-HRrest)
    VO2max = VO2exercise / fraction_VO2max
    return VO2max


def VO2max_from_METS(METS, HR, HRmax, HRrest):
    """
    From the METS value, e.g. at the treadmill
    and the Heart rate (or the fraction of the maximum Heart rate)
    estimates VO2max

    Example
    -------
    >>> from calories_VO2max import *
    >>> METS = 8.
    >>> HR = 140.
    >>> HRrest = 65.
    >>> HRmax = 185.
    >>> VO2max_from_METS(METS, HR, HRmax, HRrest)
    44.8
    """
    VO2exercise = 3.5 * METS  # 3.5 is the conversion from METS to VO2
    VO2max = VO2max_from_VO2_HR(VO2exercise, HR, HRmax, HRrest)
    return VO2max


def plot_threshold():
    HRmax = 185.
    HRrest = 65.
    age = 48.
    VO2max = VO2max_from_HR(HRmax, HRrest)
    tit = 'HRmax=' + str(HRmax) + 'HRrest=' + str(HRrest) +\
        'Approximate VO2max' + str(VO2max)
    print(tit)
    # 85. percent of the HRmax, reach 90% for top athlete
    lactate_threshold_pcHR = 85.
    percentage_HR = np.arange(50., 101., 1.)
    cal1 = calories_kg_HR_HRr(percentage_HR, HRmax, HRrest,
                              VO2max_from_HR(HRmax, HRrest))
    cal2 = calories_kg_HR(percentage_HR, VO2max)
    anabolic_threshold_pcHR_Fair = anabolic_threshold_Fair(age,
                                                           1) / HRmax * 100.

    aerobic_threshold_pcHR =\
        aerobic_threshold_from_lactate(HRmax, lactate_threshold_pcHR)

    cal3 = cal_RER(percentage_HR, HRmax, HRrest, VO2max)

    print('Aerobic threshold:', anabolic_threshold_pcHR_Fair,
          'Aerobic threshold pcHR:', aerobic_threshold_pcHR,
          'Lactate threshold:', lactate_threshold_pcHR)
    plt.plot(percentage_HR, cal1,
             label='%HR, HRmax, HRrest, VO2max')
    plt.plot(percentage_HR, cal2,
             label='%HR, VO2max uses Swain et al.')
    plt.plot(percentage_HR, cal3,
             label='%HR, HRmax, HRrest, VO2max, anabolic threshold')
    plt.title = tit
    plt.xlabel('% HRmax')
    plt.ylabel('Cal/min/kg')
    plt.legend()
    plt.grid(True)
    plt.show()


# -----------------------------------------------------------------------------------
if __name__ == "__main__":
    import doctest
    DOCTEST = True
    doctest.testmod(verbose=True, optionflags=doctest.ELLIPSIS)
