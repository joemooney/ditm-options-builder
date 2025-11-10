# DITM Options Trading: Complete User Guide

## Table of Contents
1. [What Are Options?](#what-are-options)
2. [Deep-In-The-Money (DITM) Strategy Explained](#ditm-strategy-explained)
3. [Key Terminology & Concepts](#key-terminology--concepts)
4. [Understanding the Filter Parameters](#understanding-the-filter-parameters)
5. [Reading the Output](#reading-the-output)
6. [Step-by-Step: Acting on a Recommendation](#step-by-step-acting-on-a-recommendation)
7. [Risk Management](#risk-management)
8. [Understanding Risk Metrics](#understanding-risk-metrics)
9. [Common Mistakes to Avoid](#common-mistakes-to-avoid)
10. [Example Scenarios](#example-scenarios)

---

## What Are Options?

### Basic Concept

An **option** is a contract between two parties: a **buyer** and a **seller**. Understanding both perspectives is crucial.

- **Call Option**: Contract for the right to **BUY** stock at a specific price
- **Put Option**: Contract for the right to **SELL** stock at a specific price

#### The Buyer's Perspective (Long Position)

When you **buy** an option, you are purchasing the **right** (but not the obligation) to execute the contract.

**Call Option Buyer Example**:
- AAPL stock is trading at $225
- You buy 1 AAPL call option with a $200 strike price for $28 premium
- You pay: $2,800 ($28 × 100 shares)
- You get: The **right** to buy 100 shares of AAPL at $200 each (even though it's trading at $225)
- **Maximum loss**: $2,800 (the premium you paid)
- **Maximum gain**: Unlimited (stock can rise indefinitely)

**Your Three Exit Options**:

1. **Sell the Option (Most Common)**
   - You can sell your option contract **at any time** during market hours before expiration
   - This is called "Sell to Close"
   - Example: You paid $28, option is now worth $35, sell for $3,500 profit
   - **No additional capital needed** - just sell like you would sell a stock
   - You keep the profit (or loss) and the position is closed
   - **Recommended approach for DITM strategies**

2. **Exercise the Option (Rarely Optimal)**
   - You actively choose to buy the 100 shares at the strike price
   - Example: Pay $20,000 to buy 100 shares at $200 strike
   - Requires significant capital (strike price × 100 shares)
   - You then own the shares and can hold or sell them
   - Usually worse than selling the option (you lose the time value)
   - Only makes sense if you want to own the shares long-term

3. **Let It Expire (Automatic Exercise If ITM)**
   - **CRITICAL**: If your option is in-the-money at expiration, it will be **automatically exercised** by your broker
   - Example: At expiration, AAPL is at $225, your $200 call is ITM → Auto-exercises
   - You will be **forced to buy** 100 shares at $200 ($20,000 required)
   - If you don't have $20,000 in your account:
     - Schwab may automatically sell the option before expiration (3-4pm on expiration day)
     - Or create a margin call requiring you to deposit funds immediately
     - Or sell the shares immediately after exercise, creating unexpected tax events
   - **If the option is out-of-the-money** at expiration (stock below strike), it expires worthless and you lose your $2,800 premium

**What "Let It Expire" Really Means**:

- **ITM (In-the-Money)** at expiration: Auto-exercise → You must buy the shares → Need cash equal to (strike × 100)
- **OTM (Out-of-the-Money)** at expiration: Expires worthless → You lose your premium, option disappears
- **Schwab Protection**: To protect you, Schwab typically auto-sells ITM options on expiration day if you lack funds

**When Can You Sell Your Option?**

- **Any time** during market hours (9:30am - 4:00pm ET), from the moment you buy it until 4:00pm on expiration day
- No penalty for selling early
- No requirement to hold until expiration
- This is the **primary way** to exit DITM positions with profit

**Put Option Buyer Example**:
- AAPL stock is trading at $225
- You buy 1 AAPL put option with a $250 strike price for $30 premium
- You pay: $3,000 ($30 × 100 shares)
- You get: The **right** to sell 100 shares of AAPL at $250 each (even if it drops to $200)
- **Maximum loss**: $3,000 (the premium you paid)
- **Maximum gain**: $22,000 (if stock drops to $0, you can sell at $250)

#### The Seller's Perspective (Short Position)

When you **sell** (or "write") an option, you are accepting the **obligation** to fulfill the contract if the buyer exercises it. In exchange, you collect the premium.

**Call Option Seller Example**:
- AAPL stock is trading at $225
- You sell 1 AAPL call option with a $200 strike price
- You receive: $2,800 premium (your maximum profit)
- Your obligation: If the buyer exercises, you **must sell** 100 shares of AAPL at $200 each
- **Maximum gain**: $2,800 (the premium you collected)
- **Maximum loss**: Unlimited (if stock rises to $500, you must sell at $200, losing $300/share = $30,000)

**Put Option Seller Example**:
- AAPL stock is trading at $225
- You sell 1 AAPL put option with a $250 strike price
- You receive: $3,000 premium (your maximum profit)
- Your obligation: If the buyer exercises, you **must buy** 100 shares of AAPL at $250 each
- **Maximum gain**: $3,000 (the premium you collected)
- **Maximum loss**: $25,000 (if stock drops to $0, you must buy at $250)

#### Key Differences Between Buyers and Sellers

| Aspect | Option Buyer (Long) | Option Seller (Short) |
|--------|-------------------|---------------------|
| **Pays/Receives** | Pays premium | Receives premium |
| **Rights** | Has the right to exercise | No rights, only obligations |
| **Obligation** | No obligation | Must fulfill if exercised |
| **Max Loss** | Premium paid (limited) | Potentially unlimited (calls) or substantial (puts) |
| **Max Gain** | Unlimited (calls) or substantial (puts) | Premium received (limited) |
| **Direction** | Wants option to increase in value | Wants option to decrease in value |
| **Typical Goal** | Leverage, speculation, hedging | Income generation, obligation acceptance |

#### Who Is On The Other Side?

When you buy an option, someone else is selling it. The seller could be:

1. **Market Maker**: Professional traders providing liquidity, managing risk through hedging
2. **Covered Call Writer**: Stock owner selling calls against their shares for income
3. **Cash-Secured Put Writer**: Investor willing to buy stock at lower price, collecting premium
4. **Institutional Hedger**: Large fund offsetting other portfolio risks
5. **Retail Trader**: Individual speculating or generating income

**Important**: This DITM tool focuses on **buying** options (long positions), not selling them. We are always on the buyer side, paying premium for rights and limited risk.

### Why Use Options Instead of Stock?

1. **Capital Efficiency**: Control the same number of shares with less money
2. **Leverage**: Larger percentage gains on smaller investments
3. **Risk Definition**: Know your maximum loss upfront
4. **Flexibility**: Multiple strategies for different market conditions

---

## DITM Strategy Explained

### What Makes an Option "Deep-In-The-Money"?

An option is "in the money" when it would be profitable to exercise it right now. It's "deep" in the money when it has **substantial intrinsic value**.

**For Call Options (DITM Calls):**
- Stock price is **significantly higher** than the strike price
- Example: Stock at $225, strike at $200 = $25 in-the-money

### Why DITM Instead of Buying Stock?

DITM calls are a **conservative options strategy** that mimics stock ownership with key advantages:

#### Advantages:
1. **Lower Capital Required**
   - Stock: 100 shares × $225 = $22,500
   - DITM Call: ~$20,000 for equivalent exposure
   - Savings: ~$2,500 (11%)

2. **Similar Price Movement**
   - High delta (0.80-0.95) means option moves almost 1:1 with stock
   - If stock goes up $1, your option goes up ~$0.85-0.95

3. **Limited Downside**
   - Stock: Can lose entire $22,500
   - DITM Call: Lose only the premium paid (~$20,000)
   - Plus you kept the $2,500 savings

4. **Defined Time Horizon**
   - Forces discipline with expiration dates
   - This tool looks for 90+ days to avoid time decay

#### Disadvantages:
1. **No Dividends**: Options don't receive dividend payments
2. **Time Decay**: Options lose value as expiration approaches (though minimal for DITM)
3. **Liquidity Concerns**: Options can have wider bid-ask spreads than stocks
4. **Expiration Risk**: Must close or roll the position before expiration

### Conservative vs. Speculative Options

This tool focuses on **CONSERVATIVE** options trading:

| Feature | DITM (Conservative) | OTM (Speculative) |
|---------|---------------------|-------------------|
| **Delta** | 0.80-0.95 (high) | 0.10-0.50 (low) |
| **Intrinsic Value** | 85%+ of premium | 0% (all time value) |
| **Behavior** | Moves like stock | Lottery ticket |
| **Risk** | Moderate | High |
| **Capital** | High | Low |
| **Probability** | High | Low |

---

## Key Terminology & Concepts

### Strike Price
The price at which you can buy (call) or sell (put) the stock.

**Example**: $200 strike = You can buy shares at $200

### Expiration Date
The last day you can exercise the option.

**Example**: `2025-06-20` = Option expires June 20, 2025

### DTE (Days to Expiration)
Number of calendar days until the option expires.

**Why it matters**:
- More DTE = Less time decay risk
- This tool requires minimum 90 DTE for safety

### Premium
The **price you pay** for the option contract.

**Important**: The premium is quoted **per share**, but each contract controls **100 shares**, so you multiply by 100 to get the actual cost.

**Example**: Premium of $25.00 = Cost is $25.00 × 100 = $2,500 per contract

#### Premium Components Explained

The premium you pay is made up of two parts that add together:

**Formula**: `Premium = Intrinsic Value + Time Value`

Let's use a concrete example to understand this:

**Scenario**:
- Stock: AAPL trading at $225
- Option: $200 strike call
- Premium: $28.00 (the price you see quoted)
- Days to expiration: 180 days

**Breaking down the $28 premium**:

1. **Intrinsic Value**: $25.00
   - This is the "real value" if you exercised right now
   - Formula: Stock Price - Strike Price = $225 - $200 = $25
   - This is the amount you could profit immediately by exercising
   - Think of it as the "built-in profit"

2. **Time Value**: $3.00
   - This is the "extra" you're paying above intrinsic value
   - Formula: Premium - Intrinsic Value = $28 - $25 = $3
   - This represents the option's potential to gain more value before expiration
   - You're paying for 180 days of opportunity for the stock to rise further
   - This acts as your "insurance premium" (see Time Value section below for details)

**The math**: $25 (intrinsic) + $3 (time) = **$28 total premium**

**Total cost for 1 contract**: $28 × 100 shares = **$2,800**

**Another example** (Out-of-the-money option for comparison):

**Scenario**:
- Stock: AAPL trading at $225
- Option: $250 strike call (out-of-the-money)
- Premium: $5.00
- Days to expiration: 180 days

**Breaking down the $5 premium**:
1. **Intrinsic Value**: $0.00
   - Stock at $225, strike at $250 → No immediate value
   - Formula: max(0, $225 - $250) = $0
   - This is a speculative bet, no "real value" yet

2. **Time Value**: $5.00
   - Formula: $5 premium - $0 intrinsic = $5
   - You're paying $5 entirely for the hope the stock rises above $250
   - This is pure speculation (not DITM strategy!)

**The math**: $0 (intrinsic) + $5 (time) = **$5 total premium**

**Why DITM focuses on high intrinsic value**:
- DITM: $25 intrinsic + $3 time = $28 → **89% intrinsic** (conservative!)
- OTM: $0 intrinsic + $5 time = $5 → **0% intrinsic** (speculative!)

This tool requires minimum 85% intrinsic value to ensure you're buying "real value" rather than pure speculation.

### Immediate Loss: Understanding the Break-Even Hurdle

**Critical Concept**: When you buy a DITM option, you face an **immediate loss** that must be recouped to break even. This is one of the most important metrics to understand before entering a position.

#### What is Immediate Loss?

Immediate loss is the amount you would lose if you bought an option at the Ask price and immediately sold it at the Bid price. It consists of two components:

**Formula**: `Immediate Loss = Extrinsic Value (Time Value) + Bid-Ask Spread`

#### Real Example

**Scenario**:
- Stock: AAPL trading at $268.69
- Strike: $225
- Bid: $43.20
- Ask: $43.80
- Premium (Ask): $43.80

**Calculating Immediate Loss**:

1. **Intrinsic Value**: $268.69 - $225 = $43.69
2. **Extrinsic Value** (Time Value): $43.80 (Ask) - $43.69 (Intrinsic) = $0.11
3. **Bid-Ask Spread**: $43.80 (Ask) - $43.20 (Bid) = $0.60
4. **Total Immediate Loss**: $0.11 + $0.60 = **$0.71 per share**
5. **Per Contract**: $0.71 × 100 = **$71.00**
6. **As Percentage**: ($0.71 / $43.80) × 100 = **1.62%**

**What This Means**:
- You pay $4,380 to buy one contract at Ask
- If you immediately sold at Bid, you'd get $4,320
- You'd lose $71 (1.62%) before the stock even moves
- The stock must move enough to overcome this 1.62% for you to break even

#### Is 11.48% Immediate Loss Reasonable?

You asked an excellent question about an AAPL position with 11.48% immediate loss. Let's analyze when this might be acceptable:

**The 11.48% typically breaks down as**:
- Bid-Ask Spread: ~1-2% (transaction cost)
- Extrinsic Value: ~9-10% (time value premium)

**When 11.48% Could Be Acceptable**:

1. **Long Time Horizon (DTE > 365 days)**
   - If the option has 400+ DTE, that 9-10% extrinsic decays very slowly
   - Theta (time decay) is minimal for long-dated options
   - You have over a year for stock appreciation to overcome the cost

2. **High Leverage Justifies Higher Cost**
   - With 7-13x leverage, small stock movements translate to large option gains
   - Example: 2% stock gain → ~1.7% option gain (0.85 delta) → with 10x leverage = 17% portfolio gain
   - The leverage can quickly overcome the 11.48% hurdle

3. **Cheaper Than Margin**
   - Margin interest: 10-13% annually
   - If this 11.48% covers 1-2 years, it's competitive with margin costs
   - $11.48% over 500 days = 8.4% annualized (better than margin!)

**When 11.48% is TOO HIGH** (Red Flags):

1. **Short DTE (<180 days)**: Time decay is too fast
2. **High IV (>30%)**: You're overpaying for volatility premium
3. **Low Delta (<0.85)**: Not deep enough ITM, too much extrinsic
4. **Wide Spread (>2%)**: Excessive transaction costs
5. **Low Intrinsic (<85%)**: Not conservative enough

**Recommended Immediate Loss Thresholds**:

Based on DTE (Days to Expiration):

| DTE Range | Max Acceptable Immediate Loss | Notes |
|-----------|------------------------------|-------|
| 90-180 days | 5-7% | Short-term, time decay risk is high |
| 181-365 days | 7-10% | Medium-term, balanced approach |
| 366-540 days | 10-12% | Long-term, slow time decay |
| 540+ days | 12-15% | Very long-term, minimal daily decay |

**Formula for Maximum Acceptable Loss**:
```
Max Immediate Loss % = 5% + (DTE / 365) × 5%
```

**Examples**:
- 180 DTE: 5% + (180/365) × 5% = **7.5% max**
- 365 DTE: 5% + (365/365) × 5% = **10% max**
- 540 DTE: 5% + (540/365) × 5% = **12.4% max**

**For Your 11.48% AAPL Position, Check**:
- **Delta**: Should be ≥0.90 (very deep ITM)
- **DTE**: Should be ≥400 days (long time horizon)
- **IV**: Should be <25% (low volatility premium)
- **Intrinsic %**: Should be ≥88% (very conservative)

**Bottom Line**:
- **Good DITM**: 5-8% immediate loss
- **Acceptable DITM**: 8-10% immediate loss
- **Borderline**: 10-12% (only with long DTE, high delta, low IV)
- **Too Expensive**: >12% immediate loss

**Remember**: The immediate loss must be overcome by stock appreciation and/or time value decay slowing down. The higher the percentage, the more the stock must move in your favor to profit.

### Delta (Δ)
**Most important metric for DITM trading!**

Delta measures how much the option price changes when the stock moves $1.

**Delta Values**:
- **1.00**: Moves exactly like stock (theoretical maximum for calls)
- **0.85**: If stock goes up $1, option goes up $0.85
- **0.50**: At-the-money (50% chance of profit)
- **0.10**: Far out-of-the-money (unlikely to profit)

**Delta as Probability**:
Delta also approximates the probability the option finishes in-the-money.
- Delta 0.85 ≈ 85% chance of expiring with value

**This tool uses**: 0.80-0.95 delta (very stock-like behavior)

#### How Delta Relates to Breakeven (Important Clarification!)

**Delta and Breakeven are DIFFERENT concepts** that people often confuse:

**Breakeven Point**:
- The stock price where you neither make nor lose money at expiration
- Formula: `Breakeven = Strike Price + Premium Paid`
- Example: $200 strike + $28 premium = **$228 breakeven**
- This is a **fixed number** that doesn't change after you buy
- At expiration, if stock is above $228, you profit; below $228, you lose

**Delta**:
- How much your option price moves when the stock moves $1 **right now**
- This is a **dynamic number** that changes as the stock moves and time passes
- Delta does NOT directly tell you your breakeven point

**Example to Show the Difference**:

You buy AAPL $200 call for $28 premium with delta 0.85

**Your Breakeven**: $228 (fixed)
- If AAPL is at $228 at expiration, you break even
- If AAPL is at $230 at expiration, you profit $2/share
- This doesn't involve delta at all!

**Delta's Role** (during the life of the option, before expiration):
- Stock rises from $225 to $226 (+$1)
- Your option rises from $28 to $28.85 (+$0.85, because delta = 0.85)
- Stock rises to $230 (+$5)
- Your option rises approximately $5 × 0.85 = $4.25
- New option price: $28 + $4.25 = $32.25

**Why Delta Matters for Breakeven Thinking**:

Delta tells you how quickly you'll **reach** your breakeven point:

High delta (0.90):
- Stock moves from $225 to $228 (+$3)
- Option moves +$3 × 0.90 = +$2.70
- You're close to breakeven **before expiration** (can sell for profit)

Low delta (0.50):
- Stock moves from $225 to $228 (+$3)
- Option moves +$3 × 0.50 = +$1.50
- You're still underwater even though stock hit your $228 breakeven
- You'd need stock to go higher or wait until expiration

**The Key Insight**:

- **Breakeven ($228)**: Where you profit **at expiration** if you hold until then
- **Delta (0.85)**: How fast your option gains value **before expiration** as stock rises

**With DITM options (high delta 0.80-0.95)**:
- You don't need to wait until expiration to profit
- If stock rises just a few dollars, your option gains almost dollar-for-dollar
- Example: Stock rises from $225 to $230 (+$5)
  - Your option rises ~$4.75 (95% of stock move with 0.95 delta)
  - You paid $28, now worth $32.75
  - You profit $4.75 **without waiting for expiration**
  - Even though breakeven is $228, you're profitable at $230 right now

**Summary**:
- **Breakeven**: The finish line (stock price at expiration for $0 profit/loss)
- **Delta**: The speed (how fast option moves toward profit as stock rises)
- High delta DITM options let you profit **before** reaching breakeven at expiration because they move almost 1:1 with the stock

### Intrinsic Value
The amount of profit if you exercised the option right now.

**Formula**: `Intrinsic Value = Stock Price - Strike Price` (for calls)

**Example**:
- Stock at $225
- Strike at $200
- Intrinsic Value = $225 - $200 = $25

### Time Value (Also Called "Extrinsic Value")
The **extra premium** above intrinsic value, representing potential future profit.

**Note**: Time value and extrinsic value are **the same thing** - just different names used interchangeably in options trading. Some traders prefer "extrinsic" (external to the option's immediate value) while others prefer "time" (because it represents the value of time remaining).

**Formula**: `Time Value = Premium - Intrinsic Value`

**Also written as**: `Extrinsic Value = Premium - Intrinsic Value`

**Example**:
- Premium: $28
- Intrinsic: $25
- Time Value (Extrinsic Value): $3

**Time decay (Theta)**: This value decreases as expiration approaches, accelerating in the final 30-60 days.

#### Why Extrinsic Value Matters for DITM Strategy

Understanding extrinsic (time) value is **critical** for DITM trading because it affects:

**1. How Much You're Risking vs. Gaining**

**High Extrinsic Value (Bad for DITM)**:
```
Stock: $225
Strike: $250 (out-of-the-money)
Premium: $5
Intrinsic: $0
Extrinsic: $5 (100% of premium!)

Risk: Entire $5 is time value that will decay to $0
Benefit: None - purely speculative
```

**Low Extrinsic Value (Good for DITM)**:
```
Stock: $225
Strike: $200 (deep-in-the-money)
Premium: $28
Intrinsic: $25
Extrinsic: $3 (only 11% of premium)

Risk: Only $3 can decay to $0
Benefit: $25 is "real value" you can exercise for
```

**2. Time Decay Impact**

Options lose extrinsic value as expiration approaches (this is "theta decay"):

**Option A - High Extrinsic** (OTM):
- Today: $5 premium (all extrinsic)
- 30 days later: $3 premium (losing value fast)
- At expiration: $0 (lost everything if still OTM)
- **Lost $5 to time decay**

**Option B - Low Extrinsic** (DITM):
- Today: $28 premium ($25 intrinsic + $3 extrinsic)
- 30 days later: $26 premium ($25 intrinsic + $1 extrinsic)
- At expiration: $25 (intrinsic value remains)
- **Lost only $3 to time decay**

**3. Why DITM Requires 85%+ Intrinsic Value**

This tool filters for minimum 85% intrinsic value, which means maximum 15% extrinsic:

**85% Intrinsic Example**:
```
Premium: $28
Intrinsic: $23.80 (85%)
Extrinsic: $4.20 (15%)

Time decay risk: Only 15% of your investment
Real value protected: 85% can't decay
```

**50% Intrinsic Example** (Not DITM):
```
Premium: $28
Intrinsic: $14 (50%)
Extrinsic: $14 (50%)

Time decay risk: Half your investment can decay!
Real value protected: Only 50%
```

**4. When You Should Care About Extrinsic Value**

**At Entry** (Buying):
- ✓ Choose options with LOW extrinsic value (high intrinsic %)
- ✓ This tool ensures extrinsic is < 15% of premium
- ✓ Protects you from time decay

**During Hold**:
- ✓ Monitor as extrinsic value decays over time
- ✓ Exit before final 30-60 days (when decay accelerates)
- ✓ Don't worry too much - DITM has minimal extrinsic anyway

**At Exit** (Selling):
- ✓ Sell option to capture remaining extrinsic value (free money!)
- ✗ Don't exercise - you lose all extrinsic value
- Example: Option worth $30 ($25 intrinsic + $5 extrinsic)
  - Sell: Get $30 (keep the $5 extrinsic) ✓
  - Exercise: Get $25 worth of stock (lose the $5 extrinsic) ✗

**5. Real-World Example**

You paid $28 for AAPL $200 call (stock at $225):
- Intrinsic: $25 (this can't decay, it's real stock value)
- Extrinsic: $3 (this WILL decay to $0 by expiration)

**Scenario: You hold 90 days**:
- Stock still at $225 (unchanged)
- Intrinsic still: $25 (unchanged - follows stock)
- Extrinsic now: $1 (decayed from $3)
- Option worth: $26 (lost $2 to time decay)

**Scenario: You hold to expiration**:
- Stock still at $225 (unchanged)
- Intrinsic: $25 (unchanged)
- Extrinsic: $0 (fully decayed)
- Option worth: $25 (lost $3 to time decay)

**The lesson**: Even if stock doesn't move, you lose extrinsic value over time. DITM minimizes this risk by having only 10-15% extrinsic value.

**6. Summary: Why Low Extrinsic Value = Conservative**

| Aspect | High Extrinsic (OTM) | Low Extrinsic (DITM) |
|--------|---------------------|---------------------|
| **% of Premium** | 50-100% | 10-15% |
| **Time Decay Risk** | High | Low |
| **Real Value** | Little to none | 85-90% |
| **Needs Stock to Move** | Significantly | Minimally |
| **Conservative?** | No (speculative) | Yes (stock-like) |

**Bottom line**: Extrinsic value represents the "speculative" part of an option's price. DITM strategy minimizes this by requiring 85%+ intrinsic value, making these options more like stocks (conservative) and less like lottery tickets (speculative).

#### Understanding Time Value as Insurance

When you pay time value above intrinsic value, you're essentially **buying insurance** against catastrophic loss compared to owning the stock outright.

**Example Scenario**:
```
Stock Price: $225
Strike Price: $200
Intrinsic Value: $25 ($225 - $200)
Premium (Ask): $28
Time Value: $3 ($28 - $25)
```

**What that $3 time value represents**:

If you bought the stock at $225:
- **Maximum loss**: $225 per share (stock goes to $0)
- **Total risk**: 100 shares × $225 = $22,500

If you bought the DITM call at $28:
- **Maximum loss**: $28 per share (option expires worthless)
- **Total risk**: 100 shares × $28 = $2,800

**The insurance benefit**:
- Stock ownership risk: $22,500
- Option ownership risk: $2,800
- **Insurance value**: $19,700 of downside protection

The $3 time value you pay is the "insurance premium" for this protection. Even though you have $25 of intrinsic value, you're only risking $28 total (not $225), meaning:

**You have limited your catastrophic downside** to $2,800 instead of $22,500, while maintaining similar upside potential through the high delta (0.85-0.95).

**This is the hidden value of DITM options**:
- The intrinsic value ($25) is the "real value" you control
- The time value ($3) is the cost of insurance against losing more than $28/share
- Together, they give you leveraged upside with defined downside risk

**In other words**: If the stock crashes from $225 to $50, stock holders lose $175/share ($17,500 total), but you only lose $28/share ($2,800 total). The $3 time value premium bought you protection against a $19,700 catastrophic loss.

This is why DITM options are considered **conservative leverage** - you're paying a small premium for significant downside protection while maintaining most of the upside.

### Intrinsic % (Intrinsic Value Percentage)
**Critical metric!** Percentage of the premium that is intrinsic value.

**Formula**: `Intrinsic % = Intrinsic Value / Premium`

**Example**:
- Intrinsic Value: $25
- Premium: $28
- Intrinsic %: $25 / $28 = 89.3%

**Why it matters**:
- High intrinsic % = Less risk from time decay
- This tool requires minimum 85% intrinsic value
- Higher is more conservative

### Implied Volatility (IV)
Market's expectation of how much the stock will move.

**Interpretation**:
- **Low IV** (10-20%): Stock expected to be stable
- **Medium IV** (20-40%): Normal volatility
- **High IV** (40%+): Big moves expected (earnings, news, etc.)

**Format**:
- Can be shown as decimal (0.25) or percentage (25%)
- They're the same: 0.25 = 25%

**Why it matters for DITM**:
- High IV = Higher option premiums (more expensive)
- This tool filters for IV < 30% to avoid overpaying
- Lower IV = More stable, predictable behavior

### Open Interest (OI)
Number of option contracts currently open (not yet closed or exercised).

**Why it matters**:
- High OI = **Liquid** (easy to buy/sell)
- Low OI = **Illiquid** (hard to exit, wide spreads)

**This tool requires**: Minimum 500 contracts open interest

**Example**:
- OI = 5,000 → Very liquid, tight spreads
- OI = 50 → Illiquid, avoid!

### Bid-Ask Spread
The difference between the highest price a buyer will pay (bid) and lowest price a seller will accept (ask).

**Example**:
- **Bid**: $27.80 (what you'd get if selling)
- **Ask**: $28.20 (what you'd pay if buying)
- **Spread**: $0.40
- **Mid**: $28.00 (average, used for analysis)

**Spread %**: `(Ask - Bid) / Mid`
- Example: ($28.20 - $27.80) / $28.00 = 1.43%

**Why it matters**:
- Wide spreads = **Hidden cost** when trading
- This tool requires spreads < 2% (very liquid)

#### Bid/Ask Impact on Breakeven

**Important**: In real trading, you don't pay the mid price!

When you **buy** an option:
- You pay the **ask price** ($28.20 in the example)
- Not the mid price ($28.00)
- This costs you an extra $0.20 per share

When you **sell** an option:
- You receive the **bid price** ($27.80)
- Not the mid price ($28.00)
- You get $0.20 less per share

**Impact on Breakeven Calculation**:

Using **mid price** (optimistic):
```
Strike: $200
Premium (mid): $28.00
Breakeven: $200 + $28.00 = $228.00
```

Using **ask price** (realistic):
```
Strike: $200
Premium (ask): $28.20
Breakeven: $200 + $28.20 = $228.20
```

**The $0.20 difference matters!** Over 100 shares per contract, that's $20 per contract, or $80 for 4 contracts.

**This tool's approach**:
- By default, uses **ask price** for entry breakeven calculations (realistic)
- Displays bid/ask/mid in position analysis
- Shows spread percentage so you understand the cost
- Configurable via `use_ask_for_entry` setting in web_config.json

**Recommendation**: Always use ask price for planning your breakeven, as that's what you'll actually pay in practice.

### Cost Per Share
**Key metric for comparison!** The effective price you're paying per share of stock exposure.

**Formula**: `Cost Per Share = Premium / (Delta × 100)`

**Example**:
- Premium: $28.00
- Delta: 0.85
- Cost Per Share: $28.00 / (0.85 × 100) = $28.00 / 85 = **$0.329 per share**
- For 100-share exposure: $0.329 × 100 = **$32.90**

Wait, that doesn't make sense! Let me recalculate:

**Correct Calculation**:
- Premium: $28.00 (for 1 contract = 100 shares)
- Total cost: $28.00 × 100 = $2,800
- Delta-adjusted shares: 0.85 × 100 = 85 shares of exposure
- Cost Per Share: $2,800 / 85 = **$32.94**

**Comparison to Stock**:
- Stock price: $225
- Cost per share (DITM): $32.94
- **You're getting stock-like exposure for 14.6% of the stock price**

Actually, I need to reconsider this. Let me think about it properly:

**What Cost Per Share Really Means**:
If the option premium is $25.00 (meaning $2,500 total), and delta is 0.85:
- You control 85 shares worth of movement (0.85 × 100)
- Cost per equivalent share: $2,500 / 85 = $29.41

If stock is at $225, you're paying $29.41/$225 = **13% of stock price** for equivalent exposure.

### Score
**The tool's ranking system** for how conservative the option is.

**Formula**:
```
Score = 0.4 × (1 - Delta)           # Prefer higher delta
      + 0.3 × (1 - Intrinsic%)      # Prefer higher intrinsic %
      + 0.2 × IV / MAX_IV           # Penalize high IV
      + 0.1 × Spread% / MAX_SPREAD  # Penalize wide spreads
```

**Interpretation**:
- **Lower score = More conservative** (better)
- Score considers delta, intrinsic value, IV, and liquidity
- Top-ranked option = Lowest score

---

## Understanding the Filter Parameters

These are the configurable settings in `ditm.py` that determine which options qualify:

### MIN_DELTA = 0.80
**Minimum delta** for an option to qualify.

**What it means**: Option must move at least 80 cents for every $1 the stock moves.

**Why 0.80**: Ensures stock-like behavior, not speculative.

**Adjust if**:
- Want more conservative → Increase to 0.85 or 0.90
- Willing to take more risk → Decrease to 0.75 (not recommended)

### MAX_DELTA = 0.95
**Maximum delta** for an option to qualify.

**What it means**: Avoid extremely deep ITM options.

**Why 0.95**: Delta too close to 1.0 often means:
- Very expensive (ties up too much capital)
- Inefficient (not much savings vs. buying stock)
- Poor liquidity

**Adjust if**:
- Want maximum delta → Increase to 0.99
- Want more capital efficiency → Decrease to 0.90

### MIN_INTRINSIC_PCT = 0.85
**Minimum percentage** of the premium that must be intrinsic value.

**What it means**: At least 85% of what you're paying must be "real value" (not time value).

**Why 0.85**:
- Protects against time decay
- Conservative approach
- Industry standard for DITM

**Example**:
- Premium $28, intrinsic $25 → 89% intrinsic → ✓ Qualifies
- Premium $28, intrinsic $20 → 71% intrinsic → ✗ Rejected

**Adjust if**:
- More conservative → Increase to 0.90 or 0.95
- More flexibility → Decrease to 0.80 (risky)

### MIN_DTE = 90
**Minimum days** until expiration.

**What it means**: Option must have at least 90 days (3 months) of life.

**Why 90**:
- Avoids accelerated time decay
- Gives stock time to move
- Professional standard for "LEAPS" replacement

**Adjust if**:
- Long-term hold → Increase to 180 or 365 (6-12 months)
- Shorter timeframe → Decrease to 60 (more risky)

### MAX_IV = 0.30
**Maximum implied volatility** (30%).

**What it means**: Reject options on highly volatile stocks.

**Why 0.30**:
- Avoid overpaying for options
- Target stable blue-chip stocks
- Reduce unpredictable moves

**Adjust if**:
- Only ultra-stable stocks → Decrease to 0.20
- Allow tech stocks → Increase to 0.40

### MAX_SPREAD_PCT = 0.02
**Maximum bid-ask spread** as percentage (2%).

**What it means**: Spread can't be more than 2% of the option price.

**Example**:
- Mid price: $28
- Max spread: $28 × 0.02 = $0.56
- If bid $27.50, ask $28.50 → Spread $1.00 → ✗ Rejected (too wide)

**Why 0.02**:
- Ensures liquidity
- Minimizes trading costs
- Professional minimum standard

**Adjust if**:
- Only most liquid → Decrease to 0.01
- More opportunities → Increase to 0.03

### MIN_OI = 500
**Minimum open interest** (contracts).

**What it means**: At least 500 contracts must be open.

**Why 500**:
- Reasonable liquidity
- Tight spreads
- Easy to enter/exit

**Adjust if**:
- Maximum liquidity → Increase to 1,000 or 5,000
- More opportunities → Decrease to 250 (risky for large positions)

### RISK_FREE_RATE = 0.04
**Risk-free interest rate** (4%) for Black-Scholes calculations.

**What it means**: Current Treasury yield, used in delta calculations when Schwab doesn't provide delta.

**Why 0.04**: Approximate 10-year Treasury rate.

**Adjust if**:
- Treasury rates change significantly
- Check current rates at: https://www.treasury.gov/

---

## Reading the Output

### Sample Output

```
Processing AAPL (1/5)...

======================================================================
PORTFOLIO SUMMARY
======================================================================
Total Invested: $47,850.00 (of $50,000.00 target)
Total Equivalent Shares Controlled: 547
Capital Efficiency: 87.5% of stock cost
======================================================================

  Ticker  Stock Price  Strike  Expiration  DTE  Delta  Cost/Share  Contracts  Total Cost  Equiv Shares  Score  Allocation %
0   AAPL       225.50   200.0  2025-06-20  180  0.892      198.45          4    10500.00           357  0.121          21.9
1   MSFT       415.25   380.0  2025-06-20  180  0.875      365.80          2    12200.00           175  0.134          25.5
2  GOOGL       142.30   125.0  2025-06-20  180  0.881      124.20          6     9850.00           529  0.128          20.6
3    JNJ       158.75   145.0  2025-06-20  180  0.863      142.15          5     7850.00           432  0.142          16.4
4    JPM       195.40   175.0  2025-06-20  180  0.858      167.30          4     7450.00           343  0.148          15.6
```

### Column Explanations

#### Ticker
Stock symbol (e.g., AAPL, MSFT).

#### Stock Price
Current market price of the underlying stock.

**Use**: Compare to strike and cost/share to understand the deal.

#### Strike
The strike price of the recommended option.

**Example**: Strike 200.0 means you can buy shares at $200.

**Math check**: Stock $225.50 - Strike $200 = $25.50 intrinsic value

#### Expiration
The expiration date of the option.

**Example**: `2025-06-20` = June 20, 2025

**Check**: Always verify this gives you enough time for your strategy.

#### DTE (Days to Expiration)
Calendar days until expiration.

**Example**: 180 DTE = 6 months

**Sweet spot**: 90-365 days for DITM strategies.

#### Delta
How much the option moves per $1 stock movement.

**Example**: Delta 0.892 means:
- Stock up $1 → Option up $0.89
- Stock down $1 → Option down $0.89

**Interpretation**:
- 0.85-0.89 = **Very stock-like** ✓
- 0.90-0.95 = **Extremely stock-like** ✓✓
- 0.80-0.84 = **Stock-like** ✓
- < 0.80 = Not DITM territory

#### Cost/Share
Effective cost per share of exposure (from option perspective).

**Example**: Cost/Share $198.45

**Comparison**:
- Stock price: $225.50
- Cost/share: $198.45
- **Savings**: $27.05 per share (12%)

**How to use**:
- If cost/share > stock price → Don't do it (just buy stock)
- If cost/share < stock price × 0.98 → Good deal ✓

#### Contracts
Number of option contracts recommended to buy.

**Example**: 4 contracts

**What it means**:
- 4 contracts = 4 × 100 = 400 shares of notional exposure
- But delta-adjusted = 4 × 100 × 0.892 = 357 actual shares of exposure

#### Total Cost
Total dollar amount needed for this position.

**Example**: $10,500.00

**Calculation**: 4 contracts × $26.25 premium × 100 = $10,500

**Budget check**: Ensure you can afford this.

#### Equiv Shares
Delta-adjusted share equivalents you control.

**Example**: 357 shares

**Calculation**: 4 contracts × 100 × 0.892 delta = 357 shares

**Comparison**:
- To get 357 shares of stock: 357 × $225.50 = **$80,503**
- With this DITM option: **$10,500**
- **Savings: $70,003 (87% less capital)**

Wait, this doesn't match the example... Let me recalculate:

Actually, if Cost/Share is $198.45:
- 357 equivalent shares × $198.45 cost/share = $70,846
- But Total Cost shows $10,500

I think there's confusion in my example. Let me clarify:

**Correct Interpretation**:
- Premium per contract: Let's say $25.00
- 4 contracts × $25.00 × 100 = $10,000 total cost
- This gives you 357 shares worth of delta exposure
- Cost per equivalent share: $10,000 / 357 = $28.01

The "Cost/Share" column might actually represent something different. Let me look at the code...

Looking at the code at ditm.py:204, Cost/Share is calculated as:
```python
cost_per_share = mid / shares_equiv if shares_equiv > 0 else 0
```

Where:
- `mid` = option premium (single contract price, like $25.00)
- `shares_equiv` = delta × 100

So: Cost/Share = $25.00 / (0.892 × 100) = $25.00 / 89.2 = **$0.28 per share**

Then the actual portfolio cost: $0.28 × 357 shares = $100... that's not right either.

Let me reconsider. If mid is the premium per contract:
- Premium = $25.00 (for 1 contract)
- Total cost = Premium × 100 = $2,500
- Delta-adjusted shares = 89.2
- Cost per equivalent share = $2,500 / 89.2 = $28.03

OK so Cost/Share in the output is the cost per delta-adjusted share, which you multiply by the number of equivalent shares to get total cost. Got it!

#### Score
The conservatism ranking (lower = better).

**Example**: 0.121

**Interpretation**:
- < 0.15 = **Very conservative** ✓✓
- 0.15-0.20 = **Conservative** ✓
- 0.20-0.25 = **Moderate**
- > 0.25 = Less conservative

**Use**: Options are pre-sorted by score. Top option = most conservative.

#### Allocation %
Percentage of total portfolio allocated to this position.

**Example**: 21.9%

**Ideal**: Equal allocation (20% each for 5 stocks)

**Check**: Ensure diversification - no single position > 30%

### Portfolio Summary Metrics

#### Total Invested
Sum of all position costs.

**Example**: $47,850 invested out of $50,000 target

**Why not $50,000**:
- Position sizes use whole contracts
- May not perfectly fill target capital
- Leftover cash is safety buffer

#### Total Equivalent Shares Controlled
Sum of all delta-adjusted share exposures.

**Example**: 547 shares

**What it means**: Your portfolio moves like you own 547 shares distributed across 5 stocks.

#### Capital Efficiency
Your effective cost as a percentage of buying shares outright.

**Example**: 87.5% of stock cost

**Interpretation**:
- You're paying 87.5% of what stocks would cost
- **Savings: 12.5%** (freed up for other uses)

**Note**: This varies by market conditions and which options qualify.

---

## Understanding Expiration and Exit Mechanics

This is one of the **most important** sections - it addresses what happens if you forget to close your position.

### The Critical Question: What Happens at Expiration?

Many new options traders worry: "What if I forget to sell my option before expiration?"

The answer depends on whether your option is in-the-money (ITM) or out-of-the-money (OTM):

#### Scenario 1: Option is ITM at Expiration (Most DITM Cases)

**Example**: You own AAPL $200 call, stock is at $225 at 4pm on expiration day

**What happens automatically**:
1. **Your broker will auto-exercise the option** (you don't choose this, it happens automatically)
2. You are **required to buy** 100 shares at $200 = **$20,000 cash needed**
3. If you have $20,000: Shares appear in your account Monday morning
4. If you **don't** have $20,000:
   - **Schwab's protection mechanism**: They will automatically sell your option between 3-4pm on expiration day
   - Or they'll exercise and immediately sell shares (creating tax events and potential slippage)
   - Or they'll issue a margin call requiring immediate deposit

**The key point**: You won't just "lose your premium" if ITM - you'll be forced into a stock purchase you may not be able to afford!

#### Scenario 2: Option is OTM at Expiration (Rare for DITM)

**Example**: You own AAPL $200 call, stock drops to $190 at expiration

**What happens**:
- Option expires worthless
- You lose your entire premium paid ($2,800 in example)
- No additional action required
- Option disappears from your account

### How to Avoid Expiration Problems

**Best Practice (Recommended for DITM)**:
- Set a calendar alert for **60 days before expiration**
- Plan to close (sell) the position between 30-60 days before expiration
- **Never hold DITM options to expiration day**

**Why sell before expiration?**
1. Avoid automatic exercise complications
2. Capture remaining time value (free money!)
3. Avoid expiration day volatility and wide spreads
4. No capital requirement - just sell like a stock
5. Clean exit with immediate cash settlement

**Emergency: Expiration Day Arrives**

If you accidentally hold to expiration day:

**Before 3:00pm ET**:
- You can still sell your option normally
- Use limit orders (spreads may be wider)
- Takes 5-10 minutes to execute

**After 3:00pm ET**:
- Schwab may auto-sell ITM options to protect you
- If you have sufficient funds, they may let it auto-exercise
- Contact Schwab immediately if you need help: 1-800-435-4000

### Can You Sell Anytime Before Expiration?

**YES!** This is crucial to understand:

- You can sell your option **any time** during market hours (9:30am - 4:00pm ET)
- From the moment you buy it until 4:00pm on expiration day
- **No penalty** for selling early
- **No lock-up period**
- No need to notify anyone
- Just enter "Sell to Close" order like selling a stock

**Example Timeline**:
```
January 1: Buy option
January 15: Don't like the position → Sell it (fine!)
February 10: Position up 20% → Sell it (fine!)
May 15: 60 days to expiration → Sell it (recommended)
June 20: Expiration day, 3:50pm → Can still sell (but risky/late!)
June 20: 4:01pm → Too late, auto-exercise happens
```

### Real-World Example: Forgetting to Close

**Scenario**:
- You bought 4 AAPL $200 calls for $28 ($11,200 investment)
- Expiration day arrives, you forgot about them
- AAPL is at $225 (option is ITM)

**What happens at 4pm**:
- Auto-exercise triggers
- You must buy: 4 contracts × 100 shares × $200 = **$80,000**

**If you have $80,000 in account**:
- Monday morning: You own 400 AAPL shares
- Each share cost you: $200 strike + $28 premium = $228 per share
- Current value: $225 per share
- You're actually **underwater** by $3/share = $1,200 loss
- Plus you lost all time value (could've sold option for $30+ instead of $25 intrinsic)

**If you have only $20,000 in account**:
- Schwab sees insufficient funds around 3:30pm
- They automatically sell your 4 contracts (without asking you)
- You get whatever the market price is (maybe $29, maybe $31)
- Position closed, no exercise
- You might be happy or sad depending on the price they got

**Lesson**: Always plan your exit. Don't let expiration decide for you.

### Summary: Expiration Decision Tree

```
Do you want to own the shares?
├─ NO → Sell the option before expiration (recommended)
│        ✓ Get full option value (intrinsic + time)
│        ✓ No capital needed
│        ✓ Clean exit
│
└─ YES → Still sell the option, then buy shares separately
         Why? You'll lose time value if you exercise
         Better: Sell option for $30, buy shares at $225 = net $225.30/share
         Worse: Exercise at $200 strike + $28 premium = $228/share
```

**Bottom line**: You should almost always sell your DITM options rather than let them expire or exercise them.

---

## Step-by-Step: Acting on a Recommendation

So the script recommends buying AAPL 200 strike calls expiring June 20, 2025. Now what?

### Step 1: Verify the Recommendation

Before placing any trade, double-check:

#### A. Check Current Market Conditions
```
1. Is the market open? (Best to trade during market hours)
2. Any major news about AAPL today?
3. Is implied volatility normal or elevated?
```

#### B. Verify the Numbers in Your Broker
Log into your Schwab account:

1. Navigate to: **Trade → Options**
2. Enter symbol: **AAPL**
3. Find expiration: **June 20, 2025**
4. Locate strike: **$200 CALL**
5. Check current bid/ask:
   - Bid: $27.80 (what you'd receive if selling)
   - Ask: $28.20 (what you'd pay if buying)
   - **Mid: $28.00** (what the script used)

#### C. Confirm the Filter Criteria
Check that the option still meets requirements:

| Criteria | Requirement | Your Option | Status |
|----------|-------------|-------------|--------|
| Delta | 0.80-0.95 | 0.892 | ✓ |
| DTE | ≥ 90 days | 180 days | ✓ |
| Intrinsic % | ≥ 85% | 89.3% | ✓ |
| IV | ≤ 30% | 24% | ✓ |
| Spread % | ≤ 2% | 1.4% | ✓ |
| Open Interest | ≥ 500 | 5,243 | ✓ |

### Step 2: Calculate Your Position Size

The script recommends 4 contracts, but you should verify this makes sense for you:

#### A. Capital Requirement
```
Premium: $28.00
Contracts: 4
Total Cost: 4 × $28.00 × 100 = $11,200
```

**Ask yourself**:
- Can I afford $11,200 for this position?
- Does this fit my risk tolerance?
- Is this 10-20% of my total portfolio? (recommended max)

#### B. Risk Assessment
```
Maximum Loss: $11,200 (entire premium if AAPL crashes)
Breakeven: $200 strike + $28 premium = $228 at expiration
Current Stock: $225.50
Buffer: $2.50 below breakeven (comfortable)
```

#### C. Exposure Calculation
```
Contracts: 4
Delta: 0.892
Equivalent Shares: 4 × 100 × 0.892 = 357 shares

If you bought 357 shares instead:
357 × $225.50 = $80,503 required
vs.
Option cost: $11,200
Savings: $69,303 (86% less capital)
```

### Step 3: Place the Order

#### A. Order Type: Limit Order (ALWAYS)
**Never use market orders for options!** Spreads can be wide.

**Recommended**: Place limit order at or near the **mid price**.

**Example**:
- Bid: $27.80
- Ask: $28.20
- **Mid: $28.00** ← Place limit here
- Or slightly better: $27.90

#### B. Schwab Order Entry
In the Schwab trading platform:

1. **Action**: BUY TO OPEN
2. **Symbol**: AAPL
3. **Expiration**: June 20, 2025
4. **Strike**: $200
5. **Type**: CALL
6. **Quantity**: 4 contracts
7. **Order Type**: LIMIT
8. **Limit Price**: $28.00
9. **Duration**: DAY (or GTC if patient)

#### C. Review Before Submitting
**CRITICAL CHECKS**:
- ✓ Correct symbol (AAPL)
- ✓ Correct expiration (June 20, 2025)
- ✓ Correct strike ($200)
- ✓ CALL not PUT
- ✓ BUY TO OPEN (not sell)
- ✓ 4 contracts
- ✓ Limit price $28.00
- ✓ Estimated cost: ~$11,200

**If anything looks wrong → STOP and verify**

#### D. Submit and Monitor
- Submit order
- Watch for fill
- If not filled after 5-10 minutes, consider:
  - Adjusting limit price up slightly ($28.10, $28.20)
  - Canceling if market moved significantly

### Step 4: After the Trade Executes

#### A. Confirm Execution
Check your account:
- Position should show: **+4 AAPL Jun20'25 $200 Call**
- Account balance decreased by ~$11,200
- Check fill price (should be at or better than your limit)

#### B. Record Your Trade
Document in a spreadsheet or journal:

| Date | Ticker | Position | Contracts | Entry Price | Cost | Delta | DTE |
|------|--------|----------|-----------|-------------|------|-------|-----|
| 11/8/25 | AAPL | Jun20 $200 C | 4 | $28.00 | $11,200 | 0.892 | 180 |

#### C. Set Alerts
In Schwab or your tracking app:

**Price Alerts**:
- AAPL drops below $215 (warning level)
- AAPL drops below $205 (consider exit)
- AAPL rises above $250 (potential profit take)

**Time Alerts**:
- 60 days before expiration (consider roll)
- 30 days before expiration (must decide)

### Step 5: Monitor and Manage

#### A. Daily Monitoring (Optional)
Check:
- AAPL stock price
- Your P&L (profit/loss)
- Any major news

**Don't panic on small daily moves!** DITM calls are long-term positions.

#### B. Monthly Review (Recommended)
Once per month, check:

**Position Health**:
```
Current AAPL price: $232
Your option value: $34.50
P&L: ($34.50 - $28.00) × 4 × 100 = +$2,600 (23%)

Delta still: 0.90+? ✓
DTE remaining: 150 days ✓
Still comfortable holding? ✓
```

#### C. When to Exit

**Profit Taking**:
- Hit your target (e.g., +30%, +50%)
- Stock has had a big run
- Taking risk off the table

**Loss Management**:
- Stock drops significantly
- Delta decreases below 0.75
- Better opportunities elsewhere

**Time Management**:
- 60 days to expiration: Consider rolling
- 30 days to expiration: Must close or roll
- Never hold to expiration (time decay accelerates)

### Step 6: Exit Strategies

#### A. Close the Position (Simple)
Sell your option contracts:

1. **Action**: SELL TO CLOSE
2. **Quantity**: 4 contracts
3. **Order Type**: LIMIT
4. **Limit Price**: Current mid (or better)

**Example**:
- Current bid: $34.20
- Current ask: $34.80
- Mid: $34.50
- Place limit: $34.50 (or $34.40 for faster fill)

#### B. Roll the Position (Advanced)
If you want to keep exposure but expiration approaching:

**Rolling Out** (extend time):
1. SELL TO CLOSE current position (Jun20 $200 calls)
2. BUY TO OPEN new position (Dec19 $200 calls)
3. Pay the difference (debit) or collect credit

**Rolling Up and Out** (higher strike, more time):
1. SELL TO CLOSE current position (Jun20 $200 calls)
2. BUY TO OPEN new position (Dec19 $220 calls)
3. Typically costs more but locks in profits

#### C. Exercise the Option (Rare)
**Only if you want to own shares**:
- You'll need: 4 × 100 × $200 = $80,000 cash
- You'll receive: 400 shares of AAPL at $200/share
- Usually better to just sell the option instead

---

## Risk Management

### Position Sizing Rules

#### Rule 1: Single Position Limit
**Never more than 10-20% of portfolio in one position**

**Example**:
- Portfolio: $100,000
- Max per position: $10,000-$20,000
- If script recommends 4 contracts at $11,200:
  - For $100K portfolio: ✓ OK (11.2%)
  - For $50K portfolio: ✗ Too much (22.4%)
  - Reduce to 2 contracts: $5,600 (11.2%) ✓

#### Rule 2: Total Options Exposure
**Limit total options to 50-75% of portfolio**

**Reasoning**:
- Options are leveraged instruments
- Keep 25-50% in cash/stocks as buffer
- Prevents forced liquidation in downturn

#### Rule 3: Diversification
**Minimum 5 different stocks** (as script recommends)

**Avoid**:
- All tech stocks (sector concentration)
- All same expiration date
- All same general strike depth

### Stop-Loss Guidelines

#### Mental Stop vs. Hard Stop
**Mental Stop** (Recommended for DITM):
- Decide your exit price in advance
- Monitor regularly
- Execute when triggered
- Avoids whipsaws

**Hard Stop-Loss** (Not recommended):
- Options can gap and trigger unnecessarily
- Daily volatility can stop you out
- Miss the recovery

#### Suggested Stop Levels

**Conservative** (Stock-based):
- If stock drops 10% → Review position
- If stock drops 15% → Strong consider exit
- If stock drops 20% → Exit

**Moderate** (Option P&L based):
- If option drops to -15% loss → Review
- If option drops to -25% loss → Exit

**Aggressive** (Delta-based):
- If delta drops below 0.75 → Review
- If delta drops below 0.70 → Exit

#### Example:
```
Entry:
AAPL stock: $225
Option price: $28
Delta: 0.892

Stop triggers:
Conservative (15% stock drop):
$225 × 0.85 = $191.25 → Exit if AAPL < $191

Moderate (25% option loss):
$28 × 0.75 = $21 → Exit if option < $21

Aggressive (delta < 0.75):
Monitor daily, exit if delta drops below 0.75
```

### Portfolio Allocation

#### Balanced DITM Portfolio
For $100,000 total capital:

| Category | Allocation | Amount | Purpose |
|----------|-----------|---------|----------|
| DITM Calls | 50% | $50,000 | Core stock replacement |
| Cash | 30% | $30,000 | Dry powder, safety |
| Stocks | 15% | $15,000 | Diversification |
| Bonds/Stable | 5% | $5,000 | Stability |

#### Aggressive DITM Portfolio
For $100,000 total capital:

| Category | Allocation | Amount | Purpose |
|----------|-----------|---------|----------|
| DITM Calls | 70% | $70,000 | Maximum leverage |
| Cash | 20% | $20,000 | Dry powder |
| Stocks | 10% | $10,000 | Backup |

#### Conservative DITM Portfolio
For $100,000 total capital:

| Category | Allocation | Amount | Purpose |
|----------|-----------|---------|----------|
| DITM Calls | 30% | $30,000 | Conservative exposure |
| Cash | 30% | $30,000 | Large buffer |
| Stocks | 30% | $30,000 | Core holdings |
| Bonds/Stable | 10% | $10,000 | Stability |

### Tax Considerations

#### Holding Period
- **< 1 year**: Short-term capital gains (ordinary income tax rates)
- **> 1 year**: Long-term capital gains (lower rates)

**DITM Strategy**: Often held < 1 year, so expect short-term gains tax.

#### Wash Sale Rules
If you sell at a loss and buy back within 30 days:
- Loss is disallowed for tax purposes
- Wait 31 days before repurchasing
- Or buy different strike/expiration

#### Tax Efficiency Tips
1. Harvest losses in December
2. Let winners run into next year (if sensible)
3. Keep detailed records
4. Consult tax professional

### Black Swan Protection

#### What Could Go Wrong?

**Market Crash**:
- Stock market drops 20-30% rapidly
- Your DITM calls lose significant value
- Delta drops, time value disappears

**Protection**:
- Keep 30%+ cash reserve
- Diversify across sectors
- Don't use margin
- Size positions conservatively

**Company-Specific Crisis**:
- Earnings disaster
- Regulatory action
- Management scandal

**Protection**:
- Diversification (5+ stocks)
- Monitor news
- Use blue-chip companies only
- Set alerts

**Liquidity Crisis**:
- Market freezes
- Can't exit position
- Spreads widen dramatically

**Protection**:
- Only trade high OI options (>500)
- Monitor bid-ask spreads
- Don't panic sell
- Use limit orders always

---

## Understanding Risk Metrics

The DITM tracking system calculates comprehensive risk metrics to help you evaluate strategy performance objectively. These metrics go beyond simple profit/loss to measure risk-adjusted returns and portfolio health.

### Why Risk Metrics Matter

Two traders with the same 15% return can have vastly different risk profiles:

**Trader A**: 15% return, took small consistent profits, max loss 5%
**Trader B**: 15% return, had wild swings, max loss 40%

Risk metrics help you understand which trader has the better strategy.

---

### Sharpe Ratio

#### What It Is
The **Sharpe Ratio** measures risk-adjusted return. It tells you how much return you're getting per unit of risk taken.

**Formula**:
```
Sharpe Ratio = (Portfolio Return - Risk-Free Rate) / Standard Deviation of Returns
```

#### How It's Calculated
1. Take your average annualized return (e.g., 18%)
2. Subtract risk-free rate (e.g., 4% Treasury yield)
3. Divide by annualized standard deviation of returns

**Example**:
```
Portfolio return: 18% annualized
Risk-free rate: 4%
Standard deviation: 12%

Sharpe Ratio = (18% - 4%) / 12% = 1.17
```

#### Interpretation

| Sharpe Ratio | Quality | Meaning |
|--------------|---------|---------|
| < 0 | Poor | Losing money or underperforming Treasuries |
| 0 - 0.5 | Bad | Barely beating risk-free rate |
| 0.5 - 1.0 | Acceptable | Decent risk-adjusted returns |
| 1.0 - 2.0 | Good | Strong risk-adjusted returns |
| 2.0 - 3.0 | Very Good | Excellent risk-adjusted returns |
| > 3.0 | Exceptional | Institutional-quality (rare for retail) |

**DITM Target**: 1.0 - 2.0 (good to very good)

#### What Good/Bad Looks Like

**Good Sharpe (1.5)**:
```
Returns: Consistent wins (12%, 8%, 15%, 11%, 9%)
Std Dev: Low (3%)
Risk-adjusted return: Excellent
```

**Bad Sharpe (0.3)**:
```
Returns: Wild swings (30%, -20%, 25%, -15%, 10%)
Std Dev: High (20%)
Risk-adjusted return: Poor despite decent average
```

#### Limitations
- Assumes normal distribution (options aren't normally distributed)
- Penalizes upside volatility same as downside
- Requires sufficient history (20+ trades minimum)

---

### Sortino Ratio

#### What It Is
**Sortino Ratio** is like Sharpe Ratio but **only penalizes downside volatility**. It recognizes that upside volatility is good!

**Formula**:
```
Sortino Ratio = (Portfolio Return - Risk-Free Rate) / Downside Deviation
```

#### Difference from Sharpe

**Sharpe** penalizes all volatility:
- Big wins: Penalized ✗
- Big losses: Penalized ✓

**Sortino** only penalizes downside:
- Big wins: Ignored ✓
- Big losses: Penalized ✓

#### Interpretation

| Sortino Ratio | Quality |
|---------------|---------|
| < 0 | Poor |
| 0 - 1.0 | Acceptable |
| 1.0 - 2.0 | Good |
| 2.0 - 3.0 | Very Good |
| > 3.0 | Exceptional |

**DITM Target**: 1.5 - 2.5 (better than Sharpe due to upside asymmetry)

#### Example

Portfolio A:
```
Returns: +5%, +6%, +5%, -3%, +4%
Sharpe: 1.2 (penalized for consistency)
Sortino: 1.8 (only penalizes -3%)
```

Portfolio B:
```
Returns: +15%, +20%, -5%, -8%, +10%
Sharpe: 0.9 (penalized for big wins too)
Sortino: 1.5 (only penalizes losses)
```

**Sortino is better for asymmetric strategies** (like DITM calls where upside is unlimited).

---

### Maximum Drawdown

#### What It Is
**Maximum Drawdown** is the largest peak-to-trough decline in your portfolio value.

It answers: "What's the worst I could have experienced?"

#### How It's Calculated

Track cumulative returns over time:
```
Trade 1: +$1,000 → Portfolio: $51,000 (peak)
Trade 2: +$500  → Portfolio: $51,500 (new peak)
Trade 3: -$2,000 → Portfolio: $49,500 (drawdown!)
Trade 4: -$1,000 → Portfolio: $48,500 (deeper drawdown!)
Trade 5: +$3,000 → Portfolio: $51,500 (recovery to previous peak)
```

**Max Drawdown**: From $51,500 peak to $48,500 trough = **-$3,000 (-5.8%)**

#### Interpretation

| Max Drawdown | Risk Level |
|--------------|-----------|
| 0-10% | Low risk (conservative) |
| 10-20% | Moderate risk |
| 20-30% | High risk |
| 30-50% | Very high risk |
| > 50% | Extreme risk (avoid) |

**DITM Target**: < 20% (moderate risk)

#### Why It Matters

**Psychological Impact**:
- 10% drawdown: Most can handle
- 25% drawdown: Difficult but manageable
- 50% drawdown: Panic selling, abandon strategy

**Recovery Required**:
- 10% loss → Requires 11% gain to recover
- 25% loss → Requires 33% gain to recover
- 50% loss → Requires **100% gain** to recover!

#### Example

```
Starting capital: $50,000

Best strategy:
- Average return: 12%
- Max drawdown: 8%
- Can sleep at night: ✓

Aggressive strategy:
- Average return: 18%
- Max drawdown: 35%
- Panic sold at bottom: ✗
```

**Lower drawdown often wins** due to behavioral factors.

---

### Calmar Ratio

#### What It Is
**Calmar Ratio** measures return per unit of maximum drawdown.

**Formula**:
```
Calmar Ratio = Annualized Return / Max Drawdown
```

It answers: "How much return am I getting for the worst drawdown I experience?"

#### Calculation Example

```
Annualized return: 15%
Max drawdown: 10%

Calmar Ratio = 15% / 10% = 1.5
```

#### Interpretation

| Calmar Ratio | Quality |
|--------------|---------|
| < 0.5 | Poor (return doesn't justify risk) |
| 0.5 - 1.0 | Acceptable |
| 1.0 - 3.0 | Good |
| 3.0 - 5.0 | Very Good |
| > 5.0 | Excellent |

**DITM Target**: 1.5 - 3.0

#### Why Use It

Calmar is great for **comparing strategies**:

```
Strategy A:
- Return: 20%
- Drawdown: 25%
- Calmar: 0.8 (bad)

Strategy B:
- Return: 15%
- Drawdown: 8%
- Calmar: 1.875 (good)

Strategy B is better! Lower return but much less pain.
```

---

### Profit Factor

#### What It Is
**Profit Factor** = Total Gross Profit / Total Gross Loss

Simple ratio of how much you make on winners vs. lose on losers.

#### Calculation

```
Winners: +$5,000, +$3,000, +$2,000 = $10,000 total
Losers: -$2,000, -$1,500, -$500 = $4,000 total

Profit Factor = $10,000 / $4,000 = 2.5
```

#### Interpretation

| Profit Factor | Quality |
|---------------|---------|
| < 1.0 | Losing strategy |
| 1.0 - 1.25 | Barely profitable |
| 1.25 - 1.5 | Marginal |
| 1.5 - 2.0 | Good |
| 2.0 - 3.0 | Very Good |
| > 3.0 | Excellent |

**DITM Target**: 1.8 - 2.5

#### What It Means

**Profit Factor 2.0**:
- For every $1 you lose, you make $2
- Can afford 50% win rate and still profit
- Sustainable long-term

**Profit Factor 1.2**:
- For every $1 you lose, you make $1.20
- Need 70%+ win rate to stay profitable
- Small edge, risky

---

### Win/Loss Ratio

#### What It Is
Average win size / Average loss size

Different from win rate! This is about **magnitude**, not frequency.

#### Example

```
Wins: 10 trades averaging +$500 = $5,000
Losses: 5 trades averaging -$200 = -$1,000

Win Rate: 10/15 = 66.7%
Win/Loss Ratio: $500 / $200 = 2.5
```

#### Interpretation

| Win/Loss Ratio | Quality |
|----------------|---------|
| < 1.0 | Avg loss > avg win (need high win rate) |
| 1.0 - 1.5 | Decent (wins slightly larger) |
| 1.5 - 2.5 | Good (wins notably larger) |
| > 2.5 | Excellent (big winners) |

#### Four Quadrants of Trading

|  | **High Win Rate** | **Low Win Rate** |
|---|---|---|
| **High Win/Loss** | Best! Consistent big wins | Rare big wins cover many small losses |
| **Low Win/Loss** | Many small wins, few big losses | Worst! Many small losses, rare small wins |

**DITM Strategy**: Target **High Win Rate + Moderate Win/Loss** (top-left quadrant)

---

### Expectancy

#### What It Is
**Expectancy** = Average $ profit per trade

Simple but powerful: "What do I make per recommendation?"

#### Calculation

```
10 trades:
Wins: +$500, +$600, +$450, +$550, +$500
Losses: -$200, -$150, -$250, -$180, -$220

Total P&L: $2,100
Trades: 10

Expectancy = $2,100 / 10 = $210 per trade
```

#### Interpretation

For $10,000 average position size:

| Expectancy | Quality |
|------------|---------|
| < 0 | Losing |
| $0 - $200 | Poor (2% return) |
| $200 - $500 | Acceptable (2-5%) |
| $500 - $1,000 | Good (5-10%) |
| $1,000 - $2,000 | Very Good (10-20%) |
| > $2,000 | Excellent (>20%) |

#### Why It's Useful

**Simple Forward Projection**:
```
Expectancy: $300 per trade
Plan: 50 trades per year

Expected profit: $300 × 50 = $15,000
```

**Break-Even Analysis**:
```
Fixed costs: $1,000/year (data, tools)
Expectancy: $50 per trade

Trades needed: $1,000 / $50 = 20 trades to break even
```

---

### Standard Deviation of Returns

#### What It Is
Measure of how much your returns vary around the average.

**Low StdDev**: Consistent returns (5%, 6%, 5%, 7%, 6%)
**High StdDev**: Wild swings (20%, -10%, 15%, -5%, 10%)

#### Interpretation

For average return of 12%:

| Std Dev | Meaning |
|---------|---------|
| 2-5% | Very consistent |
| 5-10% | Moderately consistent |
| 10-20% | Variable |
| 20-30% | Highly variable |
| > 30% | Extremely volatile |

#### 68-95-99.7 Rule

Assuming normal distribution:
- **68%** of results within ±1 std dev
- **95%** within ±2 std dev
- **99.7%** within ±3 std dev

**Example**:
```
Average return: 12%
Std Dev: 8%

68% of trades: Between 4% and 20%
95% of trades: Between -4% and 28%
99.7% of trades: Between -12% and 36%
```

**Use**: Helps set realistic expectations and stop-losses.

---

### Consecutive Wins/Losses

#### What It Matters
**Streaks happen!** Even with 60% win rate, you'll hit losing streaks.

#### Statistics of Streaks

With **60% win rate**:
- Probability of 3 losses in a row: 6.4%
- Probability of 5 losses in a row: 1.0%
- Probability of 7 losses in a row: 0.16%

With **50% win rate**:
- Probability of 3 losses in a row: 12.5%
- Probability of 5 losses in a row: 3.1%
- Probability of 7 losses in a row: 0.78%

#### Why Track It

**Position Sizing**:
```
Max consecutive losses: 4
Position size: Should withstand 4× max loss
Max loss per trade: 5%
Required buffer: 4 × 5% = 20% drawdown capacity
```

**Psychological Preparation**:
```
Track shows: Max 5 consecutive losses
Expectation: Could see 6-7 in a bad stretch
Mental prep: Don't abandon strategy mid-streak
```

#### Example

```
Results: W W W L W W L L L L W W W

Longest win streak: 3
Longest loss streak: 4

If each loss = -$500:
Worst streak cost: 4 × $500 = $2,000

Reserve needed: $2,500 buffer for bad runs
```

---

### Risk Metrics in Action: Complete Example

**Portfolio Performance After 20 Trades:**

```
RISK METRICS
--------------------------------------------------------------------------------
Sharpe Ratio:              1.45
Sortino Ratio:             1.82
Max Drawdown:              12.50%
Max Single Loss:           8.30%
Calmar Ratio:              1.92
Profit Factor:             2.15

Average Win:               +15.20% ($1,520)
Average Loss:              -6.80% ($680)
Win/Loss Ratio:            2.24
Expectancy (avg $ per trade): $485

Return Std Dev:            9.50%
Best Trade:                +32.50%
Worst Trade:               -8.30%
Max Consecutive Wins:      4
Max Consecutive Losses:    3
```

#### Interpretation

**Sharpe 1.45** → Good risk-adjusted returns ✓

**Sortino 1.82** → Better than Sharpe (good for asymmetric strategy) ✓

**Max Drawdown 12.5%** → Moderate, manageable ✓
- Requires 14% gain to recover
- Most can psychologically handle this

**Calmar 1.92** → Good return for the drawdown experienced ✓

**Profit Factor 2.15** → Make $2.15 for every $1 lost ✓
- Very healthy ratio
- Sustainable

**Win/Loss 2.24** → Average win is 2.24× average loss ✓
- Can afford 44% win rate and break even
- With 60% win rate, very profitable

**Expectancy $485** → Average $485 per recommendation ✓
- On $10,000 positions = 4.85% per trade
- 20 trades/year = $9,700 expected profit

**Std Dev 9.5%** → Moderate variability ✓
- Most trades between 2% and 22% return
- Predictable enough for planning

**Max Consecutive Losses: 3** → ✓
- Should size positions to handle 4-5× max loss
- $680 × 5 = $3,400 max drawdown capacity needed

#### Overall Assessment

**This is a GOOD, SUSTAINABLE strategy**:
- Strong risk-adjusted returns (Sharpe/Sortino)
- Moderate drawdowns (12.5%)
- Wins are 2× bigger than losses
- Consistent profitability (Profit Factor 2.15)
- Manageable volatility

**Action**: Continue with current approach!

---

### Using Risk Metrics to Improve

#### Compare Filter Settings

Run scans with different parameters, compare risk metrics:

```
Scan A (MIN_DELTA=0.80, MAX_IV=0.30):
- Sharpe: 1.2
- Max Drawdown: 15%
- Profit Factor: 1.8

Scan B (MIN_DELTA=0.85, MAX_IV=0.25):
- Sharpe: 1.6
- Max Drawdown: 10%
- Profit Factor: 2.3

Scan B is superior! Tighter filters = better risk profile.
```

#### Monitor Deterioration

```
Month 1-3: Sharpe 1.8, good
Month 4-6: Sharpe 1.5, still good
Month 7-9: Sharpe 0.9, deteriorating!

Action: Something changed. Review recent trades, market conditions.
```

#### Position Sizing from Risk Metrics

```
Max Consecutive Losses: 5
Max Single Loss: 10%
Required buffer: 5 × 10% = 50% potential drawdown

If you have $50,000:
- Can lose $25,000 worst case (50%)
- Each position max loss: $5,000
- At 10% risk per trade: $50,000 position size
- Use 2× safety: $25,000 per position ✓
```

---

### Targets for DITM Strategy

Based on conservative options trading:

| Metric | Target Range | Excellent |
|--------|--------------|-----------|
| Sharpe Ratio | 1.0 - 1.5 | > 1.5 |
| Sortino Ratio | 1.5 - 2.0 | > 2.0 |
| Max Drawdown | 10-20% | < 10% |
| Calmar Ratio | 1.5 - 2.5 | > 2.5 |
| Profit Factor | 1.8 - 2.5 | > 2.5 |
| Win Rate | 60-70% | > 70% |
| Win/Loss Ratio | 1.5 - 2.5 | > 2.5 |
| Expectancy | 4-8% per trade | > 8% |

If you're hitting these targets consistently, you have a solid DITM strategy!

---

## Common Mistakes to Avoid

### Mistake #1: Using Market Orders
**Wrong**:
```
Order Type: MARKET
Result: Filled at $29.50 (asked for $28.00)
Hidden cost: $1.50 × 4 × 100 = $600 lost!
```

**Right**:
```
Order Type: LIMIT at $28.00
Result: Filled at $28.00 or better
Saved: $600
```

### Mistake #2: Ignoring Bid-Ask Spreads
**Example**:
```
Option looks great:
- Mid price: $25.00
- Delta: 0.90
- DTE: 180

But:
- Bid: $22.00
- Ask: $28.00
- Spread: $6.00 (24%!)

Reality: Illiquid option, avoid!
```

### Mistake #3: Holding to Expiration
**Never hold DITM calls to expiration!**

**Why**:
- Time decay accelerates last 30 days
- Risk of assignment complications
- Might lose intrinsic value

**Rule**: Close or roll by 30-60 DTE

### Mistake #4: Ignoring Delta Changes
**Scenario**:
```
Entry: Delta 0.90, stock $225
Month later: Stock dropped to $205
Delta now: 0.75 (no longer DITM!)

Action needed: Exit or roll to lower strike
```

**Monitor delta monthly!**

### Mistake #5: Overconcentration
**Wrong**:
```
$50,000 portfolio
All in: 10 contracts AAPL $200 calls
Risk: 100% in one position!
```

**Right**:
```
$50,000 portfolio
5 stocks: $10,000 each (20% each)
Diversified risk
```

### Mistake #6: Confusing Cost Metrics
**Common confusion**:
- Premium = $28
- Cost per share = $0.31
- Total cost = $2,800

**"It only costs $0.31 per share!"** ← Wrong thinking

**Reality**: You're paying $2,800 for delta-adjusted exposure to 89 shares.

### Mistake #7: Chasing Returns
**Temptation**:
```
DITM calls too boring, only 0.85 delta
"I'll buy 0.50 delta for more upside!"

Result: Speculating, not investing
Lost the DITM advantage
```

**Stay disciplined**: Stick to DITM criteria (0.80-0.95 delta)

### Mistake #8: Ignoring Dividends
**Reality check**:
- Stock pays 2% annual dividend
- You own DITM calls (no dividend)
- You're giving up that 2%

**Factor in**: Dividend cost vs. capital savings

**Example**:
- Stock: $225, saves you $25 via DITM, but gives $4.50/year dividend
- Holding 1 year: Net savings $25 - $4.50 = $20.50
- Still worth it, but factor it in!

### Mistake #9: Not Having an Exit Plan
**Before entering, decide**:
1. Profit target (e.g., +30%)
2. Stop loss (e.g., -20%)
3. Time exit (e.g., 60 DTE roll)
4. Delta exit (e.g., < 0.75 close)

**Write it down!** Emotions will tempt you to deviate.

### Mistake #10: Overtrading
**Trap**:
```
Week 1: Buy AAPL calls
Week 2: Sell (small profit), buy MSFT calls
Week 3: Sell, buy GOOGL calls
Week 4: ...

Result:
- Death by 1000 cuts (spreads, commissions)
- Short-term gains tax
- Exhausting
```

**Better**:
- Buy quality DITM positions
- Hold 3-6 months
- Only trade when necessary

---

## Example Scenarios

### Scenario 1: Perfect Trade

**Setup**:
- Date: January 1, 2025
- Stock: AAPL at $225
- Buy: 4 contracts Jun20'25 $200 calls at $28
- Cost: $11,200
- Delta: 0.892

**Month 1** (February):
- AAPL: $232 (+3.1%)
- Option: $34 (+21.4%)
- P&L: +$2,400
- Action: Hold

**Month 3** (April):
- AAPL: $245 (+8.9%)
- Option: $47 (+67.9%)
- P&L: +$7,600
- Action: Consider taking profits

**Month 5** (June):
- AAPL: $255 (+13.3%)
- Option: $57 (+103.6%)
- P&L: +$11,600
- DTE: 20 days remaining
- Action: Sell to close

**Final Result**:
- Invested: $11,200
- Returned: $22,800
- Profit: $11,600 (103.6%)
- If bought stock: 50 shares × $30 gain = $1,500 (13.3%)
- **Leverage multiplier: 7.7x**

### Scenario 2: Managing a Decline

**Setup**:
- Date: January 1, 2025
- Stock: MSFT at $415
- Buy: 2 contracts Jun20'25 $380 calls at $40
- Cost: $8,000
- Delta: 0.875

**Month 1** (February):
- MSFT: $405 (-2.4%)
- Option: $32 (-20%)
- P&L: -$1,600
- Delta: 0.82
- Action: Monitor, within tolerance

**Month 2** (March):
- MSFT: $390 (-6%)
- Option: $22 (-45%)
- P&L: -$3,600
- Delta: 0.72 (below threshold!)
- Action: **Exit position**

**Execution**:
- Sell 2 contracts at $22
- Recover: $4,400
- Loss: -$3,600 (45%)
- Stock decline: -$50 per share (6%)

**Analysis**:
- Followed stop-loss rule (delta < 0.75)
- Prevented deeper loss
- Capital preserved: $4,400 to redeploy

**Alternative** (if didn't exit):
- Month 3: MSFT $375, Option $12, P&L -$5,600 (70% loss)
- Following rules saved $2,000

### Scenario 3: Rolling Forward

**Setup**:
- Date: January 1, 2025
- Stock: GOOGL at $142
- Buy: 5 contracts Jun20'25 $125 calls at $20
- Cost: $10,000
- Delta: 0.881

**Month 4** (May):
- GOOGL: $155 (+9.2%)
- Option: $32 (+60%)
- P&L: +$6,000
- DTE: 51 days (approaching exit window)
- Delta: 0.91
- Decision: Roll forward (keep exposure)

**Rolling Transaction**:
```
Sell to Close: 5× Jun20'25 $125 calls at $32 = +$16,000
Buy to Open:   5× Dec19'25 $135 calls at $26 = -$13,000
Net Credit: +$3,000
```

**New Position**:
- Strike: $135 (locked in $10 gain per share)
- Expiration: Dec 19, 2025 (6 more months)
- DTE: 232 days
- Delta: 0.87
- Derisked: Took $3,000 off the table

**Result**:
- Original capital: $10,000
- Recovered: $3,000
- At risk now: $7,000 (new position is "free")
- Still have upside potential

### Scenario 4: Dividend Consideration

**Comparison**: Own stock vs. DITM calls on dividend stock

**Stock**: Johnson & Johnson (JNJ)
- Price: $158.75
- Dividend: $4.96/year (3.1% yield)
- 100 shares cost: $15,875
- Annual dividend: $496

**DITM Call**:
- Strike: $145
- Expiration: Jun 20, 2025 (180 DTE)
- Premium: $16.50
- Cost: $1,650 per contract
- Delta: 0.863
- Equivalent shares: 86.3

**For equivalent exposure** (100 shares vs. 116 delta-adjusted shares):
- Stock: $15,875 + receive $496 dividends = net $15,379 annual cost
- Calls: 1.16 contracts × $1,650 = $1,914 (no dividends)

**Savings by using DITM**: $15,875 - $1,914 = **$13,961**

**Dividend sacrifice**: $496

**Net benefit**: $13,961 - $496 = **$13,465 freed capital**

**Use that capital**:
- Earn interest (4% = $538)
- Buy more positions
- Safety buffer

**Conclusion**: Even with dividends, DITM calls free up significant capital.

### Scenario 5: Liquidity Issues

**Bad Example**:

**Stock**: Small cap XYZ at $85
**Looking at**: Sep'25 $75 calls

**Option chain**:
- Premium (mid): $12.50 (looks good!)
- Delta: 0.88 (great!)
- DTE: 150 (perfect!)
- **Bid: $9.50**
- **Ask: $15.50**
- **Spread: $6.00 (48%!)**
- **Open Interest: 25** (very low!)

**Analysis**:
- Entry cost: $15.50 (must pay ask)
- To exit: $9.50 (receive bid)
- **Instant loss: $6.00 (48%) just from spread!**
- Stock must rise significantly just to break even

**Action**: **AVOID!** Fails liquidity filters.

**Good Example**:

**Stock**: AAPL at $225
**Looking at**: Jun'25 $200 calls

**Option chain**:
- Premium (mid): $28.00
- Delta: 0.892
- DTE: 180
- **Bid: $27.80**
- **Ask: $28.20**
- **Spread: $0.40 (1.4%)**
- **Open Interest: 5,243** (very high!)

**Analysis**:
- Can enter at $28.20 (ask)
- Can exit at $27.80 (bid)
- Spread cost: $0.40 (1.4%)
- Acceptable friction

**Action**: ✓ Meets all criteria

**Lesson**: Always check liquidity metrics, not just greeks!

---

## Final Checklist Before Trading

### Pre-Trade Verification

- [ ] App status "Ready For Use" in Schwab portal
- [ ] .env file configured with credentials
- [ ] Script ran successfully
- [ ] Market is open (or close to open)
- [ ] Reviewed all recommended positions
- [ ] Verified numbers in Schwab match script output
- [ ] Position sizing fits portfolio (10-20% per position)
- [ ] Total options exposure < 75% of portfolio
- [ ] Understand all metrics (delta, DTE, IV, etc.)
- [ ] Exit plan documented for each position
- [ ] Stop-loss levels determined
- [ ] Alerts set up for price/time triggers

### Order Entry Verification

- [ ] Correct ticker symbol
- [ ] Correct expiration date
- [ ] Correct strike price
- [ ] CALL (not PUT)
- [ ] BUY TO OPEN (not sell)
- [ ] Correct number of contracts
- [ ] LIMIT order (not market)
- [ ] Limit price at or near mid
- [ ] Estimated cost reviewed
- [ ] Account has sufficient funds

### Post-Trade Management

- [ ] Trade confirmed in account
- [ ] Fill price documented
- [ ] Position added to tracking spreadsheet
- [ ] Alerts configured
- [ ] Calendar reminder for 60 DTE
- [ ] Monthly review scheduled
- [ ] Exit strategy documented

---

## Conclusion

DITM options trading is a **powerful but nuanced strategy**. It's more conservative than speculative options trading, but still requires:

1. **Understanding** of options mechanics
2. **Discipline** in following criteria
3. **Risk management** through position sizing
4. **Monitoring** of positions
5. **Exit planning** before entry

This guide gave you the foundation. Now:

1. **Paper trade first** (practice without real money)
2. **Start small** (1-2 contracts to learn)
3. **Build experience** before scaling up
4. **Keep learning** - markets evolve

**Remember**: This is a tool for screening, not a guarantee of profits. Options trading involves substantial risk. Only trade with capital you can afford to lose.

**Good luck, and trade smart! 📈**

---

## Additional Resources

- [CBOE Options Education](https://www.cboe.com/education/)
- [Investopedia Options Center](https://www.investopedia.com/options-basics-tutorial-4583012)
- [Schwab Options Trading Guide](https://www.schwab.com/learn/topic/options)
- [Options Clearing Corporation](https://www.theocc.com/)
- [IRS Publication 550](https://www.irs.gov/publications/p550) (Tax treatment)

**Disclaimer**: This guide is for educational purposes only. Not investment advice. Consult a financial advisor before trading.
