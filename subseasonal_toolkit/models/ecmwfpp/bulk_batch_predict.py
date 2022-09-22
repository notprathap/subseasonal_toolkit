# Generates predictions for each of the ECMWF parameter configurations
# used by the tuner
#
# Example usage:
#   python -m subseasonal_toolkit.models.ecmwfpp.bulk_batch_predict contest_tmp2m 34w -t std_contest
#       
# Positional args:
#   gt_id: contest_tmp2m, contest_precip, us_tmp2m, or us_precip
#   horizon: 34w or 56w
#
# Named args:
#   --target_dates (-t): target dates for batch prediction
#   --cmd_prefix (-c): prefix of command used to execute batch_predict.py
#     (default: "python"); e.g., "python" to run locally,
#     "src/batch/batch_python.sh --memory 12 --cores 16 --hours 1" to
#     submit to batch queue
import os
import subprocess
from argparse import ArgumentParser
from subseasonal_toolkit.utils.general_util import printf

model_name = "ecmwfpp"

# Parse command-line arguments
parser = ArgumentParser()
parser.add_argument("pos_vars",nargs="*")  # gt_id and target_horizon
parser.add_argument('--target_dates', '-t', default="std_paper_eval")
parser.add_argument('--cmd_prefix', '-c', default="python")
parser.add_argument('--skip_existing', '-se', default=False, action='store_true', 
                    help="skip running submodels for which metrics exist")

args = parser.parse_args()
gt_id = args.pos_vars[0]
horizon = args.pos_vars[1]
target_dates = args.target_dates
cmd_prefix = args.cmd_prefix
skip_existing = args.skip_existing


# Specify list of parameter settings to run
train_years = 20
# Specify list of parameter settings to run
first_day = 1
intercept = True
last_days = [1, 7, 14, 28, 42]
margins = [0, 14, 28, 35]
# Specify parallel arrays of first and last leads
if horizon == "56w":
    first_leads = [29]
    last_leads = [29]
elif horizon == "34w":
    first_leads = [29, 0, 15, 15]
    last_leads = [29, 29, 22, 15]
elif horizon == "12w":
    # No tuning for 12w lead
    first_leads = [1]
    last_leads = [1]
else:
    raise ValueError(f"invalid horizon {horizon}")
forecast_with = ["p+c"]
debias_with = ["p+c"]

    
module_str = f"-m subseasonal_toolkit.models.{model_name}.batch_predict"
# Include quotes for batch invocation
module_str = f"\"{module_str}\""
task_str = f"{gt_id} {horizon} -t {target_dates}"
# Iterate over parallel leads arrays
for ii in range(len(first_leads)):
    first_lead = first_leads[ii]
    last_lead = last_leads[ii]
    for last_day in last_days:
        for margin in margins:    
            for fw in forecast_with:
                for dw in debias_with:
                    # Run batch predict for this configuration
                    param_str=f"-y {train_years} -i {intercept} -m {margin} -i {intercept} -fd {first_day} -ld {last_day} -fl {first_lead} -ll {last_lead} -fw {fw} -dw {dw}"
                    cmd=f"{cmd_prefix} {module_str} {task_str} {param_str}"
                    submodel_name = f"ecmwfpp-debias{intercept}_years{train_years}_margin{margin}_days{first_day}-{last_day}_leads{first_lead}-{last_lead}_lossmse_forecast{fw}_debias{dw}"
                    filename = f"eval/metrics/{model_name}/submodel_forecasts/{submodel_name}/{gt_id}_{horizon}/rmse-{gt_id}_{horizon}-{target_dates}.h5"
                    if os.path.isfile(filename) and skip_existing:
                        print(f"\nmetrics file exists for {submodel_name}")
                    else:
                        printf(f"\nRunning {cmd}")
                        subprocess.call(cmd, shell=True)
            

            

            
            
            
            
            
            
