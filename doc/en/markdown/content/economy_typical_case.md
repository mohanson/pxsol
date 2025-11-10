# Solana/Economic System/Typical Case Analysis

This section briefly discusses economic systems on blockchains. For most blockchain projects, the economic system is their foundation. If the system is cleverly designed, it can indeed support long-term rapid development of the project; if it's carelessly designed, the project can only become fertilizer for others to flourish.

**Steem Inflation and Governance Crisis 2016–2020**

Steem is a decentralized social media platform based on blockchain, where users can earn cryptocurrency rewards for creating or curating (such as liking and commenting) quality content. Steem had approximately 9% annual token inflation, with most distributed through [proof-of-brain](https://steem.com/steem-bluepaper.pdf) mining to reward content creators and token holders. However, due to high inflation causing strong selling pressure and the reward distribution mechanism being manipulated by a few whales, community confidence declined, tokens fell long-term, active users decreased, and it was eventually acquired by Tron founder Justin Sun, triggering a governance war.

**BitConnect Collapse 2018**

BitConnect was a high-yield investment project. It promised to provide investors with up to 1% daily returns (approximately 40% monthly compound interest) through lending programs and proprietary trading bots that allegedly profited from cryptocurrency market volatility. In reality, the so-called profits actually came from new user funds, constituting a Ponzi economic model. After regulatory intervention, the platform shut down, tokens went to zero within days, and investors suffered heavy losses.

**EOS Resource Model Failure 2018–2021**

EOS was arguably the most anticipated project of 2018: everyone was wondering if it would be another Ethereum. It designed a mechanism where users needed to stake EOS to obtain computational resources to use on-chain applications. Under this design, due to extreme volatility in on-chain computational resource prices, user experience was terrible. Regular users could hardly transact during peak periods, leading to massive application exodus. The final result was EOS price continuing to decline. The author was also among those who bought into EOS at the time, ultimately seeing their EOS assets shrink by 100x.

**Terra / UST Collapse 2022**

There's a common saying in the crypto world: the most unstable thing in the world is algorithmic stablecoins.

Terra was an algorithmic stablecoin project. So-called algorithmic stablecoins refer to "using some clever algorithm to ensure tokens maintain a one-to-one correspondence with the US dollar". Specifically, Terra's USD stablecoin UST maintained its $1 peg through the minting and burning of LUNA, relying on arbitrageurs to balance the price. However, the problem was that when market confidence collapsed, the arbitrage mechanism couldn't prevent LUNA from being infinitely minted, ultimately entering a "death spiral". The author was fortunate enough to witness its moment of collapse to zero. It happened at night, and by the next morning, its price had fallen from over $100 to near zero.

From these cases, we can see several common pitfalls in failed blockchain economic system designs:

- Excessive inflation causes long-term selling pressure, making price stability difficult
- Single-dimensional incentive structures lead users to come only for rewards, leaving when rewards stop
- Over-reliance on market regulation, easily failing during extreme market conditions
- Ponzi structures, completely dependent on new funds subsidizing old funds
- The most bizarre failure mode is when system design has no major flaws, but poor user experience results in no usage
