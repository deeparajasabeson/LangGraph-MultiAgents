from langchain_core.tools import tool

@tool
def lookup_faq(topic: str) -> str:
    """
    Lookup frequently asked questions about warranty, returns, and shipping.
    """

    # Placeholder implementation, replace with actual FAQ lookup logic
    faq_db = {
        "warranty": "Our products come with a one-year warranty covering manufacturing defects.",
        "returns": "You can return any products within 30 days of purchase along with receipt.",
        "shipping": "Shipping usually takes 5-7 business days.  Express delivery is 1-2 days."
    }
    return faq_db.get(
        topic.lower(),
        f"No information found for topic: {topic}.  Valid topics: " + ", ".join(faq_db.keys())
    )


@tool
def check_order_status(order_id:str) -> str:
    """
    Check the status of a customer order.
    """
    orders_db = {
        "12345": "Shipped, expected delivery in 2 days.",
        "67890": "Processing, estimated ship date tomorrow."
    }
    return orders_db.get(
        order_id,
        f"No information found for order ID: {order_id}.  Valid order IDs: " + ", ".join(orders_db.keys())
    )


@tool
def get_current_promotions(category:str = "all") -> str:
    """
    Get information about current sales and promotions.
    """
    promotions_db = {
        "all": "10% off on all products this week!",
        "electronics": "15% off on all electronics this week!",
        "clothing": "Buy 2 get 1 free on all clothing items.",
        "home": "20% off on all home appliances this week!",
    }
    return promotions_db.get(
        category.lower(),
        f"No promotions found for category: {category}.  Valid categories: " + ", ".join(promotions_db.keys())
    )

FAQ_TOOL = lookup_faq
ORDER_STATUS_TOOL = check_order_status
PROMOTIONS_TOOL = get_current_promotions
