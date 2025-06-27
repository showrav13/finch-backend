from setting.models import CompanySetting

def currency_context(request):
    try:
        company_setting = CompanySetting.objects.first()
        if company_setting is None:
            raise ValueError("No company settings found.")
        
        currency_code = company_setting.currency_code        
        currency_symbol = company_setting.currency_symbol

    except Exception as e:
        print(f"Error retrieving currency context: {e}")
        currency_code = None
        currency_symbol = None

    return {
        'currency_code': currency_code,
        'currency_symbol': currency_symbol,
    }
