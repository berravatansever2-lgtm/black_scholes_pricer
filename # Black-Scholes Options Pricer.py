# Black-Scholes Options Pricer
# Inputs: S (stock price), K (strike), T (time to expiry), r (risk-free rate), sigma (volatility)
# Output: Call price, Put price, Delta, Gamma, Vega, Theta, Rho

# BLACK-SCHOLES PRICER
#
# What is Black-Scholes trying to do?
# → Price a European option — what is the fair value today of the right to buy/sell at price K at time T
#
# Inputs:
# S = current stock price
# K = strike price
# T = time to expiration (in years)
# r = risk-free interest rate
# sigma = volatility of the stock
#
# Step 1: Calculate d1
# d1 = [ln(S/K) + (r + sigma²/2) * T] / [sigma * sqrt(T)]
#
# Step 2: Calculate d2
# d2 = d1 - sigma * sqrt(T)
#
# Step 3: Calculate N(d1) and N(d2)
# N() is the cumulative normal distribution function
# This is where scipy.stats.norm.cdf comes in
#
# Step 4: Calculate Call price
# C = S * N(d1) - K * e^(-rT) * N(d2)
#
# Step 5: Calculate Put price using Put-Call parity
# P = K * e^(-rT) * N(-d2) - S * N(-d1)
#
# Step 6: Calculate Greeks
# Delta = N(d1) for call, N(d1)-1 for put
# Gamma = N'(d1) / (S * sigma * sqrt(T))
# Vega = S * N'(d1) * sqrt(T)
# Theta = complex — do this last
# Rho = K * T * e^(-rT) * N(d2) for call


from scipy.stats import norm
import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np

def get_stock_data(ticker):
    """
    Pulls live price and calculates historical volatility
    for any stock ticker
    """
    stock = yf.Ticker(ticker)
    
    # Get current price
    S = stock.history(period="1d")['Close'].iloc[-1]
    
    # Get 1 year historical data for volatility
    hist = stock.history(period="1y")['Close']
    log_returns = np.log(hist / hist.shift(1)).dropna()
    sigma = log_returns.std() * np.sqrt(252)
    
    print(f"Ticker: {ticker}")
    print(f"Current Price: ${S:.2f}")
    print(f"Historical Volatility: {sigma:.4f} ({sigma*100:.2f}%)")
    
    return S, sigma

def suggest_strikes(S, sigma, T):
    """
    Suggests strikes based on where the stock
    could realistically move given its volatility
    
    Uses the 1 standard deviation move formula:
    Expected move = S * sigma * sqrt(T)
    """
    expected_move = S * sigma * np.sqrt(T)
    
    strikes = {
        'ATM':   round(S),                      # at the money
        '1SD_up': round(S + expected_move),      # 1 std dev above
        '1SD_down': round(S - expected_move),    # 1 std dev below
        '2SD_up': round(S + 2 * expected_move),  # 2 std devs above
        '2SD_down': round(S - 2 * expected_move) # 2 std devs below
    }
    
    print(f"\nExpected move over {T*12:.0f} months: ±${expected_move:.2f}")
    print("\nSuggested strikes:")
    for name, strike in strikes.items():
        print(f"  {name}: ${strike}")
    
    return strikes

def black_scholes(S, K, T, r, sigma):
    # Step 1: Calculate d1
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    
    # Step 2: Calculate d2
    d2 = d1 - sigma * np.sqrt(T)
    
    # Step 3: Calculate N(d1) and N(d2)
    N_d1 = norm.cdf(d1)
    N_d2 = norm.cdf(d2)
    
    # Step 4: Calculate Call price
    call_price = S * N_d1 - K * np.exp(-r * T) * N_d2
    
    # Step 5: Calculate Put price using Put-Call parity
    put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
    # Step 6: Calculate Greeks
    delta_call = N_d1
    delta_put = N_d1 - 1
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega = S * norm.pdf(d1) * np.sqrt(T)
    
    # Theta calculation (complex, simplified version)
    theta_call = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                  - r * K * np.exp(-r * T) * N_d2)
    
    theta_put = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                 + r * K * np.exp(-r * T) * norm.cdf(-d2))
    
    rho_call = K * T * np.exp(-r * T) * N_d2
    rho_put = -K * T * np.exp(-r * T) * norm.cdf(-d2)
    
    return {
        'call_price': call_price,
        'put_price': put_price,
        'delta_call': delta_call,
        'delta_put': delta_put,
        'gamma': gamma,
        'vega': vega,
        'theta_call': theta_call,
        'theta_put': theta_put,
        'rho_call': rho_call,
        'rho_put': rho_put
    }
    

def plot_option_prices(K, T, r, sigma, S_range, n_points, ticker):
    
    S_min = K * (1 - S_range)
    S_max = K * (1 + S_range)
    stock_prices = np.linspace(S_min, S_max, n_points)
    
    calls = []
    puts = []
    
    for S in stock_prices:
        result = black_scholes(S, K, T, r, sigma)
        calls.append(result['call_price'])
        puts.append(result['put_price'])
    
    plt.figure(figsize=(10, 6))
    plt.plot(stock_prices, calls, label='Call Price', color='green')
    plt.plot(stock_prices, puts, label='Put Price', color='red')
    plt.axvline(x=K, color='black', linestyle='--', label=f'Strike K={K}')
    plt.xlabel('Stock Price')
    plt.ylabel('Option Price')
    plt.title(f'Black-Scholes | {ticker} K={K} T={T}yr σ={sigma:.2f}')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'options_{ticker}_{T}yr.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Plot saved: options_{ticker}_{T}yr.png")

def analyze_stock(ticker, T, r):
    """
    Full analysis pipeline for any stock
    """
    # Step 1: Get real data
    S, sigma = get_stock_data(ticker)
    
    # Step 2: Suggest strikes
    strikes = suggest_strikes(S, sigma, T)
    
    # Step 3: Price options at each strike
    print(f"\nBlack-Scholes prices for {ticker}:")
    print(f"{'Strike':<12} {'Call':>10} {'Put':>10} {'Delta':>10}")
    print("-" * 45)
    
    for name, K in strikes.items():
        result = black_scholes(S, K, T, r, sigma)
        print(f"{name:<8} ${K:<6} "
              f"${result['call_price']:>8.2f}  "
              f"${result['put_price']:>8.2f}  "
              f"{result['delta_call']:>8.4f}")
    
    # Step 4: Plot
    plot_option_prices(round(S), T, r, sigma, S_range, n_points, ticker)
    
    return S, sigma, strikes

ticker = "NVDA"  # Example stock ticker
T = 0.5  # Time to expiration in years (6 months)
r = 0.05  # Risk-free interest rate (5%)
S_range = 0.5  # Range for plotting (30% above and below strike)
n_points = 100  # Number of points for plotting

analyze_stock(ticker, T, r) 

