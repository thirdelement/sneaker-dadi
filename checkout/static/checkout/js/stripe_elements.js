/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment
    CSS from here: 
    https://stripe.com/docs/stripe-js
*/
//Get the stripe public key and client secret.  Slice off first and last character as don't need quote marks.
var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);
//Set up stripe by creating variable using stripe public key.  Made possible by stripe js in base template.
var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();

var style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};

var card = elements.create('card', {
    style: style
});
card.mount('#card-element');

// Handle realtime validation errors on the card element
card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors');
    if (event.error) {
        var html = `
            <span role="alert">
            <i class="bi bi-x-circle"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        errorDiv.textContent = '';
    }
});

// Handle form submit
var form = document.getElementById('payment-form');

form.addEventListener('submit', function(ev) {
    //prevent the default action which is POST
    ev.preventDefault();
    //disable cart element & submit button to prevent multiple submissions
    card.update({ 'disabled': true});
    $('#submit-button').attr('disabled', true);
    //trigger overlay and fade out form 
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);
    //confirm card payment method, provide card to stripe & execute function on result
    stripe.confirmCardPayment(clientSecret, {
        payment_method: {
            card: card,
        }
    }).then(function(result) {
        //if there's an error put this into the card error div
        if (result.error) {
            var errorDiv = document.getElementById('card-errors');
            var html = `
                <span role="alert">
                <i class="bi bi-x"></i>
                </span>
                <span>${result.error.message}</span>`;
                //if error re-enable the card element and submit button to allow
                //the user to fix it
            $(errorDiv).html(html);
            //trigger overlay and fade out form 
            $('#payment-form').fadeToggle(100);
            $('#loading-overlay').fadeToggle(100);
            card.update({ 'disabled': false});
            $('#submit-button').attr('disabled', false);
            //else if status of the payment intent is succeeded submit the form
        } else {
            if (result.paymentIntent.status === 'succeeded') {
                form.submit();
            }
        }
    });
});