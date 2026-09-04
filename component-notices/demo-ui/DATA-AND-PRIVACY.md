# demo-ui data and privacy

The demo UI reads only the synthetic fixture at `fixtures/portfolio.json` through `scout_portfolio_manager.host.ReadOnlyHost`. It does not read `ZERION_API_KEY`, does not call `api.zerion.io`, and does not persist any data between requests or runs.

The demo server (`demo/zerion-portfolio-agent/server.py`) exposes four read-only JSON endpoints (`/api/snapshot`, `/api/pnl`, `/api/dca/parse`, `/api/dca/preview`) that mirror the host's own tools. It writes no file, opens no database, and sends no outbound network request. Anything typed into the DCA chat field is parsed in-process and is not logged or stored by the demo.

Running the demo locally is subject to whatever logging the operator's own machine, browser, or reverse proxy performs; that is outside this repository's control.
