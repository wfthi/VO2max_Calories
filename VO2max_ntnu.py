"""
    Predicting VO2peak from Submaximal- and Peak Exercise Models: The HUNT 3
    Fitness Study, Norway
        Henrik Loe1,2, Bjarne M. Nes1, Ulrik Wisløff1

    PLOS ONE | DOI:10.1371/journal.pone.0144873 January 21, 2016

    see HUNT3, NTNU projects

    Copyright (C) 2024  Wing-Fai Thi

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    https://inscyd.com/article/vo2max-charts-by-age-gender-sport/
    Male VO2max classification based on data from scientific literature for
    nonathletes

    VO2MAX CHART FOR MEN
    Age     Poor    Fair   Average  Good    Excellent
    ≤29    ≤24.9  25-33.9  34-43.9 44-52.9     53
    30-39  ≤22.9  23-30.9  31-41.9 42-49.9     50
    40-49  ≤19.9  20-26.9  27-38.9 39-44.9     45
    50-59  ≤17.9  18-24.9  25-37.9 36-42.9     43
    60-69  ≤15.9  16-22.9  23-35.9 36-40.9     41
    Keep in mind that these VO2max scores are for nonathletes.

    See also
    https://www.firstbeat.com/en/blog/whats-a-good-vo2max-for-me-fitness-age-men-and-women/

"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def VO2max_submaximal(incl, speed, weight, HR, age):
    """
    Predicting VO2peak from submaximal treadmill performance

    VO2max_submaximal(0.,7.5,63.,0.8*182.,47.)
    Objectiv: 7.5 km/h, flat surface, 80%, 10 min
    """
    VO2max = 35.25 + (1.276 * incl) + (6.402 * speed) - (0.196 * weight) -\
        (27.65 * HR / (215.336 - 0.73 * age))
    return VO2max


if __name__ == "__main__":
    # Example
    pdf_filename = 'VO2max_ntnu.pdf'
    pp = PdfPages(pdf_filename)
    incl_range = [0., 5., 10., 15., 20., 25.]  # percentage
    age = 25.  # age in year
    weight = 63  # in kg
    speed = np.array([3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0])  # km/h
    HRmax = 196.
    HR_range = np.array([0.65, 0.700001, 0.75, 0.8, 0.85]) * HRmax
    for incl in incl_range:
        for HR in HR_range:
            VO2max = VO2max_submaximal(incl, speed, weight, HR, age)
            plt.plot(speed, VO2max,
                     label=str(int(100. * HR / HRmax)) + '% HR$_{\mathrm{max}}$')
        plt.xlabel('Treadmill speed [km/h]')
        plt.ylabel('VO2$_{\mathrm{max}}$')
        plt.title(str(weight) + ' kg, ' + str(int(age)) + 'yrs, incl='+str(int(incl))+' %')
        plt.legend()
        plt.grid(True)
        plt.savefig(pp, format='pdf')
        plt.clf()
    pp.close()

