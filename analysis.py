#!/bin/python3
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.markers import MarkerStyle

def main():
    truth_altitude = []
    truth_temperature = []
    truth_pressure = []
    truth_density = []

    with open('isa_exponents_fixed.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            truth_altitude.append(float(row['geometric_altitude']))
            truth_temperature.append(float(row['temperature_kelvin']))
            truth_pressure.append(float(row['pressure'])*100)
            truth_density.append(float(row['density']))

    altitude = []
    temperature = []
    pressure = []
    density = []

    with open('output_file.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            altitude.append(float(row['altitude']))
            temperature.append(float(row['temperature']))
            pressure.append(float(row['pressure']))
            density.append(float(row['density']))
    
    ylabel_altitudes = altitude.copy()
    ylabel_altitudes.append(85000.0)
    ylabel_ticks = np.arange(altitude[0], ylabel_altitudes[len(ylabel_altitudes)-1], step=5000.0)

    temperature_calc_style = MarkerStyle(marker="o", fillstyle='none')
    pressure_calc_style = MarkerStyle(marker="o", fillstyle='none')
    density_calc_style = MarkerStyle(marker="o", fillstyle='none')

    fig, axs = plt.subplots(layout="constrained")
    axs1 = axs.twiny()
    axs2 = axs.twiny()

    axs.scatter(temperature, altitude, label='Calculated Temperature', marker=temperature_calc_style, color="tab:red",s=12)
    axs.scatter(truth_temperature, truth_altitude, marker='.', label='Truth Temperature', color="tab:red", s=10)
    axs.set_xlabel("Temperature [K]", fontsize=8)
    axs.set_ylabel("Altitude [m]")
    axs.tick_params(axis='x', labelsize=8)
    axs.tick_params(axis='y', labelsize=8)
    axs.set_yticks(ylabel_ticks)

    axs1.scatter(pressure, altitude, label='Calculated Pressure', marker=pressure_calc_style, color="tab:green",s=12)
    axs1.scatter(truth_pressure, truth_altitude, marker='.', label='Truth Pressure', color="tab:green",s=10)
    axs1.set_xlabel("Pressure [Pa]", fontsize=8)
    axs1.tick_params(axis='x', labelsize=8)
    axs2.scatter(density, altitude, label='Calculated Density', marker=density_calc_style, color="tab:orange",s=12)
    axs2.scatter(truth_density, truth_altitude, marker='.', label='Truth Density', color="tab:orange",s=10)
    axs2.set_xlabel("Density [kg/m^3]", fontsize=8)
    axs2.tick_params(axis='x', labelsize=8)

    axs1.xaxis.set_label_position("bottom")
    axs1.xaxis.set_ticks_position("bottom")
    axs1.spines["bottom"].set_position(("axes", -0.05))
    axs2.xaxis.set_ticks_position("bottom")
    axs2.xaxis.set_label_position("bottom")
    axs2.spines["bottom"].set_position(("axes", -0.1))

    lines_labels = [ax.get_legend_handles_labels() for ax in fig.axes]
    lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
    fig.legend(lines, labels)

    plt.show()
    fig.savefig('ISA_Analysis.png', dpi=500)

if __name__ == '__main__':
    main()