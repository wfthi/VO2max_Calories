def VO2max_Brigham_Young(weight_kg, time_min, HR, gender):
    """
    Brigham Young University Jog Test

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

    Start your stopwatch and lightly jog 1 mile. You can jog around
    a .25 mile (.40 km) track four times, or a 1 mile (1.6 km) flat surface

    https://www.wikihow.com/Measure-VO2-Max

    gender: woman = 0
            man = 1

    10/11/2020 Wing-Fai Thi
    """
    f = (0.1636 * weight_kg) + (1.438 * time_min) + (0.1928 * HR)
    VO2max = (1 - gender) * (100.5 - f) + gender * (108.844 - f)
    return VO2max


if __name__ == "__main__":
    gender = 1
    time_min = 10.8  # minutes
    weight_kg = 61.0
    HRmax = 184.
    HR = 0.9 * HRmax
    print('VO2max:', VO2max_Brigham_Young(weight_kg, time_min, HR, gender))
