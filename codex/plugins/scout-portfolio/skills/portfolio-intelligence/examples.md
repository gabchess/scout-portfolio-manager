# Examples

## Portfolio question

User: `What is my PnL?`

Use `get_pnl`. Explain the formula and identify the fixture as synthetic. Do not imply that
the result is a live account balance.

## Incomplete DCA request

User: `DCA $300 of ETH every week`

Use `parse_dca_request`. Ask for chain, source wallet, and destination wallet. Do not infer
Ethereum or either wallet.

## Complete DCA request

User: `Preview $300 of ETH on ethereum weekly from wallet:source to wallet:destination`

Use `preview_dca`. Present the proposal, assumptions, fee and slippage fields, and the
required approval state. Do not execute or describe it as submitted.
