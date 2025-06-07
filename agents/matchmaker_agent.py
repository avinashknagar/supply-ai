import json
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MatchmakerAgent:
    def __init__(self):
        """
        Initializes the MatchmakerAgent.
        """
        logger.info("MatchmakerAgent initialized.")

    def _parse_value_unit(self, value_str, default_unit=""):
        """
        Parses a string like '100 kg/month' or '98%' into a float value and a unit string.
        Handles cases with no unit, or just a number.
        """
        if isinstance(value_str, (int, float)):
            return float(value_str), default_unit.lower().strip()
        
        value_str = str(value_str).strip()
        # Attempt to remove common units like '%' before parsing, if they are part of the value itself
        if default_unit == "%" and value_str.endswith("%"):
            value_str = value_str[:-1]

        match = re.match(r"([0-9.]+)\s*(.*)", value_str)
        if match:
            val = float(match.group(1))
            unit = match.group(2).lower().strip()
            return val, unit if unit else default_unit.lower().strip()
        try:
            # If no unit found by regex, try to convert the whole string to float
            return float(value_str), default_unit.lower().strip()
        except ValueError:
            logger.warning(f"Could not parse value-unit string: '{value_str}' with default unit '{default_unit}'. Returning 0.0.")
            return 0.0, default_unit.lower().strip() # Default to 0 if unparseable

    def _calculate_score(self, inventory_item, requested_order):
        """
        Calculates a match score between an inventory item and a requested order.
        Returns a score (0-100) and a list of comments.
        """
        score = 0
        comments = []

        # 1. Material match (case-insensitive exact match)
        inv_material = str(inventory_item.get("material", "")).strip().lower()
        req_material = str(requested_order.get("material", "")).strip().lower()

        if not req_material:
            comments.append("Requested material is not specified. Cannot perform match.")
            return 0, comments

        if inv_material == req_material:
            score += 40
            comments.append(f"Material '{requested_order['material']}' matches.")
        else:
            comments.append(f"Material mismatch: Inventory '{inventory_item.get('material', 'N/A')}' vs Requested '{requested_order.get('material', 'N/A')}'.")
            return 0, comments # If material doesn't match, it's not a viable candidate

        # 2. Purity match (inventory purity >= requested purity)
        inv_purity_val, _ = self._parse_value_unit(inventory_item.get("purity", "0"), default_unit="%")
        req_purity_val, _ = self._parse_value_unit(requested_order.get("purity", "0"), default_unit="%")

        if inv_purity_val >= req_purity_val:
            score += 25
            comments.append(f"Purity meets/exceeds requirement: Inventory {inv_purity_val}% >= Requested {req_purity_val}%.")
        else:
            # score -= 15 # Penalize if purity is lower (optional, can be harsh)
            comments.append(f"Purity requirement not met: Inventory {inv_purity_val}% < Requested {req_purity_val}%.")

        # 3. Quantity match (inventory quantity >= requested quantity, unit consistency is key)
        inv_qty_val, inv_qty_unit = self._parse_value_unit(inventory_item.get("quantity", "0"), default_unit="kg/month")
        req_qty_val, req_qty_unit = self._parse_value_unit(requested_order.get("quantity", "0"), default_unit="kg/month")

        if inv_qty_unit != req_qty_unit:
            comments.append(f"Quantity unit mismatch: Inventory '{inv_qty_unit}' vs Requested '{req_qty_unit}'. Cannot directly compare quantities based on value alone.")
            # score -= 5 # Minor penalty for unit mismatch, as it complicates things but might still be fulfillable with conversion
        elif inv_qty_val >= req_qty_val:
            score += 20
            comments.append(f"Quantity sufficient: Inventory {inv_qty_val} {inv_qty_unit} >= Requested {req_qty_val} {req_qty_unit}.")
        else:
            # score -= 10 # Penalize if quantity is lower (optional)
            comments.append(f"Quantity insufficient: Inventory {inv_qty_val} {inv_qty_unit} < Requested {req_qty_val} {req_qty_unit}.")

        # 4. Technical requirements match
        inv_reqs_list = inventory_item.get("technical_requirements", [])
        req_reqs_list = requested_order.get("technical_requirements", [])

        inv_reqs = set(str(r).lower().strip() for r in inv_reqs_list if isinstance(r, str) and str(r).strip())
        req_reqs = set(str(r).lower().strip() for r in req_reqs_list if isinstance(r, str) and str(r).strip())

        if not req_reqs:
            score += 15 # Bonus if no specific tech reqs, implies flexibility
            comments.append("Order has no specific technical requirements; considered met.")
        else:
            matching_reqs = inv_reqs.intersection(req_reqs)
            missing_from_inv = req_reqs - inv_reqs
            
            if len(matching_reqs) == len(req_reqs):
                score += 15
                comments.append(f"All {len(req_reqs)} requested technical requirement(s) met: {', '.join(sorted(list(matching_reqs)))}.")
            else:
                if matching_reqs:
                    score += len(matching_reqs) * 3 # Partial match bonus, weighted per matched item
                    comments.append(f"Partially met technical requirements: {len(matching_reqs)} of {len(req_reqs)} met ({', '.join(sorted(list(matching_reqs)))}).")
                if missing_from_inv:
                    # score -= len(missing_from_inv) * 5 # Penalize for each missing req (optional)
                    comments.append(f"Inventory MISSES {len(missing_from_inv)} requirement(s): {', '.join(sorted(list(missing_from_inv)))}.")
            
            extra_in_inv = inv_reqs - req_reqs
            if extra_in_inv:
                comments.append(f"Inventory offers additional capabilities not requested: {', '.join(sorted(list(extra_in_inv)))}.")
        
        score = max(0, min(score, 100))
        return score, comments

    def compare_inventory(self, inventory_data, requested_order_data):
        """
        Compares a requested order against inventory records.
        Args:
            inventory_data (list): List of inventory item dicts.
            requested_order_data (dict): Requested order dict.
        Returns:
            list: Sorted list of potential matches with scores and comments.
        """
        if not isinstance(inventory_data, list):
            logger.error("Inventory data must be a list.")
            return [{"error": "Inventory data must be a list.", "input_type": str(type(inventory_data))}]
        if not isinstance(requested_order_data, dict):
            logger.error("Requested order data must be a dictionary.")
            return [{"error": "Requested order data must be a dictionary.", "input_type": str(type(requested_order_data))}]

        logger.info(f"Comparing order for '{requested_order_data.get('material')}' against {len(inventory_data)} items.")
        matches = []
        for item_idx, item in enumerate(inventory_data):
            if not isinstance(item, dict):
                logger.warning(f"Skipping invalid inventory item #{item_idx} (not a dict): {item}")
                continue
            score, comments = self._calculate_score(item, requested_order_data)
            # Only add to matches if the material was a potential match (score could be 0 due to other factors)
            if not (comments and "Material mismatch" in comments[0] and score == 0):
                 matches.append({
                    "inventory_item": item,
                    "match_score": score,
                    "comments": comments
                })
        
        sorted_matches = sorted(matches, key=lambda x: x["match_score"], reverse=True)
        if not sorted_matches:
            logger.info("No suitable matches found for the requested order.")
            return [{
                "message": "No suitable matches found for the requested order.", 
                "requested_order": requested_order_data
            }]
        
        logger.info(f"Found {len(sorted_matches)} potential match(es). Best score: {sorted_matches[0]['match_score'] if sorted_matches else 'N/A'}")
        return sorted_matches

