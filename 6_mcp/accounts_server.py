from mcp.server.fastmcp import FastMCP
from accounts import Account

mcp = FastMCP("accounts_server")

@mcp.tool()
async def get_balance(name: str) -> float:
    """Get the cash balance of the given account name.
    
    Args:
        name(str): The name of the account holder
    """
    return Account.get(name).balance

@mcp.tool()
async def get_holdings(name: str) -> dict[str, int]:
    """Get the holdings of the given account user.
    Args:
        name(str): The name of the account holder
    """
    return Account.get(name).holdings

@mcp.tool()
async def buy_shares(name: str, symbol: str, quantity: int, rationale: str) -> float:
    """Buy shares of a stock for the given account user.
    Args:
        name(str): The name of the account
        symbol(str): The stock symbol to buy
        quantity(int): The number of shares to buy
        rationale(str): The rationale for buying the shares
    """
    return Account.get(name).buy_shares(symbol, quantity, rationale)

@mcp.tool()
async def sell_shares(name: str, symbol: str, quantity: int, rationale: str) -> float:
    """Sell shares of a stock for the given account user.
    Args:
        name(str): The name of the account
        symbol(str): The stock symbol to sell
        quantity(int): The number of shares to sell
        rationale(str): The rationale for selling the shares
    """
    return Account.get(name).sell_shares(symbol, quantity, rationale)

@mcp.tool()
async def change_strategy(name: str, strategy: str) -> None:
    """At your descretion, if you chose to, call this to change your investment strategy for the future.
    Args:
        name(str): The name of the account
        strategy(str): The new investment strategy
    """
    return Account.get(name).change_strategy(strategy)

@mcp.resource("accounts://accounts_server/{account_name}")
async def read_account_resource(account_name: str) -> str:
    account = Account.get(account_name.lower())
    return account.report()

@mcp.resource("accounts://strategy/{account_name}")
async def read_strategy_resource(account_name: str) -> str:
    account = Account.get(account_name.lower())
    return account.get_strategy()

if __name__ == "__main__":
    mcp.run(transport='stdio')