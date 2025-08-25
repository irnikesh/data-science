# Description

Survival / Time-to-Event Modeling

Question: When will an event E for date A will occur.
Example: When (t) will the hotel for date A become fully booked?
If it is possible to fix N and t, Binary classification with Logistic regression, Random Forest, XGBoost will do. 
However, if N is not fixed, then model the distribution of time until full occupancy.

Target (T):
	•	Time (days) from snapshot date t until hotel for date A reaches 100% occupancy.
	•	If hotel never reached full before A, the data is censored (i.e., we know it wasn’t full by A, but don’t know if it could’ve been later).