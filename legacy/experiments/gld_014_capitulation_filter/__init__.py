"""GLD Signal-Day Capitulation-Strength Filter MR (GLD-014)"""

from trading.experiments import register
from trading.experiments.gld_014_capitulation_filter.strategy import GLD014Strategy

register("gld_014_capitulation_filter")(GLD014Strategy)
