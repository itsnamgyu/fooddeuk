// Create a Stripe client.
var stripe = Stripe("{{ stripe_public_key }}");

// Create an instance of Elements.
var elements = stripe.elements();

// Custom styling can be passed to options when creating an Element.
// (Note that this demo uses a wider set of styles than the guide below.)
var style = {
  base: {
    color: "#32325d",
    fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
    fontSmoothing: "antialiased",
    fontSize: "16px",
    "::placeholder": {
      color: "#aab7c4"
    }
  },
  invalid: {
    color: "#fa755a",
    iconColor: "#fa755a"
  }
};

function mountCardElement(formId, cardElementId, cardErrorsId) {
  const form = document.getElementById(formId);
  const cardElement = document.getElementById(cardElementId);
  const cardErrors = document.getElementById(cardErrorsId);

  // Create an instance of the card Element.
  var card = elements.create("card", { style: style });

  // Add an instance of the card Element into the `card-element` <div>.
  card.mount("#" + cardElementId);

  // Handle real-time validation errors from the card Element.
  card.addEventListener("change", function(event) {
    if (event.error) {
      cardErrors.textContent = event.error.message;
    } else {
      cardErrors.textContent = "";
    }
  });

  // Handle form submission.
  form.addEventListener("submit", function(event) {
    event.preventDefault();

    stripe.createToken(card).then(function(result) {
      if (result.error) {
        // Inform the user if there was an error.
        cardElement.textContent = result.error.message;
      } else {
        // Send the token to your server.
        const token = result.token;

        // Submit the form with the token ID.
        var hiddenInput = document.createElement("input");
        hiddenInput.setAttribute("type", "hidden");
        hiddenInput.setAttribute("name", "token");
        hiddenInput.setAttribute("value", token.id);
        form.appendChild(hiddenInput);
        form.submit();
      }
    });
  });
}
