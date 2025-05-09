# ESP32-C3 Voltage Divider Calculator

## About

Originally, this application was developed to design a voltage divider for an ESP32 project, but it can be used for any voltage divider circuit using the resistors you have available.

## Overview

This Python application helps design voltage dividers for the ESP32-C3 microcontroller by calculating the best resistor pairs from a user-defined list to achieve a desired output voltage, ensuring compatibility with the ESP32-C3's ADC (max 3.3V). It also suggests resistors to purchase for exact voltage outputs and lists achievable voltages with available resistors.

## Features

- **Input Validation**: Accepts user input for input voltage (Vin) and desired output voltage (Vout), ensuring Vout ≤ Vin and Vout ≥ 0.
- **ESP32-C3 Safety**: Warns if Vin exceeds 3.3V, protecting the ESP32-C3 ADC.
- **Resistor List**: Reads resistor values (in kΩ) from a `resistors.ini` file, allowing easy updates to available resistors.
- **Best Resistor Pair**: Finds the R1, R2 combination from available resistors that produces the output voltage closest to the desired Vout, minimizing total resistance for efficiency.
- **Suggested Resistors**: Calculates resistor values to pair with existing resistors for the exact desired Vout, helping identify what to buy.
- **Achievable Voltages**: Lists up to 15 achievable output voltages (≤ desired Vout) in descending order, helping users evaluate alternatives.
- **Error Handling**: Manages invalid inputs, missing files, or unachievable voltages gracefully.

## Requirements

- Python 3.x
- A `resistors.ini` file in the project directory with resistor values in kΩ (example provided below).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/esp32-c3-voltage-divider.git
   ```
2. Navigate to the project directory:
   ```bash
   cd esp32-c3-voltage-divider
   ```
3. Ensure `resistors.ini` is in the project directory (see example below).

## Usage

1. Create or edit `resistors.ini` with your resistor values (in kΩ):
   ```ini
   [Resistors]
   values = 470, 0.220, 1, 2.2, 5.6
   ```
2. Run the script:
   ```bash
   python voltage_divider.py
   ```
3. Enter the input voltage (Vin) and desired output voltage (Vout) when prompted.
4. Review the output, which includes:
   - The best R1, R2 pair and actual Vout.
   - Suggested resistors to achieve the exact Vout.
   - Up to 15 achievable voltages (≤ Vout) with current resistors.

### Example Output
```
Enter input voltage (V): 5
Warning: Input voltage exceeds 3.3V, which is unsafe for ESP32-C3 ADC.
Enter desired output voltage (V): 3

=== Best Resistor Combination ===
R1: 2.2 kΩ
R2: 5.6 kΩ
Actual output voltage: 3.026 V
Error from desired voltage: 0.026 V

=== Suggested Resistors for Exact Output ===
Use R1 = 2.000 kΩ with R2 = 470.000 kΩ (you have 470 kΩ)
...

=== Achievable Output Voltages with Current Resistors ===
Vout: 2.941 V (R1: 5.6 kΩ, R2: 2.2 kΩ)
Vout: 2.941 V (R1: 5.6 kΩ, R2: 470 kΩ)
...
```

## Project Structure

- `voltage_divider.py`: Main Python script for calculations.
- `resistors.ini`: Configuration file listing available resistor values in kΩ.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for bugs, features, or improvements.

## License

This project is licensed under the MIT License.
