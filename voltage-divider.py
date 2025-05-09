import configparser
import itertools
from math import isclose

def read_resistors(file_path):
    """Read resistor values from resistors.ini file in kilo-ohms."""
    config = configparser.ConfigParser()
    config.read(file_path)
    try:
        resistors = [float(x) for x in config['Resistors']['values'].split(',')]
        return resistors
    except KeyError:
        print("Error: Ensure resistors.ini has a [Resistors] section with 'values' key.")
        return []

def calculate_vout(vin, r1, r2):
    """Calculate output voltage of a voltage divider."""
    return vin * (r2 / (r1 + r2))

def calculate_current(vin, r1, r2):
    """Calculate current through the voltage divider in mA (R1, R2 in kΩ)."""
    return (vin / (r1 + r2)) * 1000  # Convert to mA (V/kΩ = mA)

def calculate_power(vin, current):
    """Calculate power consumption in mW."""
    return vin * current / 1000  # Convert current from mA to A for mW

def calculate_required_resistor(vin, vout_desired, known_r, imax, is_r1=True):
    """Calculate the resistor needed to pair with a known resistor for exact Vout within imax."""
    if isclose(vout_desired, 0) or isclose(vout_desired, vin):
        return None  # Impossible to achieve exactly 0V or Vin with finite resistors
    if is_r1:
        # R1 is known, solve for R2: Vout = Vin * R2/(R1 + R2)
        r2 = known_r * vout_desired / (vin - vout_desired)
    else:
        # R2 is known, solve for R1: Vout = Vin * R2/(R1 + R2)
        r1 = known_r * (vin - vout_desired) / vout_desired
        r2 = known_r
    # Check if the combination respects imax
    total_r = known_r + r2 if is_r1 else r1 + known_r
    current = calculate_current(vin, known_r, r2) if is_r1 else calculate_current(vin, r1, known_r)
    if current > imax:
        return None
    return r2 if is_r1 else r1

def find_best_resistors(vin, vout_desired, resistors, imax):
    """Find the best R1 and R2 combination from available resistors within imax."""
    if vin > 3.3:
        print("Warning: Input voltage exceeds 3.3V, which is unsafe for ESP32-C3 ADC.")
    
    best_r1, best_r2 = None, None
    best_vout = None
    best_current = None
    min_error = float('inf')
    achievable_voltages = []
    
    # Try all combinations of resistors for R1 and R2
    for r1, r2 in itertools.product(resistors, repeat=2):
        vout = calculate_vout(vin, r1, r2)
        current = calculate_current(vin, r1, r2)
        if current > imax:
            continue  # Skip combinations exceeding imax
        error = abs(vout - vout_desired)
        achievable_voltages.append((vout, r1, r2, error, current))
        
        # Update if this combination gives a closer output voltage
        if error < min_error or (isclose(error, min_error, rel_tol=1e-9) and (r1 + r2) < (best_r1 + best_r2 if best_r1 and best_r2 else float('inf'))):
            min_error = error
            best_r1, best_r2 = r1, r2
            best_vout = vout
            best_current = current
    
    return best_r1, best_r2, best_vout, best_current, achievable_voltages

def suggest_resistors(vin, vout_desired, resistors, imax):
    """Suggest resistors to pair with existing ones for exact Vout within imax."""
    suggestions = []
    for r in resistors:
        # Case 1: Known R1, find R2
        r2 = calculate_required_resistor(vin, vout_desired, r, imax, is_r1=True)
        if r2 and r2 > 0:
            suggestions.append((r, r2, "R1", "R2"))
        # Case 2: Known R2, find R1
        r1 = calculate_required_resistor(vin, vout_desired, r, imax, is_r1=False)
        if r1 and r1 > 0:
            suggestions.append((r1, r, "R1", "R2"))
    return suggestions

def main():
    # Get user input
    try:
        vin = float(input("Enter input voltage (V): "))
        vout_desired = float(input("Enter desired output voltage (V): "))
        imax = float(input("Enter maximum allowed current (mA): "))
    except ValueError:
        print("Error: Please enter valid numerical values for voltages and current.")
        return
    
    if vout_desired > vin:
        print("Error: Desired output voltage cannot be greater than input voltage.")
        return
    if vout_desired < 0:
        print("Error: Desired output voltage cannot be negative.")
        return
    if imax <= 0:
        print("Error: Maximum current must be positive.")
        return
    
    # Read resistors from file
    resistors = read_resistors('resistors.ini')
    if not resistors:
        print("Error: No valid resistors found in resistors.ini.")
        return
    
    # Find best resistor combination and achievable voltages
    r1, r2, vout, current, achievable_voltages = find_best_resistors(vin, vout_desired, resistors, imax)
    
    # Output best combination
    print("\n=== Best Resistor Combination ===")
    if r1 is None or r2 is None:
        print("No suitable resistor combination found within the current limit.")
    else:
        print(f"R1: {r1} kΩ")
        print(f"R2: {r2} kΩ")
        print(f"Actual output voltage: {vout:.3f} V")
        print(f"Error from desired voltage: {abs(vout - vout_desired):.3f} V")
        print(f"Current consumption: {current:.3f} mA")
        print(f"Power consumption: {calculate_power(vin, current):.3f} mW")
    
    # Suggest resistors to achieve exact Vout
    print("\n=== Suggested Resistors for Exact Output ===")
    suggestions = suggest_resistors(vin, vout_desired, resistors, imax)
    if not suggestions:
        print("No valid resistor suggestions within the current limit.")
    else:
        for r1_val, r2_val, r1_label, r2_label in suggestions:
            current_suggestion = calculate_current(vin, r1_val, r2_val) if r1_label == "R1" else calculate_current(vin, r1_val, r2_val)
            print(f"Use {r1_label} = {r1_val:.3f} kΩ with {r2_label} = {r2_val:.3f} kΩ "
                  f"(you have {r2_val if r2_label == 'R2' else r1_val} kΩ, current: {current_suggestion:.3f} mA)")
    
    # List achievable voltages
    print("\n=== Achievable Output Voltages with Current Resistors ===")
    # Filter voltages <= vout_desired and sort in descending order
    filtered_voltages = [v for v in achievable_voltages if v[0] <= vout_desired]
    filtered_voltages.sort(key=lambda x: (-x[0], x[1] + x[2]))
    for vout, r1, r2, _, current in filtered_voltages[:15]:  # Show top 15
        print(f"Vout: {vout:.3f} V (R1: {r1} kΩ, R2: {r2} kΩ, Current: {current:.3f} mA)")
    if len(filtered_voltages) > 15:
        print(f"... and {len(filtered_voltages) - 15} more combinations.")
    elif len(filtered_voltages) == 0:
        print("No achievable voltages less than or equal to the desired output voltage within the current limit.")

if __name__ == "__main__":
    main()
