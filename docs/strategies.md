# Writing custom strategies

A strategy is any class that subclasses `BaseStrategy` and implements `evaluate()`. Drop the file in `src/polymarket_bot/strategies/`, register it, and the bot picks it up.

## The `evaluate` contract

```python
def evaluate(
    self,
    market: Market,            # Polymarket market metadata
    orderbook: OrderBookSnapshot,  # live best bid/ask
    position: Position | None, # current position in this market, if any
) -> Signal | None:            # return a Signal to trade, or None to skip
```

The framework calls `evaluate` once per market per scan. It's pure — no I/O — so write it like a function: input → decision.

## Available primitives

`Market`:

- `condition_id`, `question`, `category`
- `yes_token_id`, `no_token_id`
- `volume_24h_usd`, `liquidity_usd`
- `end_date_iso`

`OrderBookSnapshot`:

- `token_id`
- `best_bid`, `best_ask`, `bid_size`, `ask_size`
- `midpoint` (computed)
- `spread` (computed)

`Position` (None if you're flat):

- `size`, `avg_price`, `cur_price`, `realized_pnl`

`Signal`:

- `Signal.buy(token_id, price, size, reason="")`
- `Signal.sell(token_id, price, size, reason="")`

## Patterns

### Filter early, decide late

```python
def evaluate(self, market, book, pos):
    # Hard filters first
    if market.volume_24h_usd < 50_000:
        return None
    if book.spread > 0.03:
        return None
    if "Politics" not in market.category:
        return None
    # ... your logic
```

### Stateful strategies

Use instance attributes. The strategy object lives for the bot's lifetime, so a `deque` or rolling counter works fine.

```python
@dataclass
class VWAPStrategy(BaseStrategy):
    window: int = 20
    _prices: dict[str, deque] = field(default_factory=dict)

    def evaluate(self, market, book, pos):
        history = self._prices.setdefault(book.token_id, deque(maxlen=self.window))
        history.append(book.midpoint)
        ...
```

### External signals

Nothing stops your strategy from calling out to an ML model, a sports API, an LLM, or a database. Keep it fast (the loop blocks on each call) — for slow signals, run them on a background thread and just *read* the latest value in `evaluate()`.

## Testing

```python
# tests/test_my_strategy.py
def test_my_strategy_buys_when_oversold():
    s = MyStrategy(threshold=0.10)
    book = _FakeBook(best_bid=0.05, best_ask=0.06)
    sig = s.evaluate(_FakeMarket(), book, position=None)
    assert sig is not None and sig.side == "BUY"
```

`tests/test_strategies.py` has runnable fakes you can copy.

## Checklist before going live

- [ ] All hard filters in place (volume, spread, category)
- [ ] Sized in USD, not raw shares
- [ ] Has an exit rule, not just an entry rule
- [ ] Tested in `--dry-run` for at least one full market cycle
- [ ] Risk manager limits set conservatively
