# Black-Scholes Options Pricer

**Author:** Berra Vatansever | **Built:** June 2026

A full implementation of the Black-Scholes options pricing model in Python — with all five Greeks, live market data via `yfinance`, intelligent strike suggestion based on expected move, and automated payoff visualisation.

---

## What This Does

Given any stock ticker, this tool:

1. **Pulls live price and computes historical volatility** from 1 year of daily returns
2. **Suggests realistic strike prices** based on the 1 and 2 standard deviation expected move
3. **Prices call and put options** at each suggested strike using Black-Scholes
4. **Computes all five Greeks** — Delta, Gamma, Vega, Theta, Rho
5. **Generates and saves a price curve plot** showing call and put prices across a range of stock prices

---

## The Model

### Black-Scholes Formula

The Black-Scholes model prices a European option under the assumption that the underlying asset follows Geometric Brownian Motion with constant drift and volatility.

**Step 1 — Compute d1 and d2:**

```
d1 = [ln(S/K) + (r + σ²/2) × T] / [σ × √T]
d2 = d1 - σ × √T
```

**Step 2 — Price the call and put:**

```
Call = S × N(d1) - K × e^(-rT) × N(d2)
Put  = K × e^(-rT) × N(-d2) - S × N(-d1)
```

Where `N()` is the cumulative standard normal distribution (`scipy.stats.norm.cdf`).

**Put-Call Parity** is used to derive the put price from the call, ensuring no arbitrage between the two.

---

## The Greeks

| Greek | Formula | What It Measures |
|-------|---------|-----------------|
| **Delta** | N(d1) for call / N(d1)-1 for put | Sensitivity of option price to $1 move in stock price |
| **Gamma** | N'(d1) / (S × σ × √T) | Rate of change of Delta — convexity of the option |
| **Vega** | S × N'(d1) × √T | Sensitivity to a 1% change in volatility |
| **Theta** | -(S × N'(d1) × σ) / (2√T) ± r × K × e^(-rT) × N(±d2) | Time decay — value lost per day as expiry approaches |
| **Rho** | K × T × e^(-rT) × N(d2) for call | Sensitivity to a 1% change in the risk-free rate |

---

## Strike Suggestion Engine

Rather than requiring the user to input a strike manually, the tool computes the **expected move** of the stock over the option's lifetime using:

```
Expected move = S × σ × √T
```

This is the 1 standard deviation range the stock is expected to stay within, derived from the same GBM framework underlying Black-Scholes. Five strikes are then automatically generated:

| Strike | Description |
|--------|-------------|
| ATM | At the money — current stock price |
| 1SD_up | 1 standard deviation above current price |
| 1SD_down | 1 standard deviation below current price |
| 2SD_up | 2 standard deviations above — tail scenario |
| 2SD_down | 2 standard deviations below — tail scenario |

---

## Example Output

Running with `NVDA`, `T=0.5yr`, `r=0.05`:

```
Ticker: NVDA
Current Price: $131.38
Historical Volatility: 0.5823 (58.23%)

Expected move over 6 months: ±$54.02

Suggested strikes:
  ATM:       $131
  1SD_up:    $185
  1SD_down:  $77
  2SD_up:    $239
  2SD_down:  $23

Black-Scholes prices for NVDA:
Strike        Call        Put      Delta
ATM    $131   $30.41    $29.47    0.5232
1SD_up $185    $9.42    $57.52    0.2301
...
```

---

## Installation

```bash
git clone https://github.com/berravatansever2-lgtm/black-scholes-pricer.git
cd black-scholes-pricer
pip install -r requirements.txt
```

## Usage

```bash
python black_scholes.py
```

To change the stock, expiry, or rate — edit these lines at the bottom of the file:

```python
ticker = "NVDA"   # any valid ticker
T = 0.5           # time to expiry in years
r = 0.05          # risk-free rate (US 3-month T-bill)
S_range = 0.5     # plot range — 50% above and below strike
n_points = 100    # smoothness of the plot curve
```

---

## Dependencies

| Library | Purpose |
|---------|---------|
| `numpy` | Vectorised computation |
| `scipy` | Normal distribution functions (norm.cdf, norm.pdf) |
| `yfinance` | Live stock price and historical data |
| `matplotlib` | Option price curve visualisation |

Install all:

```bash
pip install numpy scipy yfinance matplotlib
```

---

## Key Concepts Implemented

**Why log returns for volatility?** Log returns are time-additive and symmetric — simple returns compound asymmetrically across periods. Historical volatility is computed as the annualised standard deviation of daily log returns: `σ = std(log_returns) × √252`.

**Why √T for expected move?** Volatility scales with the square root of time (a property of random walks). A stock with 20% annual volatility has an expected daily move of `20% / √252 ≈ 1.26%`.

**Why Put-Call Parity?** Under no-arbitrage, the relationship `C - P = S - K×e^(-rT)` must hold. If it breaks, a riskless profit is available by simultaneously buying the cheap side and selling the expensive side. The put price in this implementation is derived from parity rather than computed independently.

---

## Limitations

- **European options only** — Black-Scholes does not price American options (which can be exercised early). American options require binomial trees or finite difference methods.
- **Constant volatility assumption** — Real markets exhibit volatility smiles and skews. The implied volatility of options varies by strike and expiry in ways Black-Scholes cannot capture.
- **No dividends** — The standard model assumes no dividend payments. A dividend-adjusted version would modify d1 to account for the continuous dividend yield.
- **Fat tails** — GBM assumes normally distributed returns. Real returns have fatter tails — extreme moves occur more frequently than the model predicts.

---

## Next Steps

- [ ] Implied volatility solver — invert Black-Scholes to find the market's implied σ from observed option prices
- [ ] Volatility smile visualisation — plot implied vol across strikes
- [ ] American option pricing via binomial tree
- [ ] Options strategy payoff diagrams — straddle, strangle, bull spread, iron condor

---

## Related Projects

- [Two-Player Stock Market Simulation](https://github.com/berravatansever2-lgtm/two_player_stock_market_simulatio) — Game-theoretic model of investor-market interaction using GBM and Monte Carlo

---

## Author

**Berra Vatansever** — Incoming Columbia University IEOR undergraduate (Class of 2030), CP Davis Scholar. Building toward quantitative research roles at systematic trading firms.

Research interests: market microstructure, game theory in financial markets, stochastic models, options pricing.

[GitHub](https://github.com/berravatansever2-lgtm) · [LinkedIn](https://linkedin.com/in/)
