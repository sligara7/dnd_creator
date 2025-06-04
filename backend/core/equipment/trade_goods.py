# trade_goods.py
# Description: Handles trade goods for commerce, bartering, and wealth storage

from typing import Dict, List, Optional, Union, Any, Tuple
import json
import re
from enum import Enum

from backend.core.equipment.equipment import Equipment, EquipmentCategory, RarityType

class TradeGoodCategory(Enum):
    """Categories of trade goods"""
    METALS = "metals"           # Ore, ingots, and metal bars
    GEMS = "gems"               # Precious and semi-precious stones
    TEXTILES = "textiles"       # Cloth, silk, wool, etc.
    SPICES = "spices"           # Exotic cooking and medicinal spices
    LIVESTOCK = "livestock"     # Animals for trading
    TIMBER = "timber"           # Wood and lumber
    FOOD = "food"               # Foods that store well for trading
    FURS = "furs"               # Animal hides and furs
    CRAFTING = "crafting"       # Materials for crafting
    EXOTIC = "exotic"           # Unusual or foreign goods
    ALCHEMICAL = "alchemical"   # Ingredients for alchemy
    ARTWORK = "artwork"         # Tradable artistic works
    TRADE_BARS = "trade_bars"   # Standardized currency equivalents

class TradeGoodProperty(Enum):
    """Properties that trade goods can have"""
    PERISHABLE = "perishable"        # Spoils over time
    NON_PERISHABLE = "non_perishable"  # Maintains quality over time
    FRAGILE = "fragile"              # Can be damaged easily
    DURABLE = "durable"              # Resistant to damage
    BULKY = "bulky"                  # Takes up significant space
    LIGHTWEIGHT = "lightweight"      # Easy to transport
    RARE = "rare"                    # Uncommon or hard to find
    COMMON = "common"                # Widely available
    LUXURY = "luxury"                # High-end or prestigious
    ESSENTIAL = "essential"          # Basic necessity
    REGULATED = "regulated"          # Subject to trade restrictions
    CONTRABAND = "contraband"        # Illegal in some regions
    VOLATILE = "volatile"            # Unstable market value

class MarketDemand(Enum):
    """Demand levels for trade goods in a market"""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    VERY_LOW = "very_low"
    NONE = "none"

