import click
from .purchase_manager import PurchaseManager


@click.group()
@click.pass_context
def cli(ctx):
    """Accountant: Process business account history and generate Beancount ledgers."""
    ctx.obj = {}
    ctx.obj["purchase_manager"] = PurchaseManager()
    # ctx.obj['counterparty_manager'] = CounterpartyManager()


@cli.group()
def purchase():
    pass


@purchase.command()
@click.argument("input_file")
@click.option(
    "--source_type",
    "-s",
    help="Define source of the purchase file to be parsed from",
    default="apple",
)
def create(input_file: str, source_type: str):
    manager = PurchaseManager("./data/purchases.json")
    purchases = manager.parse_purchase_history(input_file)
    print(len(purchases))
    manager.store_purchases(purchases)
