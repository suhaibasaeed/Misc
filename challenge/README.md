# Suhaib Saeed Network Automation Interview Exercise
## Summary
I thought these exercises were of medium difficulty, my preference for python over Ansible meant I definitely enjoyed the first one more. I spent around 7 hours of the 72 on these exercises due to work commitments on the weekend. 
## Python Exercise
### Comments, thoughts and reflections
After confirming this was allowed with Nicky I decided to use the Nornir python framework to complete this exercise. One of the main reasons was as it abstracted a lot of the complexity away that we would usually have to deal with when using libraries directly. It also meant I could have an inventory similar to Ansible plus concurrency meant execution time was very fast. I would have preferred to load the external data into the hosts.yaml file but the requirements specificed this had to be an external YAML file so I did this using the load_yaml nornir plugin.  

I had 2 files, one with verification checks which are imported into the main file. I created Nornir custom tasks for each process in the exercises. E.g. reading the yaml file in, rendered the jinja2 template and verification etc. I then ran the tasks one by one in the main function of the python file. Pylint and black were used for linting. User logging was acheived via Nornir's print_result function.  

#### Improvements
If I had more time to spend on the exercise I could've done the following:  
- Cleaned up the main function, potentially adding a loop in there
- As mentioned I think it would have been better to put the external data in the hosts.yaml file
- Make the code more modular
- Clean up some of the print_result output by doing my own logging

## Ansible Exercise
### Comments, thoughts and reflections
My Ansible setup was a standard one where all of my data went into the host_vars directory. If I had more things similar between the devices these would've went into the group_vars directory e.g. if the peers were all iBGP thus had the same ASN.  

My files were split up into a main playbook with majority of the tasks in here with another .yml file with some verification tasks for modularity. I also added tags in so that we can just run the verification tasks without running the entire playbook again via the --tags argument. I also used the assert module to verify the 2 peers were present otherwise it failed the playbook execution. The device password was taken from the user via vars_prompt. Yamllint was used for error checking.  

I personally had not used napalm verify before so big shout out to NTC's very own Przemek Rogala for the great blog post on this.  

#### Improvements
If I had more time to spend on the exercise I could've done the following:  
- Implement Ansible vaults for secrets. another option would've been using the --ask-pass arg
- Use NETCONF instead of SSH for more reliable and deterministic automation.
- Split out BGP and interfaces from a single file in host_vars into mutiple files. i.e. a file for bgp and one for interfaces
- Added more modularity into the playbook
- Write tests
- Use Ansible resource modules for more idempotency