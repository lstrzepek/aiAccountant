import os
import json


class CounterpartyError(Exception):
    pass


class CounterpartyManager:
    def __init__(self, file_path="business_partners.json"):
        self.file_path = file_path
        self.partners = self._load_partners()

    def _load_partners(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                return json.load(f)
        return {}

    def _save_partners(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.partners, f, indent=2)

    def get_or_create_partner(self, name, addres, account_number=None):
        for partner_id, partner in self.partners.items():
            # First, check if the account number exists
            if account_number:
                if partner["account_number"] == account_number:
                    return partner_id, partner["name"]

            # If account number not found, check for name match
            if partner["name"] == name:
                if (
                    account_number
                    and partner["account_number"] != account_number
                ):
                    raise CounterpartyError(
                        f"Name '{name}' exists with a different account number"
                    )
                return partner_id, name
        new_id = str(len(self.partners) + 1)
        self.partners[new_id] = {
            "name": name,
            "address": addres,
            "account_number": account_number,
        }
        self._save_partners()
        return new_id, name

    def get_partner_info(self, partner_id):
        return self.partners.get(partner_id)