# Example Usage:
if __name__ == '__main__':
    agent = MatchmakerAgent()
    sample_inventory = [
        {"material": "Sulfuric Acid", "purity": "98%", "quantity": "200 kg/month", "technical_requirements": ["Pharma Grade", "Low Water Content"]},
        {"material": "Hydrochloric Acid", "purity": "37%", "quantity": "150 kg/month", "technical_requirements": ["Industrial Grade", "Specific Inhibitor Package"]},
        {"material": "Hydrochloric Acid", "purity": "35%", "quantity": "50 kg/month", "technical_requirements": ["Industrial Grade"]},
        {"material": "Nitric Acid", "purity": "68%", "quantity": "100 kg/month", "technical_requirements": ["Reagent Grade"]},
        {"material": "Caustic Soda Flakes", "purity": "99%", "quantity": "500 kg/month", "technical_requirements": ["Food Grade", "Low Iron"]},
        {"material": "Caustic Soda Lye", "purity": "48%", "quantity": "1000 ton/year", "technical_requirements": ["Membrane Grade"]}
    ]

    test_orders = [
        {"material": "Hydrochloric Acid", "purity": "36%", "quantity": "100 kg/month", "technical_requirements": ["Industrial Grade"]},
        {"material": "Sulfuric Acid", "purity": "99%", "quantity": "150 kg/month", "technical_requirements": ["Pharma Grade", "Low Water Content", "Extra Pure"]},
        {"material": "Acetic Acid", "purity": "99%", "quantity": "50 kg/month", "technical_requirements": ["Glacial"]},
        {"material": "Caustic Soda Flakes", "purity": "90%", "quantity": "600 kg/month", "technical_requirements": ["Food Grade", "Low Iron", "Kosher Certified"]},
        {"material": "Nitric Acid", "purity": "65%", "quantity": "80 kg/month", "technical_requirements": []},
        {"material": "Caustic Soda Lye", "purity": "45%", "quantity": "50 ton/month", "technical_requirements": ["Membrane Grade"]},
        {"material": "Sulfuric Acid", "purity": "98", "quantity": "150", "technical_requirements": ["Pharma Grade"]}, # Purity/Quantity as numbers
        {"material": "Hydrochloric Acid", "purity": "30%", "quantity": "200 kg/week", "technical_requirements": ["Industrial Grade"]}, # Different quantity unit
    ]

    for i, order in enumerate(test_orders):
        print(f"\n--- Test Case {i+1} --- ({order.get('material', 'Unknown Material')})")
        print(f"Requested Order: {json.dumps(order)}")
        results = agent.compare_inventory(sample_inventory, order)
        print("Results:")
        print(json.dumps(results, indent=4))