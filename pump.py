class Pump:
    def __init__(self):
        # GPM vs killowatts used for that hour
        efficient_gpm = 1200
        self.gpm_vs_kwh = [(1000, 120),
                           (2000, 125),
                           (3000, 140),
                           (4000, 160),
                           (5400, 170),
                           (6000, 190),
                           (7400, 210),
                           (8000, 250)]
        self.gpm_max = 8000
        self.gpm_min = 0

        # Wear Starting Values
        self.bearing_wear_initial = 20000
        self.impeller_wear_initial = 40000 
        self.cavitation_chance_initial = 0

        # Wear Totals
        self.bearing_wear_totals = 20000
        self.impeller_wear_totals = 40000
        self.seal_wear_totals = 40000

        # Wear Rates
        self.bearing_wear = 1
        self.impeller_wear = 1
        self.seal_wear = 1

        # Costs
        self.bearing_replacment_cost = 1000
        self.impeller_dip_cost = 7000
        self.seal_replacment_cost = 15000
        self.kwh_cost = 0.1

        # Running Totals 
        self.total_repair_cost = 0.0
        self.total_energy_cost = 0.0

    # The cost of the pump in a given hour
    def hours_cost(self, flowrate):

        # Lets find the energy cost
        energy_cost = self.kwh_cost * self.find_kwh(flowrate)
        # Lets find the repair cost during this hour
        repair_cost = self.repair_cost(flowrate)

        # Lets add these number to our total. Giving us a running total of repair and energy cost
        self.total_repair_cost = self.total_repair_cost + repair_cost
        self.total_energy_cost = self.total_energy_cost + energy_cost

        # Return the total repair and energy cost for this hour
        return (energy_cost, repair_cost)

    def repair_cost(self, flowrate):
        # Find the wear of the bearing, impellers, and seals
        self.wear(flowrate);
        repair_cost = 0;

        # Check if any of the parts are at failure, If so lets replace them and charge the cost for 
        # replacments
        if (self.bearing_wear_totals < 0):
            self.bearing_wear_totals = self.bearing_wear_totals + self.bearing_wear_initial
            repair_cost = repair_cost + self.bearing_replacment_cost
        if (self.impeller_wear_totals < 0):
            self.impeller_wear_totals = self.impeller_wear_totals + self.impeller_wear_initial
            repair_cost = repair_cost + self.impeller_dip_cost

        return repair_cost

    def get_max(self):
        return self.gpm_max

    def idle_wear(self):
        self.bearing_wear_totals = self.bearing_wear_totals - (self.bearing_wear * .5)
        self.impeller_wear_totals = self.impeller_wear_totals - (self.impeller_wear * .5)
        self.seal_wear_totals = self.seal_wear_totals - (self.seal_wear * .5)

    def wear(self, flowrate):
        # Here we will calculate the actual wear on the different parts
        hourly_bearing_wear = 0
        hourly_impeller_wear = 0
        hourly_seals_wear = 0

        # For higher flowrates the wear on the bearings and impellers are greater than if they are
        # lower. If they are in the typical design parameters they are 1
        if((flowrate - self.gpm_min) / (self.gpm_max - self.gpm_min) > .9):
            hourly_bearing_wear = self.bearing_wear * 1.2
            hourly_impeller_wear = self.impeller_wear * 1.2

        if((flowrate - self.gpm_min) / (self.gpm_max - self.gpm_min) < .7):
            hourly_bearing_wear = self.bearing_wear * .8
            hourly_impeller_wear = self.impeller_wear * .8
        else:
            hourly_bearing_wear = self.bearing_wear
            hourly_impeller_wear = self.impeller_wear

        # Take the wear off of the life of the part
        self.bearing_wear_totals = self.bearing_wear_totals - hourly_bearing_wear
        self.impeller_wear_totals = self.impeller_wear_totals - hourly_impeller_wear
        self.seal_wear_totals = self.seal_wear_totals - self.seal_wear

    def find_kwh(self, flowrate):
        # For the flow rate interpolate between the closets points and make the kwatts used that number
        v = 0
        if flowrate > self.gpm_max:
            1000

        # Go through the points and find the proper points to interpolate on
        for x in self.gpm_vs_kwh:
            v = v + 1
            if x[0] > flowrate:
                break
            if v + 1 > len(self.gpm_vs_kwh) - 1:
                break
        return self.linear_interpolation(self.gpm_vs_kwh[v-1], self.gpm_vs_kwh[v], flowrate)

    def linear_interpolation(self, tupleOne, tupleTwo, expected_value):
        # Interpolate between two values
        return tupleOne[1] + (expected_value - tupleOne[0]) * ((tupleTwo[1] - tupleOne[1])/(tupleTwo[0] - tupleOne[0]))
