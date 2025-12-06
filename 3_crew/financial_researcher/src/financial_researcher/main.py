#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from financial_researcher.crew import FinancialResearcher

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the FinancialResearcher crew.
    """
    inputs = {
        'company': 'Apple',
    }
    try:
        result = FinancialResearcher().crew().kickoff(inputs=inputs)
        print('\n\n=== FINALE REPORT ===\n\n')
        print(result.raw)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


if __name__ == "__main__":
    run()