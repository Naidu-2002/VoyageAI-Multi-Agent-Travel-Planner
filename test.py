from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights




res = search_flights("plan a trip from DFW to LAX on July 15th, returning on July 20th for 2 adults and 1 child, with a budget of $500 per person. Include flight times, airlines, and prices.")
print(res)