 select printf('$%.2f',round(sum(pid_output)/2/60/60*12*.10,2)) from firing where run_id>44;
