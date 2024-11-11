import os
import subprocess
from codecarbon import EmissionsTracker

# Given a file path measure emissions in kg CO2 eq
def measure_emissions_g_co2_eq(test_file_path):
    tracker = EmissionsTracker(save_to_file=False)
    emissions_kg_CO2eq = None
    
    try:
        tracker.start()
        print(f"Running test: {test_file_path}")
        
        # Run the test file using unittest with subprocess
        result = subprocess.run(
            ["python", "-m", "unittest", test_file_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Test executed successfully.")
        else:
            print("Test execution failed.")
            print(f"Output: {result.stderr}")
        
    except Exception as e:
        print(f"An error occurred while running the test: {e}")
    
    finally:
        emissions_kg_CO2eq = tracker.stop()
    
    # Print the emissions data if available
    if emissions_kg_CO2eq is not None:
        # Emissions as CO₂-equivalents [CO₂eq], in kg
        print("CO2 g eq emissions: ")
        print(emissions_kg_CO2eq*1000)
        # print(f"Carbon Emissions for {os.path.basename(test_file_path)}: {emissions_data['emissions']:.6f} kg CO2eq")
    else:
        print("No emissions data collected.")
        
    return emissions_kg_CO2eq*1000 # in grams

# file_path = "./test.py"
# measure_emissions_kg_co2_eq(file_path)