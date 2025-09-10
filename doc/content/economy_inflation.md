# Solana/Economic System/Inflation Rewards

According to the original design, the Solana network issues new tokens through a predetermined inflation mechanism, with these new tokens being proportionally distributed to the foundation, validators, and delegators. The inflation rate starts at an initial 8%, decreases by 15% annually, with the goal of long-term stabilization at 1.5%. The Solana Foundation receives a fixed 5% of inflation until it has been continuously receiving it for 7 years.

You can query Solana's current inflation rate in real-time through RPC. At the current time point, the inflation rate is `0.04317705363505517`. Additionally, you can see that the `foundation` value is `0.0`, meaning the foundation is no longer receiving the default 5% of inflation, even though the 7-year period has not been completed.

```py
import pxsol

pxsol.config.current = pxsol.config.mainnet
print(pxsol.rpc.get_inflation_rate())

# {
#   'epoch': 842,
#   'foundation': 0.0,
#   'total': 0.04317705363505517,
#   'validator': 0.04317705363505517,
# }
```

You can find the parameters for Solana's inflation rate at [https://github.com/anza-xyz/solana-sdk/blob/9decd857f019cc4c8dd89f4b3811ea56b0ac5c8e/inflation/src/lib.rs#L30-L34](https://github.com/anza-xyz/solana-sdk/blob/9decd857f019cc4c8dd89f4b3811ea56b0ac5c8e/inflation/src/lib.rs#L30-L34). Unfortunately, I haven't found specific information about when the Solana Foundation reward was changed from 5% to 0%, but I suspect it was implemented after a vote by the Solana validator community. The specific timing was likely before relevant forums and websites were established, such as some vote in 2021 or 2022.

Solana's inflation rate is based on a fixed initial inflation rate that decreases by a certain percentage annually until it reaches the long-term target inflation rate. The specific formula is as follows:

```txt
Iₜ=max(I₀×(1−r)ᵗ, Iₑ)
```

Where:

- `Iₜ`: Inflation rate in year t
- `I₀`: Initial inflation rate (8%)
- `Iₑ`: Target inflation rate (1.5%)
- `r`: Annual reduction rate (15%)
- `t`: Time (in years, calculated from the start of the inflation mechanism)

The inflation rate determines the amount of new SOL tokens added each year. Based on the current circulating supply, multiplying by the inflation rate gives the number of new tokens for that year.

Q: Assuming the total supply in 2025 is 600 million SOL, with an inflation rate Iₜ=4.3%, what is the estimated number of new tokens for that year?

A: `600000000 × 0.043 = 25800000`.

It's important to note that Solana's inflation is calculated based on total supply, not circulating supply. This means that even if some tokens are locked or not in circulation, they are still included in the inflation calculation. This helps ensure the long-term stability and security of the network, as more tokens are allocated to validators and stakers to incentivize them to maintain the network. However, this also makes the actual impact of inflation more complex, as the number of tokens in circulation may differ significantly from the total supply.

Additionally, in actual operation, Solana does not calculate inflation rates and distribute rewards based on real-world "years." Solana's fundamental time unit is the epoch, which typically lasts about 2-3 days (in most cases you can roughly consider it as 2 days). Each epoch contains a certain number of slots (time slots), usually about 432,000 slots. Inflation rewards are distributed to validators and stakers at the end of each epoch.