class TradeGoods(Equipment):
    """
    Class for handling trade goods for commerce, bartering, and wealth storage.
    
    Extends the Equipment class with trade-specific functionality for creating,
    valuing, and trading goods for character commerce and economic activities.
    """
    
    def __init__(self, llm_service=None):
        """Initialize the trade goods manager with parent equipment functionality."""
        super().__init__(llm_service)
        
        # Additional trade goods configuration
        self.regional_modifiers = {
            "urban_center": {"metals": 1.0, "gems": 1.2, "textiles": 1.0, "spices": 1.1, 
                           "livestock": 0.9, "timber": 1.1, "food": 0.9},
            "rural_village": {"metals": 1.2, "gems": 1.4, "textiles": 1.1, "spices": 1.3, 
                            "livestock": 0.8, "timber": 0.7, "food": 0.7},
            "mountain_hold": {"metals": 0.7, "gems": 0.8, "textiles": 1.2, "spices": 1.3, 
                            "livestock": 1.1, "timber": 1.1, "food": 1.2},
            "coastal_port": {"metals": 1.1, "gems": 1.0, "textiles": 0.9, "spices": 0.8, 
                           "livestock": 1.0, "timber": 1.0, "food": 0.8},
            "desert_outpost": {"metals": 1.3, "gems": 1.1, "textiles": 1.2, "spices": 0.9, 
                             "livestock": 1.3, "timber": 1.5, "food": 1.4}
        }
        
        # Demand by settlement type
        self.demand_by_region = {
            "urban_center": {"metals": MarketDemand.HIGH, "gems": MarketDemand.HIGH, 
                          "textiles": MarketDemand.MODERATE, "spices": MarketDemand.HIGH},
            "rural_village": {"food": MarketDemand.LOW, "livestock": MarketDemand.LOW, 
                           "metals": MarketDemand.HIGH, "timber": MarketDemand.LOW},
            "mountain_hold": {"metals": MarketDemand.LOW, "gems": MarketDemand.LOW, 
                           "timber": MarketDemand.MODERATE, "food": MarketDemand.HIGH},
            "coastal_port": {"spices": MarketDemand.LOW, "textiles": MarketDemand.LOW, 
                          "exotic": MarketDemand.LOW, "food": MarketDemand.MODERATE}
        }
        
        # Standard trade good values by weight/unit
        self.standard_values = {
            "metals": {"copper": {"gp": 0.5, "per": "pound"}, 
                    "silver": {"gp": 5, "per": "pound"}, 
                    "gold": {"gp": 50, "per": "pound"}, 
                    "platinum": {"gp": 500, "per": "pound"},
                    "iron": {"gp": 0.1, "per": "pound"}},
            "gems": {"average": {"gp": 50, "per": "gem"}, 
                   "high_quality": {"gp": 500, "per": "gem"}, 
                   "exceptional": {"gp": 5000, "per": "gem"}},
            "textiles": {"cotton": {"gp": 0.5, "per": "yard"}, 
                       "linen": {"gp": 1, "per": "yard"}, 
                       "silk": {"gp": 10, "per": "yard"}},
            "spices": {"common": {"gp": 1, "per": "pound"}, 
                     "exotic": {"gp": 5, "per": "pound"}, 
                     "rare": {"gp": 15, "per": "pound"}},
            "livestock": {"chicken": {"gp": 0.1, "per": "animal"}, 
                        "goat": {"gp": 1, "per": "animal"}, 
                        "cow": {"gp": 10, "per": "animal"}, 
                        "ox": {"gp": 15, "per": "animal"}}
        }
    
    def get_trade_goods_by_category(self, category: Union[TradeGoodCategory, str]) -> List[Dict[str, Any]]:
        """
        Get trade goods filtered by category.
        
        Args:
            category: Category to filter by (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of trade goods in the category
        """
        if isinstance(category, str):
            # Try to convert string to enum
            try:
                category = TradeGoodCategory(category.lower())
            except ValueError:
                # If not a valid category, return empty list
                return []
        
        return [
            t for t in self.trade_goods.values() 
            if "trade_good_category" in t and t["trade_good_category"] == category
        ]
    
    def get_trade_goods_by_property(self, property_name: Union[TradeGoodProperty, str]) -> List[Dict[str, Any]]:
        """
        Get trade goods that have a specific property.
        
        Args:
            property_name: Property to filter by (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of trade goods with the property
        """
        property_str = property_name.value if isinstance(property_name, TradeGoodProperty) else str(property_name).lower()
        
        return [
            t for t in self.trade_goods.values() 
            if "properties" in t and any(property_str in prop.lower() for prop in t["properties"])
        ]
    
    def get_trade_goods_by_value_range(self, min_value: float, max_value: float) -> List[Dict[str, Any]]:
        """
        Get trade goods within a specific value range.
        
        Args:
            min_value: Minimum value in gold pieces
            max_value: Maximum value in gold pieces
            
        Returns:
            List[Dict[str, Any]]: List of trade goods in value range
        """
        matched_goods = []
        
        for good_id, good_data in self.trade_goods.items():
            # Calculate base value of the trade good
            if "base_value" in good_data:
                # If it has a direct base value
                value_gp = good_data["base_value"].get("gp", 0)
                value_gp += good_data["base_value"].get("sp", 0) / 10
                value_gp += good_data["base_value"].get("cp", 0) / 100
                
                if min_value <= value_gp <= max_value:
                    matched_goods.append(good_data)
                    
            elif "unit_value" in good_data and "quantity" in good_data:
                # If it has a unit value and quantity
                unit_value_gp = good_data["unit_value"].get("gp", 0)
                unit_value_gp += good_data["unit_value"].get("sp", 0) / 10
                unit_value_gp += good_data["unit_value"].get("cp", 0) / 100
                
                total_value = unit_value_gp * good_data["quantity"]
                
                if min_value <= total_value <= max_value:
                    matched_goods.append(good_data)
        
        return matched_goods
    
    def calculate_trade_good_value(self, 
                                good_id: str, 
                                region_type: str = "urban_center",
                                quantity: float = 1.0) -> Dict[str, Any]:
        """
        Calculate the value of a trade good in a specific region.
        
        Args:
            good_id: ID of the trade good
            region_type: Type of region for pricing
            quantity: Quantity of the trade good
            
        Returns:
            Dict[str, Any]: Value calculation results
        """
        good_data = self._find_item_by_id(good_id)
        if not good_data:
            return {"error": "Trade good not found"}
        
        # Get the category for regional adjustments
        category = None
        if "trade_good_category" in good_data:
            category = good_data["trade_good_category"]
            if isinstance(category, TradeGoodCategory):
                category = category.value
        
        # Get base value
        base_value_gp = 0
        if "base_value" in good_data:
            base_value_gp = good_data["base_value"].get("gp", 0)
            base_value_gp += good_data["base_value"].get("sp", 0) / 10
            base_value_gp += good_data["base_value"].get("cp", 0) / 100
        elif "unit_value" in good_data:
            base_value_gp = good_data["unit_value"].get("gp", 0)
            base_value_gp += good_data["unit_value"].get("sp", 0) / 10
            base_value_gp += good_data["unit_value"].get("cp", 0) / 100
        
        # Apply regional modifier
        region_modifier = 1.0
        if region_type in self.regional_modifiers and category and category in self.regional_modifiers[region_type]:
            region_modifier = self.regional_modifiers[region_type][category]
        
        # Apply quantity
        adjusted_value = base_value_gp * region_modifier * quantity
        
        # Apply bulk discounts or premiums
        quantity_modifier = 1.0
        if quantity >= 100:
            quantity_modifier = 0.8  # 20% discount for bulk purchase
        elif quantity >= 50:
            quantity_modifier = 0.9  # 10% discount for bulk purchase
        elif quantity >= 20:
            quantity_modifier = 0.95  # 5% discount for bulk purchase
        elif quantity <= 0.1:
            quantity_modifier = 1.5  # 50% premium for very small amounts
        
        final_value = adjusted_value * quantity_modifier
        
        # Check for special market conditions
        market_demand = MarketDemand.MODERATE
        if region_type in self.demand_by_region and category and category in self.demand_by_region[region_type]:
            market_demand = self.demand_by_region[region_type][category]
        
        demand_modifier = 1.0
        if market_demand == MarketDemand.VERY_HIGH:
            demand_modifier = 1.5
        elif market_demand == MarketDemand.HIGH:
            demand_modifier = 1.2
        elif market_demand == MarketDemand.LOW:
            demand_modifier = 0.8
        elif market_demand == MarketDemand.VERY_LOW:
            demand_modifier = 0.6
        elif market_demand == MarketDemand.NONE:
            demand_modifier = 0.3
        
        final_value *= demand_modifier
        
        # Convert to currency units
        gp = int(final_value)
        sp = int((final_value - gp) * 10)
        cp = int(((final_value - gp) * 10 - sp) * 10)
        
        return {
            "trade_good_name": good_data.get("name"),
            "base_value_gp": base_value_gp,
            "quantity": quantity,
            "region_type": region_type,
            "region_modifier": region_modifier,
            "quantity_modifier": quantity_modifier,
            "market_demand": market_demand.value if isinstance(market_demand, MarketDemand) else market_demand,
            "demand_modifier": demand_modifier,
            "final_value": {
                "gp": gp,
                "sp": sp,
                "cp": cp
            },
            "final_value_gp": final_value
        }
    
    def find_profitable_trades(self, 
                            origin_region: str, 
                            destination_region: str,
                            investment_limit_gp: float = 100.0,
                            available_goods: List[str] = None) -> Dict[str, Any]:
        """
        Find potentially profitable trades between regions.
        
        Args:
            origin_region: Region where goods are purchased
            destination_region: Region where goods are sold
            investment_limit_gp: Maximum investment in gold pieces
            available_goods: Optional list of available good IDs
            
        Returns:
            Dict[str, Any]: Profitable trade opportunities
        """
        if origin_region not in self.regional_modifiers or destination_region not in self.regional_modifiers:
            return {"error": "Invalid region specified"}
        
        # Get goods to analyze
        goods_to_check = []
        if available_goods:
            for good_id in available_goods:
                good_data = self._find_item_by_id(good_id)
                if good_data:
                    goods_to_check.append(good_data)
        else:
            goods_to_check = list(self.trade_goods.values())
        
        # Analyze potential profits
        opportunities = []
        
        for good in goods_to_check:
            good_id = good.get("id")
            category = None
            
            # Get category for calculations
            if "trade_good_category" in good:
                category = good["trade_good_category"]
                if isinstance(category, TradeGoodCategory):
                    category = category.value
            else:
                continue  # Skip items without a category
            
            # Calculate purchase cost
            origin_cost = self.calculate_trade_good_value(good_id, origin_region, 1.0)
            if "error" in origin_cost:
                continue
                
            # Calculate sell value at destination
            destination_value = self.calculate_trade_good_value(good_id, destination_region, 1.0)
            if "error" in destination_value:
                continue
            
            # Calculate maximum quantity that can be purchased with investment limit
            origin_cost_per_unit = origin_cost["final_value_gp"]
            if origin_cost_per_unit <= 0:
                continue
                
            max_quantity = investment_limit_gp / origin_cost_per_unit
            
            # Calculate potential profit
            destination_value_per_unit = destination_value["final_value_gp"]
            potential_profit_per_unit = destination_value_per_unit - origin_cost_per_unit
            potential_profit = potential_profit_per_unit * max_quantity
            profit_margin = (potential_profit_per_unit / origin_cost_per_unit) * 100 if origin_cost_per_unit > 0 else 0
            
            # Only include profitable trades
            if potential_profit > 0:
                opportunities.append({
                    "trade_good": good.get("name"),
                    "trade_good_id": good_id,
                    "origin_cost_per_unit": origin_cost_per_unit,
                    "destination_value_per_unit": destination_value_per_unit,
                    "profit_per_unit": potential_profit_per_unit,
                    "max_quantity": round(max_quantity, 2),
                    "total_investment": round(origin_cost_per_unit * max_quantity, 2),
                    "potential_profit": round(potential_profit, 2),
                    "profit_margin": round(profit_margin, 1),
                    "category": category
                })
        
        # Sort by profit margin (highest first)
        opportunities.sort(key=lambda x: x["profit_margin"], reverse=True)
        
        return {
            "origin_region": origin_region,
            "destination_region": destination_region,
            "investment_limit_gp": investment_limit_gp,
            "opportunities": opportunities,
            "total_opportunities": len(opportunities)
        }
    
    def create_custom_trade_good(self, 
                              name: str,
                              trade_good_category: TradeGoodCategory,
                              base_value: Dict[str, int],
                              weight_per_unit: float = 1.0,
                              properties: List[str] = None,
                              unit: str = "pound",
                              description: str = None,
                              region_of_origin: str = None) -> Dict[str, Any]:
        """
        Create a custom trade good with specified attributes.
        
        Args:
            name: Name of the trade good
            trade_good_category: Category of the trade good
            base_value: Base value in currency
            weight_per_unit: Weight per unit in pounds
            properties: List of trade good properties
            unit: Unit of measure (pound, yard, piece, etc.)
            description: Description of the trade good
            region_of_origin: Region where the good originates
            
        Returns:
            Dict[str, Any]: Created trade good data
        """
        # Generate a description if none provided
        if description is None:
            description = f"A tradeable {trade_good_category.value} good valued for commerce."
        
        # Set default properties if none provided
        if properties is None:
            if trade_good_category in [TradeGoodCategory.FOOD, TradeGoodCategory.SPICES]:
                properties = [TradeGoodProperty.PERISHABLE.value]
            elif trade_good_category in [TradeGoodCategory.METALS, TradeGoodCategory.GEMS]:
                properties = [TradeGoodProperty.NON_PERISHABLE.value, TradeGoodProperty.DURABLE.value]
            else:
                properties = [TradeGoodProperty.NON_PERISHABLE.value]
        
        # Create the trade good data
        trade_good_data = {
            "id": f"custom_{name.lower().replace(' ', '_')}",
            "name": name,
            "category": EquipmentCategory.TRADE_GOOD,
            "trade_good_category": trade_good_category,
            "base_value": base_value,
            "weight_per_unit": weight_per_unit,
            "properties": properties,
            "unit": unit,
            "description": description
        }
        
        # Add region of origin if provided
        if region_of_origin:
            trade_good_data["region_of_origin"] = region_of_origin
        
        # Add to trade goods collection
        self.trade_goods[trade_good_data["id"]] = trade_good_data
        
        return trade_good_data
    
    def calculate_bulk_trade_value(self,
                                trade_data: List[Dict[str, Any]],
                                destination: str = "urban_center") -> Dict[str, Any]:
        """
        Calculate the total value and weight of a bulk trade shipment.
        
        Args:
            trade_data: List of trade goods with quantities
            destination: Destination region type
            
        Returns:
            Dict[str, Any]: Bulk trade calculation results
        """
        total_value_gp = 0
        total_weight = 0
        items_calculated = []
        
        for item in trade_data:
            good_id = item.get("id")
            quantity = item.get("quantity", 1)
            
            # Calculate value
            value_result = self.calculate_trade_good_value(good_id, destination, quantity)
            if "error" in value_result:
                continue
            
            # Get weight
            good_data = self._find_item_by_id(good_id)
            weight = 0
            if good_data and "weight_per_unit" in good_data:
                weight = good_data["weight_per_unit"] * quantity
            
            # Add to totals
            total_value_gp += value_result["final_value_gp"]
            total_weight += weight
            
            items_calculated.append({
                "name": good_data.get("name"),
                "quantity": quantity,
                "unit": good_data.get("unit", "unit"),
                "value_gp": value_result["final_value_gp"],
                "weight": weight
            })
        
        # Convert total value to currency
        gp = int(total_value_gp)
        sp = int((total_value_gp - gp) * 10)
        cp = int(((total_value_gp - gp) * 10 - sp) * 10)
        
        return {
            "total_items": len(items_calculated),
            "total_value": {
                "gp": gp,
                "sp": sp,
                "cp": cp
            },
            "total_value_gp": total_value_gp,
            "total_weight_pounds": total_weight,
            "destination": destination,
            "items": items_calculated
        }
    
    def enhance_trade_good_with_llm(self, 
                                 good_id: str, 
                                 enhancement_type: str = "description") -> Dict[str, Any]:
        """
        Enhance trade good with LLM-generated content.
        
        Args:
            good_id: ID of the trade good to enhance
            enhancement_type: Type of enhancement (description, market, origin)
            
        Returns:
            Dict[str, Any]: Enhanced trade good data
        """
        good_data = self._find_item_by_id(good_id)
        if not good_data:
            return {"error": "Trade good not found"}
            
        # Create a copy to avoid modifying the original
        enhanced_good = good_data.copy()
        
        if enhancement_type.lower() == "description":
            # Generate detailed description
            prompt = self.llm_advisor._create_prompt(
                "create detailed trade good description",
                f"Trade Good: {good_data.get('name')}\n"
                f"Category: {good_data.get('trade_good_category').value if isinstance(good_data.get('trade_good_category'), TradeGoodCategory) else 'unknown'}\n"
                f"Properties: {', '.join(good_data.get('properties', []))}\n\n"
                "Create a detailed description of this trade good, including its appearance, "
                "origins, qualities that make it valuable, and common uses. The description should "
                "help players understand the item's place in the economy and its cultural significance."
            )
            
            try:
                response = self.llm_advisor.llm_service.generate(prompt)
                
                # Clean up the response
                clean_response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
                clean_response = re.sub(r'\{.*?\}', '', clean_response, flags=re.DOTALL)
                
                enhanced_good["detailed_description"] = clean_response.strip()
            except Exception as e:
                print(f"Error generating trade good description: {e}")
                enhanced_good["detailed_description"] = "A standard trade good of its type."
                
        elif enhancement_type.lower() == "market":
            # Generate market information
            prompt = self.llm_advisor._create_prompt(
                "generate market information",
                f"Trade Good: {good_data.get('name')}\n"
                f"Category: {good_data.get('trade_good_category').value if isinstance(good_data.get('trade_good_category'), TradeGoodCategory) else 'unknown'}\n\n"
                "Create market information for this trade good, including "
                "regions where it's in high demand, factors that affect its value, "
                "common trading practices, and potential market opportunities. "
                "Return as JSON with 'high_demand_regions', 'value_factors', 'trading_practices', and 'market_opportunities' keys."
            )
            
            try:
                response = self.llm_advisor.llm_service.generate(prompt)
                market_data = self.llm_advisor._extract_json(response)
                
                if market_data:
                    enhanced_good["market_information"] = market_data
                else:
                    enhanced_good["market_information"] = {
                        "high_demand_regions": ["Various urban centers"],
                        "value_factors": ["Supply and demand", "Quality"],
                        "trading_practices": ["Standard commerce"],
                        "market_opportunities": ["Potential for profit in distant markets"]
                    }
            except Exception as e:
                print(f"Error generating market information: {e}")
                enhanced_good["market_information"] = {
                    "high_demand_regions": ["Various urban centers"],
                    "value_factors": ["Supply and demand", "Quality"],
                    "trading_practices": ["Standard commerce"],
                    "market_opportunities": ["Potential for profit in distant markets"]
                }
            
        elif enhancement_type.lower() == "origin":
            # Generate origin story
            prompt = self.llm_advisor._create_prompt(
                "create trade good origin story",
                f"Trade Good: {good_data.get('name')}\n"
                f"Category: {good_data.get('trade_good_category').value if isinstance(good_data.get('trade_good_category'), TradeGoodCategory) else 'unknown'}\n\n"
                "Create an interesting origin story for this trade good, including where it's found or produced, "
                "how it became valuable as a trading commodity, historical significance in trade networks, "
                "and any legends or stories associated with it. The origin story should add depth and "
                "narrative hooks for the trade good."
            )
            
            try:
                response = self.llm_advisor.llm_service.generate(prompt)
                enhanced_good["origin_story"] = response
            except Exception as e:
                print(f"Error generating trade good origin story: {e}")
                enhanced_good["origin_story"] = f"A {good_data.get('name')} with a typical trading history."
            
        return enhanced_good
    
    def generate_trade_network(self, 
                            regions: List[str],
                            focus_categories: List[str] = None) -> Dict[str, Any]:
        """
        Generate a network of trade relationships between regions.
        
        Args:
            regions: List of region types to include
            focus_categories: Optional list of trade good categories to focus on
            
        Returns:
            Dict[str, Any]: Trade network data
        """
        valid_regions = []
        for region in regions:
            if region in self.regional_modifiers:
                valid_regions.append(region)
        
        if not valid_regions:
            return {"error": "No valid regions specified"}
        
        # Ensure focus categories are valid
        valid_categories = []
        if focus_categories:
            for category in focus_categories:
                try:
                    # Convert string to enum
                    if isinstance(category, str):
                        cat_enum = TradeGoodCategory(category.lower())
                        valid_categories.append(cat_enum.value)
                    else:
                        valid_categories.append(category.value)
                except ValueError:
                    continue
        
        # If no valid categories specified, use all categories
        if not valid_categories:
            valid_categories = [c.value for c in TradeGoodCategory]
        
        # Use LLM to generate trade network
        regions_str = ", ".join(valid_regions)
        categories_str = ", ".join(valid_categories)
        
        prompt = self.llm_advisor._create_prompt(
            "generate trade network",
            f"Regions: {regions_str}\n"
            f"Trade Categories: {categories_str}\n\n"
            "Generate a comprehensive trade network between these regions, showing how goods flow "
            "between them and where specific trade advantages exist. For each region, specify its "
            "exports, imports, trade advantages, and key relationships with other regions. "
            "Include details about trade routes, potential obstacles, and cultural factors affecting trade. "
            "Return as JSON with 'regions' as an array of objects containing 'name', 'exports', 'imports', "
            "'advantages', 'disadvantages', 'key_relationships', and 'trade_routes' keys."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            network_data = self.llm_advisor._extract_json(response)
            
            if network_data and "regions" in network_data:
                return {
                    "included_regions": valid_regions,
                    "focus_categories": valid_categories,
                    "trade_network": network_data["regions"]
                }
        except Exception as e:
            print(f"Error generating trade network: {e}")
        
        # Fallback response
        basic_network = []
        for region in valid_regions:
            exports = []
            imports = []
            
            # Simply determine some basic exports/imports based on regional modifiers
            region_mods = self.regional_modifiers.get(region, {})
            for category, modifier in region_mods.items():
                if modifier < 1.0 and category in valid_categories:
                    exports.append(category)
                elif modifier > 1.0 and category in valid_categories:
                    imports.append(category)
            
            basic_network.append({
                "name": region,
                "exports": exports or ["various goods"],
                "imports": imports or ["various goods"],
                "advantages": ["Standard trade capabilities"],
                "key_relationships": [r for r in valid_regions if r != region]
            })
        
        return {
            "included_regions": valid_regions,
            "focus_categories": valid_categories,
            "trade_network": basic_network
        }
    
    def estimate_trade_investment(self, 
                               trade_good_ids: List[str],
                               budget_gp: float,
                               optimization_goal: str = "profit") -> Dict[str, Any]:
        """
        Estimate optimal investment distribution among trade goods.
        
        Args:
            trade_good_ids: List of trade good IDs to consider
            budget_gp: Available budget in gold pieces
            optimization_goal: Goal of optimization (profit, diversity, value)
            
        Returns:
            Dict[str, Any]: Investment recommendation
        """
        # Gather valid trade goods
        valid_goods = []
        for good_id in trade_good_ids:
            good_data = self._find_item_by_id(good_id)
            if good_data:
                valid_goods.append(good_data)
        
        if not valid_goods:
            return {"error": "No valid trade goods specified"}
        
        # Create context for the LLM prompt
        goods_context = []
        for good in valid_goods:
            base_value_gp = 0
            if "base_value" in good:
                base_value_gp = good["base_value"].get("gp", 0)
                base_value_gp += good["base_value"].get("sp", 0) / 10
                base_value_gp += good["base_value"].get("cp", 0) / 100
            elif "unit_value" in good:
                base_value_gp = good["unit_value"].get("gp", 0)
                base_value_gp += good["unit_value"].get("sp", 0) / 10
                base_value_gp += good["unit_value"].get("cp", 0) / 100
                
            goods_context.append({
                "name": good.get("name"),
                "id": good.get("id"),
                "category": good.get("trade_good_category").value if isinstance(good.get("trade_good_category"), TradeGoodCategory) else "unknown",
                "value_gp": base_value_gp,
                "properties": good.get("properties", [])
            })
        
        prompt = self.llm_advisor._create_prompt(
            "optimize trade investment",
            f"Available Goods: {json.dumps(goods_context)}\n"
            f"Budget: {budget_gp} gold pieces\n"
            f"Optimization Goal: {optimization_goal}\n\n"
            "Calculate an optimal investment distribution across these trade goods based on the given budget "
            f"and optimization goal ({optimization_goal}). Consider the characteristics of each good, "
            "including value, category, and properties. For each recommended purchase, specify quantity, "
            "cost, expected return, and rationale. "
            "Return as JSON with 'investment_strategy', 'recommended_purchases' as an array of objects, 'total_spent', "
            "'expected_returns', and 'risks_and_opportunities' keys."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            investment_plan = self.llm_advisor._extract_json(response)
            
            if investment_plan:
                investment_plan["available_budget_gp"] = budget_gp
                investment_plan["optimization_goal"] = optimization_goal
                return investment_plan
        except Exception as e:
            print(f"Error estimating trade investment: {e}")
        
        # Fallback response with simple distribution
        recommended_purchases = []
        remaining_budget = budget_gp
        
        # Simple even distribution among goods
        allocation_per_good = budget_gp / len(valid_goods)
        
        for good in valid_goods:
            base_value_gp = good.get("base_value", {}).get("gp", 1)
            quantity = int(allocation_per_good / base_value_gp)
            actual_cost = quantity * base_value_gp
            
            if quantity > 0 and actual_cost <= remaining_budget:
                recommended_purchases.append({
                    "trade_good": good.get("name"),
                    "quantity": quantity,
                    "cost": actual_cost,
                    "expected_return": actual_cost * 1.2,  # Assume 20% profit
                    "rationale": "Basic allocation strategy"
                })
                remaining_budget -= actual_cost
        
        return {
            "available_budget_gp": budget_gp,
            "optimization_goal": optimization_goal,
            "investment_strategy": "Basic even distribution",
            "recommended_purchases": recommended_purchases,
            "total_spent": budget_gp - remaining_budget,
            "expected_returns": sum(p["expected_return"] for p in recommended_purchases),
            "risks_and_opportunities": ["Standard market fluctuations apply"]
        }
    
    def generate_trade_good_appearance(self, good_id: str, quality: str = "standard") -> str:
        """
        Generate a detailed visual description of a trade good.
        
        Args:
            good_id: ID of the trade good
            quality: Quality level (poor, standard, superior, exceptional)
            
        Returns:
            str: Detailed appearance description
        """
        good_data = self._find_item_by_id(good_id)
        if not good_data:
            return "Trade good not found"
        
        context = f"Trade Good: {good_data.get('name')}\n"
        context += f"Type: {good_data.get('trade_good_category').value if isinstance(good_data.get('trade_good_category'), TradeGoodCategory) else 'unknown'}\n"
        context += f"Quality: {quality}\n"
        context += f"Properties: {', '.join(good_data.get('properties', []))}\n"
            
        prompt = self.llm_advisor._create_prompt(
            "describe the physical appearance of this trade good",
            context + "\n"
            "Create a vivid, detailed description of this trade good's physical appearance. "
            f"Include details about its color, texture, packaging, distinguishing features, and overall "
            f"quality level ({quality}). The description should help players visualize the goods "
            "they're trading and understand its value."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            
            # Clean up the response by removing any JSON formatting
            clean_response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
            clean_response = re.sub(r'\{.*?\}', '', clean_response, flags=re.DOTALL)
            
            return clean_response.strip()
        except Exception as e:
            print(f"Error generating trade good appearance: {e}")
            
        # Fallback description
        return f"A standard quality sample of {good_data.get('name')} suitable for trade."