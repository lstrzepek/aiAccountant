import re
import json
from datetime import datetime
from bs4 import BeautifulSoup


class PurchaseManager:
    def __init__(self, file_path="purchases.json"):
        self.file_path = file_path

    def store_purchases(self, purchases):
        # # Filter out zero-price items and sort by date (newest first)
        # filtered_purchases = [
        #     p
        #     for p in purchases
        #     if p["price"] != "0,00 zł" and p["price"] != "Free"
        # ]
        # filtered_purchases.sort(key=lambda x: x["purchase_date"], reverse=True)

        # Convert datetime objects to strings for JSON serialization
        for purchase in purchases:
            purchase["purchase_date"] = purchase["purchase_date"].strftime(
                "%Y-%m-%d"
            )

        # Save to file
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(purchases, f, indent=2)

    def get_purchases_by_date(self, target_date):
        target_date_str = target_date.strftime("%Y-%m-%d")

        with open(self.file_path, "r") as f:
            purchases = json.load(f)

        # Since the list is sorted by date, we can use binary search
        left, right = 0, len(purchases) - 1
        while left <= right:
            mid = (left + right) // 2
            mid_date = purchases[mid]["purchase_date"]
            if mid_date == target_date_str:
                # Found a matching date, now collect all purchases for this date
                results = [purchases[mid]]
                # Check preceding purchases
                i = mid - 1
                while (
                    i >= 0 and purchases[i]["purchase_date"] == target_date_str
                ):
                    results.append(purchases[i])
                    i -= 1
                # Check following purchases
                i = mid + 1
                while (
                    i < len(purchases)
                    and purchases[i]["purchase_date"] == target_date_str
                ):
                    results.append(purchases[i])
                    i += 1
                return results
            elif mid_date > target_date_str:
                left = mid + 1
            else:
                right = mid - 1

        return []  # No purchases found for the given date

    def _extract_purchase_info(self, line):
        pattern = r"(\d{1,2}\s\w+\s\d{4})\s(\w+)\sTotal\s([\d,]+\s\w+).*?\s(.*?)\s([\d,]+\s\w+|Free)$"
        match = re.search(pattern, line)

        if match:
            date_str, purchase_id, total_price, product_name, price = (
                match.groups()
            )

            date = datetime.strptime(date_str, "%d %b %Y")

            product_name = product_name.replace("Loading... ", "").replace(
                "This purchase is free and does not have an invoice ", ""
            )

            # If the price is 'Free', set it to '0,00 zł'
            # if price == "Free":
            #     price = "0,00 zł"

            return {
                "purchase_date": date,
                "purchase_id": purchase_id,
                "total_price": total_price,
                "product_name": product_name,
                "price": price,
            }
        else:
            return None

    def parse_purchase_history(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
            soup = BeautifulSoup(html_content, "html.parser")
            divs = soup.find_all("div", class_="purchase loaded collapsed")

            print(len(divs))
            results = []
            for div in divs:
                line = re.sub(r"\s+", " ", div.get_text())
                result = self._extract_purchase_info(line.strip())
                if not result:
                    print(f"Couldn't extract information from: '{line}'")
                elif result["price"] == "Free":
                    continue
                else:
                    results.append(result)
            return results


# # Example usage
# manager = PurchaseManager()
#
# # Sample purchases data
# purchases = [
#     {
#         'purchase_date': datetime(2018, 11, 14),
#         'purchase_id': 'MM4WYQLNYW',
#         'total_price': '32,99 zł',
#         'product_name': 'Course Tier 7 Udemy Online Video Courses',
#         'price': '32,99 zł'
#     },
#     {
#         'purchase_date': datetime(2018, 11, 12),
#         'purchase_id': 'R3H1T86F816',
#         'total_price': '0,00 zł',
#         'product_name': 'Free Product',
#         'price': 'Free'
#     },
#     {
#         'purchase_date': datetime(2018, 11, 14),
#         'purchase_id': 'ANOTHERPURCHASE',
#         'total_price': '15,99 zł',
#         'product_name': 'Another Product',
#         'price': '15,99 zł'
#     }
# ]
#
# # Store purchases
# manager.store_purchases(purchases)
#
# # Retrieve purchases for a specific date
# retrieved_purchases = manager.get_purchases_by_date(datetime(2018, 11, 14))
# print(json.dumps(retrieved_purchases, indent=2))
