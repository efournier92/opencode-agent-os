#!/usr/bin/env python3
"""Single source of OpenCode Go model prices and the plan split."""

# model id -> (input, output, cached, monthly_limit) per 1M tokens.
PRICES = {
    "deepseek-v4.1-flash": (0.15, 0.60, 0.003, 100),
    "glm-5.3": (1.40, 4.40, 0.26, 15),
    "glm-5.3-flash": (0.15, 0.50, 0.03, 60),
}

# Historical name kept so callers can import either spelling.
GO_PRICES = PRICES

# Fraction of the monthly allowance each window may consume.
PLAN_SPLIT = {"5h": 0.20, "weekly": 0.50, "monthly": 1.0}
