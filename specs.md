# PURPOSE

Election polls published by media outlets typically present results as absolute figures—for example: Party A is projected at 34 seats, Party B at 28, and Party C at 11.

The objective of this project is to move beyond static projections. Given a specific election poll, this project will calculate a probability distribution for each party (the likelihood of winning 0, 1, 2, ..., 120 seats) and establish a 90% confidence interval for their final seat count.

# SPECIFICATION

## DATA SOURCE

1. All project data is consolidated within the `/data` folder.
2. There is a subfolder for each election cycle, e.g. `/data/25th-Knesset-2022`.
3. Each election cycle subfolder includes:
	* `parties.json` - Mapping from party symbols to party names, and the list of surplus agreements. Parties are uniquely identified by their Hebrew symbols (1–4 letters).
	* `/polls` - A subfolder including the raw data of each poll. Poll results are stored as decimal fractions of total respondents rather than seat counts (e.g., 0.283 for "מחל", which means 28.3% of the respondents will vote for this party).

## LOGIC

1. Seat Allocation: The distribution of seats among parties will be calculated using the Bader-Ofer method, as detailed in the next section.
2. For each poll, use Monte Carlo simulations to calculate a probability distribution for each party, and establish a 90% confidence interval for their final seat count.
3. Parameters for Monte Carlo simulations:
	* Distribution: Dirichlet
	* Concentration parameter: α_i ​= P_i ​× N, where P_i​ is the party fraction and N is the sample size.
	* Iterations: 100,000
	* Seed: fixed default seed for reproducibility
4. Store the results in the `/output` folder that mirrors the `/data` folder structure (subfolder for each election cycle, each one containing a subfolder for each poll). Each poll subfolder should include the following files:
	* `stats.json` - The high-level stats of each party in the poll: average seat count, probability to pass the electoral threshold, and upper and lower bounds of the 90% confidence interval.
	* `seat_counts.csv` - The frequency matrix with the following structure:
	`PartySymbol,0_seats,1_seat,2_seats,3_seats,...,120_seats`
	Each row is a party and each column is a possible seat count (0–120).
5. By default, run simulations for new polls only (added to the `/polls` folder but no corresponding subfolder in the `/output` folder). However, let the user run simulations for a specific poll. If it already has a corresponding subfolder in the `/output` folder, override it.

## Seat Distribution According to the Bader-Ofer Method

### Constants:

* Number of seats for distribution: 120
* Electoral threshold: 3.25%

### Input:

* The competing parties and the number of valid votes each received.
* Pairs of parties that entered into surplus agreements.

### Output:

* A list of parties and the number of seats each received (including parties that did not pass the electoral threshold).

### Distribution of Seats:

1. Calculate the minimum number of votes required to participate in the seat distribution: Total valid votes multiplied by the electoral threshold.
2. Parties that received fewer than the minimum number of votes do not participate in the distribution (each receives 0 seats).
3. Calculate the total valid votes of only the parties participating in the distribution.
4. Calculate the "Quota": Divide the total valid votes of the participating parties (from step 3) by the number of seats for distribution (120). The integer part of the quotient is the Quota.
5. For each participating party: Divide its number of valid votes by the Quota. The integer part of the quotient is the initial number of seats the party receives.
6. If there are unassigned seats (i.e., if the total seats distributed in step 5 is less than 120):
	1. Review the pairs of parties with surplus agreements. If one party in a pair failed to pass the electoral threshold (per step 2), the agreement is voided.
	2. Treat each valid pair as a single entity whose votes are the sum of both parties, and whose current seats are the sum of seats already assigned to both.
	3. For each entity (party or pair), divide its total valid votes by (its current seats + 1). This result is the "Entity Quota."
	4. The entity with the highest Entity Quota receives one additional seat. In case of a tie, randomly select one of the tied entities. Update its Entity Quota accordingly. Repeat this process until all remaining seats are distributed.
7. Internal apportionment of surplus seats: For each pair of parties with a valid surplus agreement, repeat steps 3–6 above, with the following changes:
	* Only the two parties in the pair participate.
	* The number of seats for distribution is the combined sum of seats they received together (instead of 120).
	* There are no surplus agreements to consider.
