# [Operations Simulator](https://regressionsimulator.herokuapp.com/)

##### About this Simulator:
This simulator was built to provide an interactive platform for running simulations on 
different staffing and scheduling scenarios. The simulator lets you input the following parameters:

- __Number of Agents:__ Enter the number of agents staffed. Current assumption is that all these agents
are staffed 24x7. This is not practical, however, it is equivalent to having a flat staff throughout the day.
A more efficient system will call for different schedules assigned to different agents to meet the changing workload demand.
This scenario will be built in future versions, but can be easily integrated in this simulator.
- __Peak Call Count:__ Lets you enter the maximum expected number of calls in an half-hour interval. Using this input, 
a call distribution is built for the entire day, assuming linear increase in the average number of calls to the peak value and then
a linear decrease in average calls. Once the average call distribution is built, actual call counts are calculated based on a random draw
from a poisson distribution assuming the average calls for that interval is based on the distribution previously generated.
- __Average Handling Time (Lower and Upper bounds):__ The average handling time or AHT includes the total time spent by agents on a call and two inputs
are taken from the user - minimum and maximum AHT expected throughout the day. Using these lower and upper bounds a random draw allows the simulator
to assign a call aht to each call in every interval. 

Once the above inputs are available, calls are generated with AHT assigned to each. These calls are then allocated to agents. Agent allocation is usually
random for agents in idle status, but if no agents are available in an interval, then the call is assigned to the agent who is available at the earliest 
to reduce the call wait time. This assignment is based on a first-in first-out assignment where the calls are sequentially queued and the first call to arrive 
will be handled first. 


![](*.gif)


