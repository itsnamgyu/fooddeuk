# DT-STRIPE

Newer Stripe integration for the Django Template project, supporting token-based payments and subscriptions.

## Usage

- Copy Stripe API keys to `.env`.
- Enable webhooks to endpoint `<dt-stripe url base>/webhooks`, or `https://mysite.com/dt-stripe/webhooks` by default.
  - As of Oct 5th, 2019, we don't have any webhooks enabled.

### Template Tags (All-In-One)

Can use when there is only one Stripe Card Element on the page.

```html
{% load dt_stripe %}

<div class="form-row">
  <label for="card-element">
    Credit or debit card
  </label>
  <div id="card-element" class="mb-3 w-100"></div>
  <div id="card-errors" role="alert"></div>
</div>

{% dt_stripe 'form-id' 'card-element-id' 'card-errors-id' %}
```

### Template Tags (Standard)

Must use when there are more than one Stripe Card Elements on the page.

```
{% dt_stripe_init %}
{% dt_stripe_mount_card_element 'form-id' 'card-element-id' 'card-errors-id' %}
```

## Objects

### Products, Plans, SKUs

These can be created from dt_stripe. There is an option to fetch ALL objects from Stripe.

### Customers, Subscriptions, Orders

These will be created and stored in dt_stripe. Communication is mostly one-way (dt_stripe -> Stripe),
with the exception of Subscription cancellations.

Subscription cancellations will be handled via webhooks. Cancelled subscriptions are marked as
cancelled. To renew a subscription, the user must initialize a new subscription. When they do, the
old subscription is discarded from dt_stripe.
