# Import from a json file
import json
#Import from a csv
import csv
#Import our custom pump model
from pump import Pump
# Import the statistics packages 
import statistics
# Used for plotting
import matplotlib.pyplot as plt
# For the datetime conversion
from datetime import datetime
# Extended stats library
from scipy import stats

#input Values you can modify
YEARS = 20;

# Flowrates of the imported data don't change these values
flowrates = []
Hourly = [[] for Null in range(24)]
Length = [0] * 24
Average = [0] * 24
Deviation = [0] * 24
AverageTotal = 0
DeviationToatl = 0


def main():
    with open ('flowstudy.csv', newline='') as csvfile:
        flowreader = csv.reader(csvfile, delimiter=',')
        for row in flowreader:
            flowrates.append({"date": datetime.strptime(row[0], '%m/%d/%Y %H:%M'), "flowrate": float(row[1])})

    for d in flowrates:
        hour = d["date"].hour
        Hourly[hour].append(d["flowrate"])
        Length[hour] = Length[hour] + 1

    for i in range(24):
        Average[i] = statistics.mean(Hourly[i])
        Deviation[i] = statistics.stdev(Hourly[i])
        Hourly[i] = sorted(Hourly[i])

    # Years of predicted data
    predicted_data = []
    for i in range(YEARS * 365 * 24):
        predicted_data.extend(stats.norm.rvs(Average[i % 24], Deviation[i % 24], size=1))

    # Initalize two pumps
    A = Pump()
    B = Pump()
    hourly_data = []
    #with open ('pumps.json', 'r') as output: 
    #    json.read((A.__dict__, B.__dict__), output)

    for i in predicted_data:
        gpm = convert_to_gpm(i)
        temp_data = []
        temp_data.append(int(gpm))

        # This code checks the pumps max flowrate and splits the flow between the two pumps
        # and adds a small overhead. 
        if A.get_max() > gpm:
            temp_data.append(A.hours_cost(gpm))
            B.idle_wear()
        else:
            temp_data.append(A.hours_cost(gpm))
            temp_data.append(B.hours_cost(gpm))
        hourly_data.append(temp_data)

    # Print the final numbers
    with open ('output/data.csv', 'w') as output:
        writer = csv.writer(output, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for z in hourly_data:
            writer.writerow(z)

    with open ('output/average.csv', 'w') as output:
        writer = csv.writer(output, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(("Pump A Energy Total", int(A.total_energy_cost)))
        writer.writerow(("Pump A Repair Total", int(A.total_repair_cost)))
        writer.writerow(("Pump B Energy Total", int(B.total_energy_cost)))
        writer.writerow(("Pump B Repair Total", int(B.total_repair_cost)))
        writer.writerow(("Pump A Energy Yearly", int(A.total_energy_cost / YEARS)))
        writer.writerow(("Pump A Repair Yearly", int(A.total_repair_cost / YEARS)))
        writer.writerow(("Pump B Energy Yearly", int(B.total_energy_cost / YEARS)))
        writer.writerow(("Pump B Repair Yearly", int(B.total_repair_cost / YEARS)))

def convert_to_gpm(flowrate):
    return ((flowrate * 1000000) / 1440)

main()
