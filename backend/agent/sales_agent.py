import logging

import requests

import backend.config as config
from backend.agent.intent_detector import has_booking_intent
from backend.agent.json_parser import extract_action_json
from backend.agent.product_matcher import find_product_in_message
from backend.agent.prompts import SALES_AGENT_PROMPT_TEMPLATE
from backend.tools.odoo_tools import (
    check_stock_and_prices,
    create_sales_quotation,
    search_or_create_customer,
)

logger = logging.getLogger(__name__)


def call_llm_provider(system_prompt: str, user_message: str, provider: str) -> str:
    """Route the request to the chosen LLM provider at runtime."""
    provider = provider.lower()
    logger.info("Calling LLM provider: %s", provider)

    if provider == "local":
        full_prompt = (
            f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
            f"<|im_start|>user\n{user_message}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        payload = {
            "model": config.LOCAL_MODEL_NAME,
            "prompt": full_prompt,
            "stream": False,
            "temperature": 0.1,
        }

        logger.debug("Sending request to Ollama at %s", config.LOCAL_LLM_URL)
        response = requests.post(config.LOCAL_LLM_URL, json=payload, timeout=30)
        response.raise_for_status()
        llm_text = response.json().get("response", "").strip()
        logger.info("Received Ollama response (%d chars)", len(llm_text))
        logger.debug("Raw Ollama response: %s", llm_text)
        return llm_text

    if provider == "groq":
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {config.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": config.GROQ_MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.1,
        }
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        llm_text = response.json()["choices"][0]["message"]["content"].strip()
        logger.info("Received Groq response (%d chars)", len(llm_text))
        return llm_text

    if provider == "gemini":
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{config.GEMINI_MODEL_NAME}:generateContent?key={config.GEMINI_API_KEY}"
        )
        headers = {"Content-Type": "application/json"}
        combined_prompt = f"System Instructions:\n{system_prompt}\n\nUser Message: {user_message}"
        payload = {
            "contents": [{"parts": [{"text": combined_prompt}]}],
            "generationConfig": {"temperature": 0.1},
        }
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        llm_text = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        logger.info("Received Gemini response (%d chars)", len(llm_text))
        return llm_text

    raise ValueError(f"Unknown MODEL_PROVIDER: {provider}")


def _build_inventory_context(phones_data: list[dict]) -> str:
    context = "الموبايلات المتاحة في المخزن حالياً:\n"
    for phone in phones_data:
        specs = phone.get("description_sale") or "لا توجد مواصفات"
        context += (
            f"- الموبايل: {phone['name']} | المعرف (ID): {phone['id']} | "
            f"السعر: {phone['list_price']} جنيه | المتاح: {int(phone['qty_available'])} أجهزة | "
            f"المواصفات: {specs}\n"
        )
    return context


def _handle_create_order(action_data: dict, customer_name: str, customer_phone: str) -> str:
    product_id = action_data.get("product_id")
    reply_text = action_data.get("reply") or "تمام يا فندم، هنحجزلك الموبايل."

    try:
        product_id = int(product_id)
    except (TypeError, ValueError):
        logger.error("Invalid product_id in action payload: %s", product_id)
        return "❌ عذراً، حدث خطأ في معرف المنتج. الرجاء المحاولة مرة أخرى."

    logger.info(
        "Creating order for customer=%s phone=%s product_id=%s",
        customer_name,
        customer_phone,
        product_id,
    )
    customer_id = search_or_create_customer(customer_name, customer_phone)
    logger.info("Resolved customer_id=%s", customer_id)

    order_name = create_sales_quotation(customer_id, product_id, qty=1)
    logger.info("Created quotation: %s", order_name)

    if isinstance(order_name, str) and order_name.startswith("Error creating quotation"):
        logger.error("Odoo quotation creation failed: %s", order_name)
        return f"❌ {order_name}"

    return f"{reply_text} (تم تسجيل طلبك في أودو برقم: {order_name} 📝)"


def run_sales_agent(user_message: str, customer_name: str, customer_phone: str, provider: str) -> str:
    logger.info(
        "Running sales agent for customer=%s phone=%s message=%s",
        customer_name,
        customer_phone,
        user_message,
    )

    try:
        phones_data = check_stock_and_prices()
        logger.info("Loaded %d products from Odoo inventory", len(phones_data))
    except Exception as exc:
        logger.exception("Failed to load inventory from Odoo")
        return f"Error connecting to Odoo inventory: {exc}"

    context = _build_inventory_context(phones_data)

    try:
        system_prompt = SALES_AGENT_PROMPT_TEMPLATE.format(context=context)
    except KeyError as exc:
        logger.exception("Prompt template formatting failed")
        return f"Error preparing agent prompt: {exc}"

    try:
        ai_reply = call_llm_provider(system_prompt, user_message, provider)
        logger.debug("Raw AI reply: %s", ai_reply)
    except Exception as exc:
        logger.exception("LLM provider call failed")
        return f"Error connecting to LLM Agent: {exc}"

    action_data = extract_action_json(ai_reply)
    if action_data and action_data.get("action") == "create_order":
        return _handle_create_order(action_data, customer_name, customer_phone)

    if has_booking_intent(user_message):
        matched_product = find_product_in_message(user_message, phones_data)
        if matched_product:
            logger.info(
                "Using booking fallback for product=%s id=%s",
                matched_product["name"],
                matched_product["id"],
            )
            fallback_action = {
                "action": "create_order",
                "product_id": matched_product["id"],
                "reply": f"تمام يا فندم، هنحجزلك {matched_product['name']}.",
            }
            return _handle_create_order(fallback_action, customer_name, customer_phone)

    logger.info("Returning conversational LLM reply without Odoo action")
    return ai_reply
