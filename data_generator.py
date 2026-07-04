import json
import random
import argparse
from datetime import datetime, timedelta

def generate_ecosystem_payload(persona):
    current_date = datetime.now()
    
    # Configure baseline health characteristics based on persona
    if persona == "prime":
        company, industry, multiplier = "Vanguard Engineering", "Precision Manufacturing", 1.0
        gst_delays, upi_bounces, power_trend, epfo_trend = [0, 0, 0], 2, [5000, 5200, 5500], [45, 46, 47]
    elif persona == "volatile":
        company, industry, multiplier = "Balaji Logistics", "Spices Trading", 0.8
        gst_delays, upi_bounces, power_trend, epfo_trend = [5, 12, 0], 8, [4000, 2200, 4800], [22, 22, 21]
    else: # stressed
        company, industry, multiplier = "Royal Weaving Unit", "Textile Mill", 0.5
        gst_delays, upi_bounces, power_trend, epfo_trend = [18, 25, 30], 27, [3500, 1800, 400], [18, 14, 10]

    # 1. GSTN API Payload Simulation (GSTR-1 Business Sales)
    gstn_payload = {
        "provider": "GSTN_API_GATEWAY",
        "status": "SUCCESS",
        "data": {
            "gstin": "29AAAAX1234X1Z",
            "filing_history": [
                {"period": "2026-05", "gross_turnover": round(1200000 * multiplier, 2), "filing_delay_days": gst_delays[0]},
                {"period": "2026-04", "gross_turnover": round(1150000 * multiplier, 2), "filing_delay_days": gst_delays[1]},
                {"period": "2026-03", "gross_turnover": round(1300000 * multiplier, 2), "filing_delay_days": gst_delays[2]}
            ]
        }
    }

    # 2. Account Aggregator (AA) Banking/UPI Payload Simulation
    aa_payload = {
        "provider": "ACCOUNT_AGGREGATOR_NETWORK",
        "consent_id": "aa-consent-uuid-998877",
        "data": {
            "account_summary": {
                "account_type": "CURRENT",
                "three_month_inflow": round(3650000 * multiplier, 2),
                "average_monthly_balance": round(150000 * multiplier, 2)
            },
            "upi_merchant_analytics": {
                "total_transaction_count": random.randint(1500, 3000),
                "failed_or_reversed_technical_bounces": upi_bounces,
                "daily_cash_flow_variance_percentage": 12 if persona == "prime" else (42 if persona == "volatile" else 85)
            }
        }
    }

    # 3. EPFO Portal Payroll Payload Simulation
    epfo_payload = {
        "provider": "EPFO_UAN_GATEWAY",
        "status": "AUTHENTICATED",
        "data": {
            "establishment_id": "BG/BAN/0012345/000",
            "historical_contributions": [
                {"wage_month": "2026-05", "member_count": epfo_trend[0], "amount_deposited": epfo_trend[0] * 1800},
                {"wage_month": "2026-04", "member_count": epfo_trend[1], "amount_deposited": epfo_trend[1] * 1800},
                {"wage_month": "2026-03", "member_count": epfo_trend[2], "amount_deposited": epfo_trend[2] * 1800}
            ]
        }
    }

    # 4. DISCOM Utility Payload Simulation (e.g., BESCOM Electricity Telemetry)
    discom_payload = {
        "provider": "DISCOM_UTILITY_BHARAT_BILLPAY",
        "data": {
            "consumer_number": "1029384756",
            "utility_provider": "BESCOM_BANGALORE",
            "billing_history": [
                {"bill_period": "2026-05", "consumption_kwh": power_trend[0], "payment_status": "PAID"},
                {"bill_period": "2026-04", "consumption_kwh": power_trend[1], "payment_status": "PAID"},
                {"bill_period": "2026-03", "consumption_kwh": power_trend[2], "payment_status": "PAID" if persona != "stressed" else "OVERDUE"}
            ]
        }
    }

    # Combine into unified master ingestion payload
    return {
        "application_metadata": {
            "company_name": company,
            "industry_type": industry,
            "evaluation_timestamp": current_date.isoformat(),
            "target_persona_test": persona
        },
        "ecosystem_inputs": {
            "gstn": gstn_payload,
            "account_aggregator": aa_payload,
            "epfo": epfo_payload,
            "discom": discom_payload
        }
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--persona", choices=["prime", "volatile", "stressed"], required=True)
    args = parser.parse_args()
    
    output = generate_ecosystem_payload(args.persona)
    with open(f"mock_msme_{args.persona}.json", "w") as f:
        json.dump(output, f, indent=4)
    print(f"✓ Created ecosystem payload for: {output['application_metadata']['company_name']}")