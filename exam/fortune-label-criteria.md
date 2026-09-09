# Why the Fortune Labels Use These Attempt Ranges

The current fortune labels classify how unusual the number of bogo-sort attempts is for six items. The boundaries are based on cumulative percentiles of the examination results, not on arbitrary attempt counts.

The explanation below reconstructs the rule from the current implementation, the earlier N=5 implementation, and the examination data recorded in the repository. The commit that changed the list length from five to six does not state the rationale in its message, so the design interpretation is evidence-based rather than a quotation from the original author.

## Current classification

The rules are implemented in [`fortune_label()`](../luck.py#L92-L109).

| Attempts | Label | Approximate cumulative percentile | Interpretation |
| ---: | --- | ---: | --- |
| `1` | `extremely_lucky` | 0.14% | The items were sorted by the first shuffle. |
| `2`–`37` | `very_lucky` | up to 5% | The result is in roughly the luckiest 5%. |
| `38`–`161` | `lucky` | up to 20% | The result is in roughly the luckiest 20%. |
| `162`–`311` | `a_bit_lucky` | up to 35% | The result is better than the central range. |
| `312`–`755` | `ordinal` | up to 65% | The central, ordinary range. |
| `756`–`1,157` | `a_bit_unlucky` | up to 80% | The result is below the central range but not yet unusual. |
| `1,158`–`2,154` | `unlucky` | up to 95% | The result is between roughly the 80th and 95th percentiles. |
| `2,155`–`5,000` | `very_unlucky` | up to 99.9% | The result is in the upper tail of the distribution. |
| `>5,000` | `extremely_unlucky` | remaining roughly 0.1% | Sorting did not succeed within the configured limit. |

The first attempt is separated from `very_lucky` because success on the first shuffle is a distinct event: its theoretical probability is only about 0.14%. The `ordinal` range covers the middle 30% between the 35th and 65th percentiles. The other ordinary labels are arranged in approximately 15-percentage-point bands around it.

## Why six items produce these numbers

With six distinct items, exactly one of the `6! = 720` permutations is sorted. If each shuffle is independent and uniformly distributed, the probability of success on one attempt is:

```text
p = 1 / 720
```

The probability of succeeding within `k` attempts is therefore:

```text
P(attempts <= k) = 1 - (719 / 720)^k
```

The current boundaries are close to the attempt counts at the 5%, 20%, 35%, 65%, 80%, and 95% cumulative points of this distribution. The upper boundary of 5,000 is also meaningful: the probability of still not succeeding after 5,000 attempts is about 0.096%, which is approximately the final 0.1% tail.

The examination is finite and uses implementation-specific random-number generators, so measured values vary by a few attempts. For example, the examination data at the repository state where the N=6 rules were introduced contained these values:

| Cumulative percentile | Attempts in recorded data | Current label boundary |
| ---: | ---: | ---: |
| 5.0% | 37 | `37` |
| 20.0% | 161 | `161` |
| 35.0% | 311 | `311` |
| 65.0% | 755 | `755` |
| 80.0% | 1,157 | `1,157` |
| 95.0% | 2,154 | `2,154` |

The exact match indicates that these recorded values were used for the hard-coded boundaries. A later run can produce nearby values in `exam/exam_data.txt`; the label rules do not change automatically when the examination is rerun.

## Why the rules changed from N=5 to N=6

The original N=5 implementation used these percentile-oriented comments and boundaries:

| Label | N=5 boundary | Intended cumulative point |
| --- | ---: | ---: |
| `very_lucky` | `7` | about 5% |
| `lucky` | `27` | about 20% |
| `normal` | `109` | about 60% |
| `a_bit_unlucky` | `165` | about 75% |
| `unlucky` | `274` | about 90% |
| `very_unlucky` | `600` | near the upper limit |

When the sorted list changed from five items to six in commit `c5e49f3` (`change length of list to be sorted: 5 -> 6`), the success probability for each shuffle dropped from `1 / 5!` to `1 / 6!`. The old attempt counts therefore no longer represented the same rarity. The thresholds were replaced with the N=6 examination values, and the middle of the scale was refined into `a_bit_lucky`, `ordinal`, and `a_bit_unlucky`.

The resulting scale preserves the percentile idea while giving the six-item version a symmetric central band and a separate first-attempt and timeout tail. Because the thresholds are part of [`luck.py`](../luck.py), changing the examination size or rerunning the examination does not by itself change the public fortune labels.

## Timeout boundary

`MAX_ATTEMPTS` is `5,000`. In [`calculate_attempts()`](../luck.py#L80-L89), the loop stops when `iteration > MAX_ATTEMPTS` if sorting has still not succeeded. Such a result is returned as `5,001` and is classified as `extremely_unlucky`.
