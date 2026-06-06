# 15 — Resilience: nested path params

Skrajny przypadek: zagnieżdżone ścieżki `{order_id}`, `{customer_id}` — test generatora kodu + verify + retry.

Jeśli runda 1 generuje złą składnię lub brakuje PATCH — kolejna runda dostaje błędy w prompcie.
