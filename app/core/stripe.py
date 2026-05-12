import stripe
from app.core.vars import STRIPE_KEY

client = stripe.StripeClient(STRIPE_KEY)
