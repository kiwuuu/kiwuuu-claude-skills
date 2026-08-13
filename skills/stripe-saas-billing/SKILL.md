---
name: stripe-saas-billing
description: Stripe subscription billing for SaaS. USE WHEN implementing Stripe subscriptions, handling webhook events, managing proration, building dunning logic, or debugging billing issues. Covers subscription lifecycle, invoice handling, trial periods, upgrade/downgrade, failed payment recovery, and Stripe Python SDK patterns.
---

# Stripe SaaS Billing Skill

Complete Stripe subscription billing reference for SaaS. All patterns assume Python + Flask (Kiwuuu's stack).

## Environment Variables (Kiwuuu — Agency Tier pricing, 2026-07)
```bash
STRIPE_SECRET_KEY=sk_live_...          # Server-side only, never expose
STRIPE_PRICE_AGENCY_BASE=price_...     # $499/mo recurring price ID (Agency Tier base)
STRIPE_PRICE_WORKSPACE=price_...       # $19/mo per-workspace price ID (quantity-based)
STRIPE_WEBHOOK_SECRET=whsec_...        # From Stripe Dashboard → Webhooks
# Legacy self-serve tiers ($49 Pro / $99 Business) are retired — see vault kiwuuu-pricing
```

**Agency Tier checkout:** one subscription with two line items — the base price (quantity 1) and the workspace price with `quantity=<workspace count>`. Adjust workspaces later via `stripe.Subscription.modify` on that item's quantity; Stripe prorates automatically.

---

## Subscription Lifecycle

```
User clicks Upgrade
    ↓
Create Stripe Customer (or reuse existing)
    ↓
Create Checkout Session (hosted page)
    ↓
User enters card → Stripe processes
    ↓
Webhook: checkout.session.completed → set plan = 'pro'/'business'
    ↓
Webhook: invoice.payment_succeeded (monthly) → plan stays active
    ↓
Webhook: invoice.payment_failed → send WA alert, retry 3x
    ↓
Webhook: customer.subscription.deleted → set plan = 'free'
```

---

## Checkout Session (Kiwuuu pattern)
```python
import stripe
stripe.api_key = STRIPE_SECRET_KEY

def create_checkout_session(user_id: str, email: str, price_id: str) -> str:
    """Returns checkout URL. Creates/reuses Stripe customer."""
    # Get or create customer
    profile = get_sb().table('profiles').select('stripe_customer_id').eq('id', user_id).single().execute().data
    customer_id = profile.get('stripe_customer_id') if profile else None
    
    if not customer_id:
        customer = stripe.Customer.create(email=email, metadata={'user_id': user_id})
        customer_id = customer.id
        get_sb().table('profiles').update({'stripe_customer_id': customer_id}).eq('id', user_id).execute()
    
    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode='subscription',
        payment_method_types=['card'],
        line_items=[{'price': price_id, 'quantity': 1}],
        success_url=f'{BASE_URL}/dashboard?upgrade=success',
        cancel_url=f'{BASE_URL}/dashboard',
        metadata={'user_id': user_id}
    )
    return session.url
```

---

## Webhook Handler (Complete)
```python
@app.route('/api/stripe/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data()
    sig = request.headers.get('Stripe-Signature', '')
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        return jsonify({'error': 'Invalid signature'}), 400
    
    etype = event['type']
    obj   = event['data']['object']
    
    if etype == 'checkout.session.completed':
        _handle_checkout_complete(obj)
    elif etype == 'invoice.payment_succeeded':
        _handle_payment_success(obj)
    elif etype == 'invoice.payment_failed':
        _handle_payment_failed(obj)
    elif etype == 'customer.subscription.updated':
        _handle_subscription_updated(obj)
    elif etype == 'customer.subscription.deleted':
        _handle_subscription_deleted(obj)
    
    return jsonify({'received': True})
```

---

## Critical Webhook Handlers

### checkout.session.completed
```python
def _handle_checkout_complete(session):
    user_id = session['metadata'].get('user_id')
    plan = _plan_from_price(session.get('amount_total', 0))
    get_sb().table('profiles').update({'plan': plan}).eq('id', user_id).execute()
    # Send WA congrats, admin notify
```

### invoice.payment_failed (Dunning)
```python
def _handle_payment_failed(invoice):
    customer_id = invoice['customer']
    attempt_count = invoice.get('attempt_count', 1)
    # Retry schedule: Stripe auto-retries at 1, 3, 5, 7 days
    # After 4 failures: subscription cancels → triggers subscription.deleted
    if attempt_count == 1:
        # First failure: gentle WA message
        _wa_billing_failed(phone, 'stripe')
    elif attempt_count >= 3:
        # 3rd failure: urgent WA + admin alert
        _wa_notify_admin_billing('payment_failed_critical', email)
```

### customer.subscription.deleted
```python
def _handle_subscription_deleted(subscription):
    customer_id = subscription['customer']
    # Set plan to 'free' (was paying, now canceled)
    # 'free' ≠ 'trial' — different gating behavior
    rows = get_sb().table('profiles').select('id,email').eq('stripe_customer_id', customer_id).execute().data
    if rows:
        get_sb().table('profiles').update({'plan': 'free'}).eq('id', rows[0]['id']).execute()
```

---

## Plan ↔ Price Mapping
```python
STRIPE_PRICE_TO_PLAN = {
    STRIPE_PRICE_PRO: 'pro',
    STRIPE_PRICE_BUSINESS: 'business',
}

def _plan_from_price(price_id: str) -> str:
    return STRIPE_PRICE_TO_PLAN.get(price_id, 'pro')
```

---

## Proration (Upgrade/Downgrade)

### Upgrade (Pro → Business)
```python
subscription = stripe.Subscription.retrieve(sub_id)
stripe.Subscription.modify(
    sub_id,
    items=[{
        'id': subscription['items']['data'][0]['id'],
        'price': STRIPE_PRICE_BUSINESS,
    }],
    proration_behavior='always_invoice',  # Charge diff immediately
)
```

### Downgrade (Business → Pro)
```python
stripe.Subscription.modify(
    sub_id,
    items=[{'id': item_id, 'price': STRIPE_PRICE_PRO}],
    proration_behavior='none',  # Credit on next invoice, not immediate refund
)
```

---

## Dunning (Failed Payment Recovery)

### Stripe Smart Retries (Auto)
Enable in Dashboard → Billing → Subscriptions → Smart Retries
Stripe uses ML to retry at optimal times. Recovers ~30% of failed payments.

### Manual Dunning Emails/WA (Layer on top)
```
Day 0: First failure → "Your payment didn't go through. Update card:"
Day 3: Second attempt → WA message: "We tried again — still needs updating"
Day 5: Third attempt → Email + WA: "Action required to keep access"
Day 7: Final attempt → "Access paused — update card to reactivate"
Day 8: subscription.deleted fires → plan = 'free'
```

---

## Customer Portal (Self-Service)
```python
@app.route('/api/billing/portal', methods=['POST'])
@require_auth
def billing_portal():
    profile = _get_profile()
    customer_id = profile.get('stripe_customer_id')
    if not customer_id:
        return jsonify({'error': 'No billing account'}), 400
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=f'{BASE_URL}/dashboard',
    )
    return jsonify({'url': session.url})
```

---

## Testing Checklist
- [ ] Test card: 4242 4242 4242 4242 (success)
- [ ] Declined card: 4000 0000 0000 0002
- [ ] Insufficient funds: 4000 0000 0000 9995
- [ ] 3DS required: 4000 0027 6000 3184
- [ ] Webhook tested with `stripe listen --forward-to localhost:4000/api/stripe/webhook`
- [ ] Verify plan updates in Supabase after checkout
- [ ] Verify WA notification fires on upgrade
- [ ] Verify plan = 'free' on cancel
