from fastapi import FastAPI, HTTPException

app = FastAPI(title="Syralaa Layer 1 Network & Anonymous AI Trading")

wallets = {}
order_book = [{"price": 0.10, "amount": 1000}, {"price": 1.00, "amount": 500}]

# إعدادات عملة Syralaa والتحكم بالقيمة والإنتاج الكمي الثابت للسعر
token_state = {
    "name": "Syralaa",
    "symbol": "SRL",
    "total_supply": 1000000.0,
    "current_price": 0.50,  # السعر الحالي القابل للتحكم
    "price_floor": 0.50     # الحد الأدنى الثابت للسعر (لا ينخفض مهما زاد الإنتاج)
}

# 1. لوحة معلومات الشبكة والعملة
@app.get("/")
def home():
    return {
        "message": "Welcome to Syralaa Network (Layer 1)",
        "coin": token_state["symbol"],
        "price": token_state["current_price"],
        "status": "Online & Secure"
    }

@app.get("/network/token-info")
def token_info():
    return {
        "network_name": "Syralaa Layer 1",
        "coin_name": token_state["name"],
        "coin_symbol": token_state["symbol"],
        "total_supply": token_state["total_supply"],
        "current_price_usdt": token_state["current_price"],
        "price_protection": "Secured against price drop (Constant Floor)",
        "privacy": "100% No-KYC Anonymous"
    }

# 2. لوحة التحكم الإدارية لتغيير السعر بدون فتح الكود
@app.post("/admin/set-price")
def set_token_price(data: dict):
    new_price = float(data.get("new_price", 0))
    if new_price < token_state["price_floor"]:
        raise HTTPException(
            status_code=400, 
            detail=f"عذراً، لا يمكن خفض سعر العملة عن الحد الأدنى الثابت وهو {token_state['price_floor']} USDT حمايةً لقيمة الشبكة!"
        )
    
    token_state["current_price"] = new_price
    token_state["price_floor"] = new_price 
    
    return {
        "status": "success",
        "message": "تم تحديث سعر عملة Syralaa بنجاح وثبات تام!",
        "new_price": token_state["current_price"]
    }

# 3. زر الإنتاج الكمي (Minting) لزيادة إجمالي الكمية مع ثبات السعر
@app.post("/admin/mint")
def mint_tokens(data: dict):
    mint_amount = float(data.get("amount", 0))
    if mint_amount <= 0:
        raise HTTPException(status_code=400, detail="كمية الإنتاج يجب أن تكون أكبر من الصفر")
    
    token_state["total_supply"] += mint_amount
    
    return {
        "status": "success",
        "message": f"تم إنتاج كمية جديدة بقيمة {mint_amount} من عملة Syralaa بنجاح!",
        "new_total_supply": token_state["total_supply"],
        "current_price_guaranteed": token_state["current_price"]
    }

# 4. إنشاء محفظة فورية مع منح 100 USDT بونص للتداول حصراً
@app.post("/wallet/create")
def create_wallet(data: dict):
    address = data.get("address")
    if not address:
        raise HTTPException(status_code=400, detail="عنوان المحفظة مطلوب")
        
    if address in wallets:
        return {"message": "المحفظة موجودة مسبقاً", "wallet": wallets[address]}
    
    wallets[address] = {
        "bonus_usdt": 100.0,       # بونص تجريبي للتداول (غير قابل للسحب كأصل)
        "withdrawable_usdt": 0.0,  # الأرباح القابلة للسحب الفوري
        "SYRALAA_COIN": 0.0,       # رصيد عملة Syralaa بعد الشراء
        "ai_bot_active": False
    }
    return {
        "message": "تم إنشاء محفظتك على شبكة Syralaa بنجاح وحصلت على 100 USDT للتداول!",
        "address": address,
        "wallet": wallets[address]
    }

# 5. إيداع الأموال (مع دعم شبكة BEP20)
@app.post("/wallet/deposit")
def deposit(data: dict):
    address = data.get("address")
    amount = float(data.get("amount", 0))
    network = data.get("network", "BEP20")  # دعم شبكة BEP20 افتراضياً
    tx_hash = data.get("tx_hash", "SIMULATED_TX")
    
    if address not in wallets:
        raise HTTPException(status_code=404, detail="المحفظة غير موجودة")
        
    if network.upper() not in ["BEP20", "TRC20", "ERC20"]:
        raise HTTPException(status_code=400, detail="الشبكة غير مدعومة، يرجى استخدام شبكة BEP20")

    wallets[address]["withdrawable_usdt"] += amount
    return {
        "status": "success",
        "message": f"تم إيداع مبلغ {amount} USDT بنجاح عبر شبكة {network.upper()}",
        "tx_hash": tx_hash,
        "wallet": wallets[address]
    }

# 6. سحب الأرباح فقط بعد بيع العملات (مع دعم شبكة BEP20)
@app.post("/wallet/withdraw")
def withdraw(data: dict):
    address = data.get("address")
    amount = float(data.get("amount", 0))
    network = data.get("network", "BEP20")
    to_external_wallet = data.get("to_wallet") # عنوان محفظة العميل الخارجية (مثل Trust Wallet أو Binance)
    
    if not to_external_wallet:
        raise HTTPException(status_code=400, detail="يجب تحديد عنوان محفظة الاستلام الخارجية (BEP20)")

    if address not in wallets:
        raise HTTPException(status_code=404, detail="المحفظة غير موجودة")
        
    user_wallet = wallets[address]
    
    if amount <= 0 or amount > user_wallet["withdrawable_usdt"]:
        raise HTTPException(
            status_code=400, 
            detail="عذراً، بونص الـ 100 الأساسي غير قابل للسحب. يمكنك فقط سحب أرباح التداول والبيع!"
        )
    
    user_wallet["withdrawable_usdt"] -= amount
    return {
        "status": "success",
        "message": f"تم إرسال الأرباح بنجاح عبر شبكة {network.upper()} إلى المحفظة الخارجية: {to_external_wallet}",
        "withdrawn_amount": amount,
        "remaining_withdrawable": user_wallet["withdrawable_usdt"]
    }

# 7. تداول وعمل بوت الـ AI بعملة Syralaa
@app.post("/ai/deploy-bot")
def deploy_ai_bot(data: dict):
    address = data.get("address")
    strategy = data.get("strategy", "safe")
    
    if address not in wallets:
        raise HTTPException(status_code=404, detail="المحفظة غير موجودة")
    
    user_wallet = wallets[address]
    total_available_usdt = user_wallet["bonus_usdt"] + user_wallet["withdrawable_usdt"]
    
    if total_available_usdt <= 0:
        raise HTTPException(status_code=400, detail="الرصيد غير كافٍ لتشغيل البوت!")

    user_wallet["ai_bot_active"] = True
    
    spent_usdt = user_wallet["bonus_usdt"] * 0.5
    purchased_coins = spent_usdt / token_state["current_price"]

    user_wallet["bonus_usdt"] -= spent_usdt
    user_wallet["SYRALAA_COIN"] += purchased_coins
    
    # محاكاة ربح تجريبي يضاف لرصيد الأرباح القابلة للسحب بعد البيع
    simulated_profit = 5.0 
    user_wallet["withdrawable_usdt"] += simulated_profit

    return {
        "status": "نجاح تشغيل بوت الـ AI وشراء عملة Syralaa!",
        "actions_taken": f"تم شراء {purchased_coins} من عملة Syralaa، وإضافة أرباح بيع بقيمة {simulated_profit} USDT لرصيدك القابل للسحب عبر BEP20.",
        "updated_wallet": user_wallet
    }
