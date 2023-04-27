import stripe
import json
from django.shortcuts import render
from django.conf import settings
from .models import Produto, Pedido
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt


stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    produto = Produto.objects.get(id = 1)
    context = {
        'produto': produto,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'home.html', context=context)

@csrf_exempt
def create_payment(request, id):
    produto = Produto.objects.get(id=id)
    email = json.loads(request.body)['email']

    intent = stripe.PaymentIntent.create(
        amount=int(produto.preco),
        currency='BRL',
        metadata={
            'produto_id': produto.id,
            'email': email
        }
    )
    return JsonResponse({
        'clientSecret': intent['client_secret']
    })

def success(request):
    return HttpResponse('Success')

def error(request):
    return HttpResponse('Error')

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header, 
            endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event['type'] == 'charge.succeeded':
        session = event['data']['object']
        x = Pedido(
            produto_id=session['metadata']['produto_id'],
            email=session['metadata']['email'],
            valor_pago=session['amount'],
            payment_intent=session['payment_intent'],
            status=session['status']
        )
        x.save()

    return HttpResponse(status=200)




# Redirecinar para efetuar pagamento no site da stripe
# def create_checkout_session(request, id):
#     produto = Produto.objects.get(id = id)
#     YOUR_DOMAIN = "http://127.0.0.1:8000"
#     checkout_session = stripe.checkout.Session.create(
#         # Itens que o Cliente comprou
#         line_items=[
#             {
#                 'price_data': {
#                     'currency': 'BRL',
#                     'unit_amount': int(produto.preco),
#                     'product_data': {
#                             'name': produto.nome
#                         }

#                 },
#                 'quantity': 1,
#             },
#         ],
#         payment_method_types=[
#             'card',
#             'boleto',
#         ],
#         metadata={
#             'id_produto': produto.id,
#             'nome': 'Pedro Lucas',
#             'endereco': 'Av. Python',
#         },
#         mode='payment',
#         success_url=YOUR_DOMAIN + '/success',
#         cancel_url=YOUR_DOMAIN + '/error',
#     )
#     return JsonResponse({'id': checkout_session.id})
