# THIS SCRIPT DOES NOT ESTIMATE TOU AND AFA

import numpy as np
import matplotlib.pyplot as plt

# --- Domestic Tariff Parameters --- #
ST_THRESHOLD = 600
HIGH_USAGE_THRESHOLD = 1500
RETAIL_CHARGE_AMOUNT = 10.0

# Rates (RM/kWh)
RATES = {
    "tier1": {"energy": 0.2703, "capacity": 0.0455, "network": 0.1285},
    "tier2": {"energy": 0.3703, "capacity": 0.0455, "network": 0.1285}
}

# Incentive tiers
INCENTIVE_TIERS = [
    (200, -0.25), (250, -0.245), (300, -0.225), (350, -0.21),
    (400, -0.17), (450, -0.145), (500, -0.12), (550, -0.105),
    (600, -0.09), (650, -0.075), (700, -0.055), (750, -0.045),
    (800, -0.04), (850, -0.025), (900, -0.01), (1000, -0.005),
    (1500, 0)
]

# Example fuel adjustment by month (fixed for this graph)
FUEL_RATE = -0.0145

def get_incentive(consumption):
    for max_kwh, rate in INCENTIVE_TIERS:
        if consumption <= max_kwh:
            return consumption * rate
    return 0

def calculate_bill(consumption):
    # Energy, capacity, network, fuel
    if consumption <= HIGH_USAGE_THRESHOLD:
        energy = consumption * RATES["tier1"]["energy"]
        capacity = consumption * RATES["tier1"]["capacity"]
        network = consumption * RATES["tier1"]["network"]
        fuel = consumption * FUEL_RATE if consumption > ST_THRESHOLD else 0
    else:
        energy = consumption * RATES["tier2"]["energy"]
        capacity = consumption * RATES["tier2"]["capacity"]
        network = consumption * RATES["tier2"]["network"]
        fuel = consumption * FUEL_RATE
    
    # Retail charge
    retail = RETAIL_CHARGE_AMOUNT if consumption > ST_THRESHOLD else 0
    
    # Incentive
    incentive = get_incentive(consumption)
    
    # Subtotal
    subtotal = energy + capacity + network + fuel + retail + incentive
    
    # Service Tax (applies only if >600 kWh)
    service_tax = 0
    if consumption > ST_THRESHOLD:
        service_tax = 0.08 * (energy + capacity + network + fuel + retail + incentive)
    
    # KWTBB (applies if >300 kWh)
    kwtbb = 0
    if consumption > 300:
        kwtbb = 0.016 * (energy + capacity + network + incentive)
    
    total = subtotal + service_tax + kwtbb
    return total

# Generate data
consumptions = np.arange(1, 2001, 10)
bills = np.array([calculate_bill(x) for x in consumptions])
unit_costs = bills / consumptions  # Effective RM/kWh

# Gradient (numerical derivative)
def gradient_at(x, h=1):
    return (calculate_bill(x+h) - calculate_bill(x-h)) / (2*h)

grad_1200 = gradient_at(1200)
grad_1665 = gradient_at(1665)

# Plot
fig, ax1 = plt.subplots(figsize=(10,6))

# Bill curve
ax1.plot(consumptions, bills, label="Bill (RM)", color="blue", linewidth=2)
ax1.set_xlabel("Consumption (kWh)")
ax1.set_ylabel("Bill (RM)", color="blue")
ax1.tick_params(axis="y", labelcolor="blue")

# Highlight thresholds
ax1.axvline(600, color="red", linestyle="--", alpha=0.6, label="ST Threshold (600 kWh)")
ax1.axvline(1500, color="purple", linestyle="--", alpha=0.6, label="High Usage (1500 kWh)")

# Effective cost curve (second y-axis)
ax2 = ax1.twinx()
ax2.plot(consumptions, unit_costs, label="Effective Cost (RM/kWh)", color="green", linewidth=2)
ax2.set_ylabel("Effective Cost (RM/kWh)", color="green")
ax2.tick_params(axis="y", labelcolor="green")

# Title & grid
plt.title("Electricity Bill vs Consumption (Domestic Tariff)")
ax1.grid(True, linestyle="--", alpha=0.5)

# Legends
fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.9))

plt.tight_layout()
plt.show()

grad_1200, grad_1665
