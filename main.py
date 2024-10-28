import sys
from purchase_manager import PurchaseManager


def main():
    pass
    if sys.argv[1] == "purchase":
        manager = PurchaseManager(sys.argv[2])
        purchases = manager.parse_purchase_history(sys.argv[3])
        print(len(purchases))
        manager.store_purchases(purchases)


if __name__ == "__main__":
    main()
